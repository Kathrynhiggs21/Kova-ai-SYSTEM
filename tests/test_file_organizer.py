import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "file_organizer.py"
SPEC = importlib.util.spec_from_file_location("file_organizer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FileOrganizerTests(unittest.TestCase):
    def test_explicit_area_is_case_insensitive_and_canonical(self):
        self.assertEqual(MODULE.area_for({"area": "KOVA", "name": "Notes.txt"}), "KOVA")
        self.assertEqual(MODULE.area_for({"area": "reagan", "name": "Notes.txt"}), "Reagan")

    def test_short_title_normalizes_kova_and_removes_copy_noise(self):
        item = {"name": "K9va_OS_Automation_Plan_FINAL (2).docx"}
        self.assertEqual(MODULE.short_title(item), "KOVA Operating System Automation Plan")

    def test_short_title_keeps_meaningful_trailing_year(self):
        self.assertEqual(MODULE.short_title({"name": "KOVA Roadmap 2026.docx"}), "KOVA Roadmap 2026")
        self.assertEqual(MODULE.short_title({"name": "KOVA Roadmap v2.docx"}), "KOVA Roadmap")

    def test_final_requires_verification_and_legacy_status_maps_to_review(self):
        self.assertEqual(MODULE.lifecycle_for({"name": "KOVA Final Guide.docx"})[0], "REVIEW")
        self.assertEqual(
            MODULE.lifecycle_for({"name": "KOVA Final Guide.docx", "verified": True})[0],
            "FINAL",
        )
        self.assertEqual(MODULE.lifecycle_for({"status": "UNREVIEWED"})[0], "REVIEW")

    def test_boundary_matching_does_not_call_capital_an_api_topic(self):
        self.assertEqual(MODULE.topic_for({"name": "KOVA Capital Budget.txt"}), "KOVA Reference")
        self.assertEqual(MODULE.topic_for({"name": "KOVA API Plan.txt"}), "KOVA Connectors")

    def test_separator_sensitive_and_uninspected_state(self):
        self.assertEqual(MODULE.sensitivity_for({"name": "private-config-url.txt"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "ordinary-notes.txt"})[0], "UNKNOWN")
        self.assertEqual(
            MODULE.sensitivity_for({"name": "ordinary-notes.txt", "content_inspected": True})[0],
            "CLEAR",
        )

    def test_exact_duplicate_requires_hash_and_is_deterministic(self):
        items = [
            {"id": "older", "name": "KOVA Plan.docx", "md5Checksum": "same", "modified": "2026-01-01T00:00:00Z"},
            {"id": "newer", "name": "KOVA Plan.docx", "md5Checksum": "same", "modified": "2026-02-01T00:00:00Z"},
        ]
        rows = MODULE.build_registry(items)
        self.assertIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])
        self.assertEqual(rows[0]["canonical_version_key"], rows[1]["version_key"])

        reversed_rows = MODULE.build_registry(list(reversed(items)))
        canonical_ids = [row["source_id"] for row in reversed_rows if "DUPLICATE" not in row["flags"]]
        self.assertEqual(canonical_ids, ["newer"])

    def test_exact_duplicate_uses_blob_sha_evidence(self):
        rows = MODULE.build_registry([
            {"id": "older", "name": "KOVA Plan.docx", "blob_sha": "same", "modified": "2026-01-01T00:00:00Z"},
            {"id": "newer", "name": "KOVA Plan.docx", "blob_sha": "same", "modified": "2026-02-01T00:00:00Z"},
        ])
        self.assertIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])

    def test_same_title_without_hash_is_only_a_review_candidate(self):
        rows = MODULE.build_registry([
            {"id": "1", "name": "KOVA Plan.docx", "size": 9, "modified": "2026-01-01T00:00:00Z"},
            {"id": "2", "name": "KOVA Plan.docx", "size": 9, "modified": "2026-02-01T00:00:00Z"},
        ])
        self.assertNotIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])
        candidates = [row for row in rows if row["possible_duplicate_of"] is not None]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["lifecycle"], "REVIEW")

    def test_mixed_hash_likely_group_is_marked_for_review(self):
        rows = MODULE.build_registry([
            {"id": "hashless-newer", "name": "KOVA Plan.docx", "size": 9, "modified": "2026-02-01T00:00:00Z"},
            {"id": "hashed-older", "name": "KOVA Plan.docx", "size": 9, "md5Checksum": "abc", "modified": "2026-01-01T00:00:00Z"},
        ])
        candidates = [row for row in rows if row["possible_duplicate_of"] is not None]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["source_id"], "hashed-older")
        self.assertEqual(candidates[0]["lifecycle"], "REVIEW")

    def test_version_identity_includes_source(self):
        a = MODULE.version_key({"id": "a", "md5Checksum": "same"})
        b = MODULE.version_key({"id": "b", "md5Checksum": "same"})
        self.assertNotEqual(a, b)

    def test_local_version_identity_uses_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            item = Path(temp_dir) / "KOVA Notes.txt"
            item.write_text("first", encoding="utf-8")
            first_input = {"source": "local", "path": str(item)}
            first = MODULE.version_key(first_input)
            item.write_text("second", encoding="utf-8")
            second_input = {"source": "local", "path": str(item)}
            second = MODULE.version_key(second_input)
            self.assertNotEqual(first, second)
            self.assertEqual(first_input["revision_id"], first_input["sha256"])
            self.assertEqual(second_input["revision_id"], second_input["sha256"])

    def test_local_source_identity_is_preserved_in_registry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            item = Path(temp_dir) / "Notes.txt"
            item.write_text("notes", encoding="utf-8")
            row = MODULE.build_registry([{"source": "local", "path": str(item), "name": item.name}])[0]
            self.assertEqual(row["source_id"], str(item))

    def test_registry_rows_include_version_evidence(self):
        row = MODULE.build_registry([{
            "id": "1",
            "name": "KOVA Plan.docx",
            "source": "google_drive",
            "md5Checksum": "abc123",
            "headRevisionId": "rev-1",
            "version": "7",
        }])[0]
        self.assertEqual(row["version_evidence"]["source"], "google_drive")
        self.assertEqual(row["version_evidence"]["headRevisionId"], "rev-1")
        self.assertEqual(row["version_evidence"]["md5Checksum"], "abc123")

    def test_chat_record_role_does_not_infer_a_decision(self):
        self.assertEqual(MODULE.record_role_for({"name": "KOVA ideas chat"}), "Unknown")
        self.assertEqual(MODULE.record_role_for({"record_role": "decision"}), "Decision")

    def test_history_and_verified_decision_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "private" / "registry.json"
            old = MODULE.build_registry([{
                "id": "1", "name": "KOVA Guide.docx", "modified": "2026-01-01T00:00:00Z",
                "lifecycle": "FINAL", "verified": True, "verification_evidence": "Owner approved"
            }])
            MODULE.write_registry(old, output)
            MODULE.write_registry(MODULE.build_registry([]), output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["items"]), 1)
            self.assertFalse(payload["items"][0]["observed_current"])
            self.assertEqual(payload["items"][0]["verification"]["evidence"], "Owner approved")
            self.assertEqual(payload["exceptions"]["generated_at"], payload["generated_at"])
            self.assertEqual(payload["exceptions"]["exception_count"], 1)
            self.assertEqual(len(payload["exceptions"]["items"]), 1)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
            self.assertTrue(output.with_name("registry.exceptions.json").exists())

    def test_registry_rejects_non_private_output_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir) / "shared"
            parent.mkdir(mode=0o755)
            output = parent / "registry.json"

            with self.assertRaises(PermissionError):
                MODULE.write_registry(MODULE.build_registry([]), output)

    def test_history_preserves_superseded_relationship(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "private" / "registry.json"
            original = MODULE.build_registry([{
                "id": "1",
                "name": "KOVA Old Guide.docx",
                "superseded_by": "source:2",
                "modified": "2026-01-01T00:00:00Z",
            }])
            MODULE.write_registry(original, output)
            refresh = MODULE.build_registry([{
                "id": "1",
                "name": "KOVA Old Guide.docx",
                "modified": "2026-01-01T00:00:00Z",
            }])
            MODULE.write_registry(refresh, output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["items"][0]["superseded_by"], "source:2")
            self.assertEqual(payload["items"][0]["lifecycle"], "ARCHIVE")

    def test_incremental_write_reclassifies_duplicates_against_previous_current_hashes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "private" / "registry.json"
            MODULE.write_registry(MODULE.build_registry([{
                "id": "1",
                "name": "KOVA Plan A.docx",
                "md5Checksum": "same",
                "modified": "2026-01-01T00:00:00Z",
            }]), output)
            MODULE.write_registry(MODULE.build_registry([{
                "id": "2",
                "name": "KOVA Plan B.docx",
                "md5Checksum": "same",
                "modified": "2026-02-01T00:00:00Z",
            }]), output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            rows_by_id = {row["source_id"]: row for row in payload["items"]}
            self.assertIn("DUPLICATE", rows_by_id["1"]["flags"])
            self.assertEqual(rows_by_id["1"]["canonical_version_key"], rows_by_id["2"]["version_key"])
            self.assertNotIn("DUPLICATE", rows_by_id["2"]["flags"])

    def test_merge_history_preserves_prior_decisions_and_verification_evidence(self):
        previous = [{
            "version_key": "same",
            "area": "KOVA",
            "topic": "KOVA Connectors",
            "record_role": "Decision",
            "lifecycle": "FINAL",
            "lifecycle_color": MODULE.LIFECYCLE_COLORS["FINAL"],
            "decision_reason": "Owner approved",
            "flags": ["DUPLICATE"],
            "flag_colors": [MODULE.FLAG_COLORS["DUPLICATE"]],
            "canonical_version_key": "winner",
            "possible_duplicate_of": None,
            "verification": {
                "verified": True,
                "evidence": "Approved",
                "reference": "issue-1",
                "checked_at": "2026-01-01T00:00:00Z",
            },
            "version_evidence": {"md5Checksum": "same", "headRevisionId": "rev-1"},
            "observed_current": False,
        }]
        current = [{
            "version_key": "same",
            "area": "Reagan",
            "topic": "KOVA Workflows",
            "record_role": "Source",
            "lifecycle": "REVIEW",
            "lifecycle_color": MODULE.LIFECYCLE_COLORS["REVIEW"],
            "decision_reason": "Needs current verification",
            "flags": [],
            "flag_colors": [],
            "canonical_version_key": None,
            "possible_duplicate_of": None,
            "verification": {
                "verified": True,
                "evidence": None,
                "reference": None,
                "checked_at": None,
            },
            "version_evidence": {"md5Checksum": "same"},
            "observed_current": True,
        }]
        merged = MODULE.merge_history(current, previous)[0]
        self.assertEqual(merged["area"], "KOVA")
        self.assertEqual(merged["topic"], "KOVA Connectors")
        self.assertEqual(merged["record_role"], "Decision")
        self.assertEqual(merged["lifecycle"], "FINAL")
        self.assertIn("DUPLICATE", merged["flags"])
        self.assertEqual(merged["canonical_version_key"], "winner")
        self.assertEqual(merged["verification"]["evidence"], "Approved")
        self.assertEqual(merged["version_evidence"]["headRevisionId"], "rev-1")
        self.assertEqual(merged["decision_reason"], "Owner approved")

    def test_merge_history_keeps_prior_lifecycle_when_refresh_only_derives_recency(self):
        previous = [{
            "version_key": "same",
            "lifecycle": "ARCHIVE",
            "lifecycle_color": MODULE.LIFECYCLE_COLORS["ARCHIVE"],
            "decision_reason": "Known replacement recorded",
            "verification": {"verified": False, "source_status": None},
            "flags": [],
            "flag_colors": [],
        }]
        current = [{
            "version_key": "same",
            "lifecycle": "ACTIVE",
            "lifecycle_color": MODULE.LIFECYCLE_COLORS["ACTIVE"],
            "decision_reason": "Recent relevant work",
            "verification": {"verified": False, "source_status": None},
            "flags": [],
            "flag_colors": [],
        }]
        merged = MODULE.merge_history(current, previous)[0]
        self.assertEqual(merged["lifecycle"], "ARCHIVE")
        self.assertEqual(merged["decision_reason"], "Known replacement recorded")

    def test_incremental_merge_keeps_previous_observed_current_state_for_unmentioned_items(self):
        previous = [
            {"version_key": "existing", "observed_current": True},
        ]
        current = [
            {"version_key": "new", "observed_current": True},
        ]
        merged = {row["version_key"]: row for row in MODULE.merge_history(current, previous)}
        self.assertTrue(merged["existing"]["observed_current"])
        self.assertTrue(merged["new"]["observed_current"])

    def test_default_private_dir_uses_xdg_data_home(self):
        original_private = MODULE.os.environ.get("KOVA_PRIVATE_STATE_DIR")
        original_xdg = MODULE.os.environ.get("XDG_DATA_HOME")
        try:
            MODULE.os.environ.pop("KOVA_PRIVATE_STATE_DIR", None)
            MODULE.os.environ["XDG_DATA_HOME"] = "/tmp/xdg-home"
            self.assertEqual(MODULE.default_private_dir(), Path("/tmp/xdg-home/kova/private"))
        finally:
            if original_private is None:
                MODULE.os.environ.pop("KOVA_PRIVATE_STATE_DIR", None)
            else:
                MODULE.os.environ["KOVA_PRIVATE_STATE_DIR"] = original_private
            if original_xdg is None:
                MODULE.os.environ.pop("XDG_DATA_HOME", None)
            else:
                MODULE.os.environ["XDG_DATA_HOME"] = original_xdg

    def test_legacy_cli_without_inventory_is_a_noop(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                ["python3", str(SCRIPT), temp_dir, "--execute"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Legacy move/folder arguments were ignored", result.stdout)

    def test_missing_stable_source_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            MODULE.build_registry([{"name": "KOVA Notes.txt"}])

    def test_cli_does_not_modify_governed_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            original = root / "private-config-url.txt"
            original.write_text("unchanged", encoding="utf-8")
            inventory = root / "inventory.json"
            registry = root / "private" / "registry.json"
            inventory.write_text(
                json.dumps([{"source": "local", "path": str(original), "name": original.name}]),
                encoding="utf-8",
            )
            subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(original.read_text(encoding="utf-8"), "unchanged")
            self.assertTrue(registry.exists())

    def test_dry_run_previews_merged_registry_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inventory = root / "inventory.json"
            registry = root / "private" / "registry.json"
            inventory.write_text("[]", encoding="utf-8")
            MODULE.write_registry(
                MODULE.build_registry([{
                    "id": "1",
                    "name": "KOVA Guide.docx",
                    "modified": "2026-01-01T00:00:00Z",
                    "lifecycle": "FINAL",
                    "verified": True,
                }]),
                registry,
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry), "--dry-run"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(len(payload["items"]), 1)
            self.assertFalse(payload["items"][0]["observed_current"])
            self.assertEqual(payload["exceptions"]["exception_count"], 1)

    def test_cli_rejects_registry_that_overwrites_inventory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            inventory = Path(temp_dir) / "inventory.json"
            inventory.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(inventory)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--registry must not overwrite the input inventory", result.stderr)

    def test_cli_rejects_repository_local_registry_output(self):
        inventory = SCRIPT.parents[1] / "tests" / "tmp_inventory.json"
        registry = SCRIPT.parents[1] / "tests" / "tmp_registry.json"
        inventory.write_text("[]", encoding="utf-8")
        try:
            result = subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--registry must point outside the repository checkout", result.stderr)
        finally:
            inventory.unlink(missing_ok=True)
            registry.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
