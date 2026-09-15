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

    def test_same_title_without_hash_is_only_a_review_candidate(self):
        rows = MODULE.build_registry([
            {"id": "1", "name": "KOVA Plan.docx", "size": 9},
            {"id": "2", "name": "KOVA Plan.docx", "size": 9},
        ])
        self.assertNotIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])
        candidates = [row for row in rows if row["possible_duplicate_of"] is not None]
        self.assertEqual(len(candidates), 1)
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

    def test_chat_record_role_does_not_infer_a_decision(self):
        self.assertEqual(MODULE.record_role_for({"name": "KOVA ideas chat"}), "Unknown")
        self.assertEqual(MODULE.record_role_for({"record_role": "decision"}), "Decision")

    def test_history_and_verified_decision_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "registry.json"
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
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            self.assertEqual(output.parent.stat().st_mode & 0o777, 0o700)
            self.assertTrue(output.with_name("registry.exceptions.json").exists())

    def test_history_preserves_superseded_relationship(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "registry.json"
            original = MODULE.build_registry([{"id": "1", "name": "KOVA Old Guide.docx", "superseded_by": "source:2"}])
            MODULE.write_registry(original, output)
            refresh = MODULE.build_registry([{"id": "1", "name": "KOVA Old Guide.docx"}])
            MODULE.write_registry(refresh, output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["items"][0]["superseded_by"], "source:2")

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
            inventory.write_text(json.dumps([{"id": "1", "name": original.name}]), encoding="utf-8")
            subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(original.read_text(encoding="utf-8"), "unchanged")
            self.assertTrue(registry.exists())


if __name__ == "__main__":
    unittest.main()
