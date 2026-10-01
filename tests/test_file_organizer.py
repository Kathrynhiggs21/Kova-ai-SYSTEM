import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "file_organizer.py"
SPEC = importlib.util.spec_from_file_location("file_organizer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FileOrganizerTests(unittest.TestCase):
    def test_local_identity_requires_absolute_paths_and_prefers_canonical_path(self):
        with self.assertRaisesRegex(ValueError, "absolute"):
            MODULE.version_key({"source": "local", "id": "unstable-id", "path": "notes.txt", "version": "1"})
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "notes.txt"
            source.write_text("notes")
            item = {"source": "local", "id": "unstable-id", "path": str(source.parent / ".." / source.parent.name / source.name)}
            self.assertEqual(MODULE.source_identity(item), str(source))

    def test_github_identity_uses_repository_and_file_path_instead_of_shared_id(self):
        first = {"source": "github", "id": "shared", "repository": "owner/repo", "path": "one.md", "blob_sha": "same"}
        second = {**first, "path": "two.md"}
        third = {**first, "repository": "owner/other"}
        self.assertEqual(len({MODULE.version_key(item) for item in (first, second, third)}), 3)
        self.assertEqual(MODULE.source_identity(first), "owner/repo:one.md")

    def test_probable_duplicate_pointer_clears_when_current_metadata_resolves_it(self):
        previous = MODULE.build_registry([{"source": "test", "id": "a", "name": "KOVA guide", "size": 12, "version": "1"}])
        previous[0]["possible_duplicate_of"] = "stale-target"
        refreshed = MODULE.build_registry([{"source": "test", "id": "a", "name": "Unrelated item", "size": 13, "version": "1"}])
        merged = MODULE.build_registry_payload(refreshed, previous)["items"]
        self.assertIsNone(merged[0]["possible_duplicate_of"])

    def test_explicit_non_drive_setup_inventory_defaults_to_incremental(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "inventory.json"
            inventory.write_text(json.dumps([{"source": "github", "id": "a", "name": "Guide", "blob_sha": "v1"}]))
            output = root / "private" / "registry.json"
            result = subprocess.run(["bash", str(SCRIPT.parent / "setup_kova_organization.sh"), str(inventory), str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())["items"][0]["version_evidence"]["source"], "github")

    def test_fresh_observation_replaces_history_even_without_modified_timestamps(self):
        previous = MODULE.build_registry([{"source": "test", "id": "a", "name": "Guide", "version": "old"}])
        current = MODULE.build_registry([{"source": "test", "id": "a", "name": "Guide", "version": "new"}])
        merged = MODULE.merge_history(current, previous)
        self.assertEqual([row["version_key"] for row in merged if row["observed_current"]], [current[0]["version_key"]])

    def test_incremental_hashless_title_matches_enter_review(self):
        first = MODULE.build_registry([{"source": "test", "id": "a", "name": "KOVA Guide", "size": 12, "version": "1", "status": "ACTIVE"}])
        second = MODULE.build_registry([{"source": "test", "id": "b", "name": "KOVA Guide copy", "size": 12, "version": "1", "status": "ACTIVE"}])
        rows = MODULE.build_registry_payload(second, first)["items"]
        candidates = [row for row in rows if row.get("possible_duplicate_of")]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["lifecycle"], "REVIEW")
        self.assertNotIn("DUPLICATE", candidates[0]["flags"])

    def test_local_content_is_hashed_once_per_build_and_refreshed_next_build(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "guide.txt"
            source.write_text("first content")
            original_open = Path.open
            reads = []
            def counted_open(path, *args, **kwargs):
                if path == source:
                    reads.append(path)
                return original_open(path, *args, **kwargs)
            item = {"source": "local", "id": "a", "path": str(source), "name": "KOVA Guide"}
            with mock.patch.object(Path, "open", counted_open):
                first = MODULE.build_registry([item])
            self.assertEqual(len(reads), 1)
            source.write_text("second content")
            second = MODULE.build_registry([item])
            self.assertNotEqual(first[0]["version_key"], second[0]["version_key"])

    def test_unverified_scan_timestamp_cannot_override_curated_classification(self):
        item = {"source": "test", "id": "a", "name": "KOVA Connector", "version": "1"}
        previous = MODULE.build_registry([{**item, "verified": True}])
        previous[0].update(area="Personal", topic="KOVA Memory", record_role="Decision")
        current = MODULE.build_registry([{**item, "verified": False, "checked_at": "2026-10-01T00:00:00Z"}])
        merged = MODULE.merge_history(current, previous)[0]
        self.assertEqual((merged["area"], merged["topic"], merged["record_role"]), ("Personal", "KOVA Memory", "Decision"))

    def test_ambiguous_multiple_current_revisions_are_rejected_in_either_order(self):
        items = [{"source": "test", "id": "a", "name": "KOVA Guide", "version": "1"},
                 {"source": "test", "id": "a", "name": "KOVA Guide", "version": "2"}]
        for batch in (items, list(reversed(items))):
            with self.assertRaisesRegex(ValueError, "one current version"):
                MODULE.build_registry(batch)

    def test_drive_metadata_versions_retain_history_when_content_is_unchanged(self):
        item = {"source": "google_drive", "id": "a", "name": "KOVA guide", "md5Checksum": "same", "headRevisionId": "same-revision"}
        first = MODULE.build_registry([{**item, "version": "1"}])
        second = MODULE.build_registry([{**item, "name": "Renamed guide", "version": "2"}])
        self.assertNotEqual(first[0]["version_key"], second[0]["version_key"])
        merged = MODULE.merge_history(second, first)
        self.assertEqual(len(merged), 2)
        self.assertEqual(sum(row["observed_current"] for row in merged), 1)

    def test_exception_output_cannot_overwrite_the_input_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "registry.exceptions.json"
            inventory.write_text("[]")
            with self.assertRaisesRegex(ValueError, "overwrite the input"):
                MODULE.validate_registry_output_path(inventory, root / "registry.json")
            self.assertEqual(inventory.read_text(), "[]")

    def test_unverified_explicit_status_cannot_replace_verified_lifecycle(self):
        initial = MODULE.build_registry([{
            "source": "test", "id": "a", "name": "KOVA guide", "version": "1",
            "status": "FINAL", "verified": True, "verification_evidence": "Owner approved",
        }])
        refresh = MODULE.build_registry([{
            "source": "test", "id": "a", "name": "KOVA guide", "version": "1",
            "status": "ACTIVE", "verified": False,
        }])
        merged = MODULE.merge_history(refresh, initial)[0]
        self.assertEqual(merged["lifecycle"], "FINAL")
        self.assertEqual(merged["verification"]["source_status"], "FINAL")

    def test_supersession_overrides_a_stale_active_status(self):
        lifecycle, _ = MODULE.lifecycle_for({"status": "ACTIVE", "superseded_by": "replacement"})
        self.assertEqual(lifecycle, "ARCHIVE")

    def test_authoritative_clear_inspection_removes_the_sensitive_flag(self):
        item = {"source": "test", "id": "a", "name": "KOVA guide", "version": "1"}
        initial = MODULE.build_registry([{**item, "sensitive": True}])
        refresh = MODULE.build_registry([{**item, "sensitivity_checked": True}])
        merged = MODULE.merge_history(refresh, initial)[0]
        self.assertEqual(merged["sensitivity"], "CLEAR")
        self.assertNotIn("SENSITIVE", merged["flags"])

    def test_delimiters_cannot_collapse_distinct_exact_versions(self):
        first = MODULE.version_key({"source": "test", "id": "a|b", "version": "c"})
        second = MODULE.version_key({"source": "test", "id": "a", "version": "b|c"})
        self.assertNotEqual(first, second)

    def test_upgrade_preserves_earlier_keys_and_verified_decisions(self):
        item = {"source": "test", "id": "a", "name": "KOVA guide", "version": "1"}
        previous = MODULE.build_registry([{**item, "status": "FINAL", "verified": True}])
        previous[0]["version_key"] = "earlier-delimited-key"
        merged = MODULE.merge_history(MODULE.build_registry([item]), previous)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["lifecycle"], "FINAL")

    def test_overlapping_refreshes_retain_both_connector_updates(self):
        code = '''
import sys, time
from pathlib import Path
from scripts import file_organizer as f
original = f.build_registry_payload
def delayed(*args, **kwargs):
    time.sleep(0.3)
    return original(*args, **kwargs)
f.build_registry_payload = delayed
rows = f.build_registry([{"source": "test", "id": sys.argv[2], "name": "KOVA guide", "version": "1"}])
f.write_registry(rows, Path(sys.argv[1]))
'''
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "private" / "registry.json"
            processes = [subprocess.Popen([sys.executable, "-c", code, str(output), identity], cwd=SCRIPT.parents[1]) for identity in ("a", "b")]
            for process in processes:
                self.assertEqual(process.wait(timeout=10), 0)
            rows = json.loads(output.read_text())["items"]
            self.assertEqual({row["source_id"] for row in rows}, {"a", "b"})

    def test_generic_revision_cannot_stand_in_for_supported_evidence(self):
        with self.assertRaisesRegex(ValueError, "supported version evidence"):
            MODULE.version_key({"source": "test", "id": "a", "revision_id": "invented"})
        with self.assertRaisesRegex(ValueError, "supported version evidence"):
            MODULE.version_key({"source": "test", "id": "a", "revision_id": "wrong", "version": "1"})

    def test_scoped_drive_snapshot_preserves_other_sources(self):
        previous = MODULE.build_registry([
            {"source": "google_drive", "id": "drive", "name": "Drive", "version": "1"},
            {"source": "github", "id": "git", "name": "Git", "version": "1"},
            {"source": "local", "id": "local", "name": "Local", "version": "1"},
        ])
        payload = MODULE.build_registry_payload([], previous, full_snapshot=True, snapshot_sources={"google_drive"})
        rows = {row['source_id']: row for row in payload['items']}
        self.assertFalse(rows['drive']['observed_current'])
        self.assertTrue(rows['git']['observed_current'])
        self.assertTrue(rows['local']['observed_current'])
        with self.assertRaisesRegex(ValueError, "outside the selected"):
            MODULE.build_registry_payload(previous, full_snapshot=True, snapshot_sources={"google_drive"})

    def test_registry_rejects_linked_parent_before_touching_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / 'target'
            target.mkdir(mode=0o700)
            alias = root / 'alias'
            alias.symlink_to(target, target_is_directory=True)
            with self.assertRaises(PermissionError):
                MODULE.write_registry([], alias / 'registry.json')
            self.assertEqual(list(target.iterdir()), [])

    def test_registry_rejects_hardlinked_existing_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / 'original.json'
            target.write_text('{"items": []}')
            output = root / 'registry.json'
            output.hardlink_to(target)
            with self.assertRaises(PermissionError):
                MODULE.write_registry([], output)
            self.assertEqual(target.read_text(), '{"items": []}')

    def test_supplied_version_keys_cannot_bypass_evidence_or_collapse_identities(self):
        with self.assertRaisesRegex(ValueError, "version evidence"):
            MODULE.version_key({"source": "test", "id": "a", "version_key": "arbitrary"})
        with self.assertRaisesRegex(ValueError, "does not match"):
            MODULE.version_key({"source": "test", "id": "a", "version": "1", "version_key": "arbitrary"})
        valid = {"source": "test", "id": "a", "version": "1"}
        key = MODULE.version_key(valid)
        self.assertEqual(MODULE.version_key({**valid, "version_key": key}), key)

    def test_canonical_ties_across_source_namespaces_are_order_independent(self):
        items = [
            {"source": "google_drive", "id": "same", "name": "A", "md5Checksum": "same"},
            {"source": "github", "id": "same", "name": "B", "md5Checksum": "same"},
        ]
        def winner(payload):
            return next(r['version_key'] for r in payload if 'DUPLICATE' not in r['flags'])
        initial = MODULE.build_registry(items)
        reversed_rows = MODULE.build_registry(list(reversed(items)))
        self.assertEqual(winner(initial), winner(reversed_rows))
        self.assertEqual(winner(initial), winner(MODULE.build_registry_payload(initial)['items']))

    def test_connector_identity_requires_namespace_and_separates_same_ids(self):
        with self.assertRaisesRegex(ValueError, "source namespace"):
            MODULE.version_key({"id": "same", "version": "1"})
        self.assertNotEqual(
            MODULE.version_key({"source": "google_drive", "id": "same", "version": "1"}),
            MODULE.version_key({"source": "github", "id": "same", "version": "1"}),
        )

    def test_canonical_ranking_compares_absolute_instants(self):
        rows = MODULE.build_registry([
            {"source": "test", "id": "older", "name": "A", "md5Checksum": "same", "modified": "2026-01-01T01:00:00+02:00"},
            {"source": "test", "id": "newer", "name": "B", "md5Checksum": "same", "modified": "2026-01-01T00:30:00Z"},
        ])
        self.assertEqual([r['source_id'] for r in rows if 'DUPLICATE' not in r['flags']], ['newer'])
        payload = MODULE.build_registry_payload(rows)
        self.assertEqual([r['source_id'] for r in payload['items'] if 'DUPLICATE' not in r['flags']], ['newer'])

    def test_explicit_canonical_and_blob_evidence_survive_incremental_publish(self):
        canonical = MODULE.build_registry([{
            "source": "github", "id": "explicit", "name": "A", "blob_sha": "same", "canonical": True,
        }])
        previous = MODULE.build_registry_payload(canonical)['items']
        newer = MODULE.build_registry([{
            "source": "github", "id": "newer", "name": "B", "blob_sha": "same", "modified": "2026-01-01T00:30:00Z",
        }])
        payload = MODULE.build_registry_payload(newer, previous)
        rows = {r['source_id']: r for r in payload['items']}
        self.assertTrue(rows['explicit']['canonical'])
        self.assertEqual(rows['explicit']['version_evidence']['blob_sha'], 'same')
        self.assertNotIn('DUPLICATE', rows['explicit']['flags'])
        self.assertEqual(rows['newer']['canonical_version_key'], rows['explicit']['version_key'])

    def test_new_canonical_clears_old_duplicate_marker(self):
        original = MODULE.build_registry([
            {"source": "test", "id": "a", "name": "A", "md5Checksum": "same"},
            {"source": "test", "id": "b", "name": "B", "md5Checksum": "same"},
        ])
        current = MODULE.build_registry([{
            "source": "test", "id": "a", "name": "A", "md5Checksum": "same", "canonical": True,
        }])
        payload = MODULE.build_registry_payload(current, original)
        rows = {r['source_id']: r for r in payload['items']}
        self.assertNotIn('DUPLICATE', rows['a']['flags'])
        self.assertIsNone(rows['a']['canonical_version_key'])
        self.assertIn('DUPLICATE', rows['b']['flags'])

    def test_complete_snapshot_expires_absent_items_but_delta_preserves_them(self):
        previous = MODULE.build_registry([
            {"source": "test", "id": "a", "name": "A", "version": "1"},
            {"source": "test", "id": "b", "name": "B", "version": "1"},
        ])
        current = MODULE.build_registry([{"source": "test", "id": "a", "name": "A", "version": "1"}])
        snapshot = MODULE.build_registry_payload(current, previous, full_snapshot=True)
        self.assertFalse(next(r for r in snapshot['items'] if r['source_id'] == 'b')['observed_current'])
        delta = MODULE.build_registry_payload(current, previous)
        self.assertTrue(next(r for r in delta['items'] if r['source_id'] == 'b')['observed_current'])
        self.assertTrue(all(r['observed_current'] for r in MODULE.build_registry_payload([], previous)['items']))

    def test_new_revision_retires_previous_current_version(self):
        previous = MODULE.build_registry([{"source": "test", "id": "a", "name": "A", "version": "1"}])
        current = MODULE.build_registry([{"source": "test", "id": "a", "name": "A", "version": "2"}])
        payload = MODULE.build_registry_payload(current, previous)
        self.assertEqual(sum(r['observed_current'] for r in payload['items']), 1)
        self.assertFalse(next(r for r in payload['items'] if r['version_evidence']['version'] == '1')['observed_current'])

    def test_resolved_sensitive_and_duplicate_flags_do_not_create_exceptions(self):
        rows = MODULE.build_registry([
            {"source": "test", "id": "a", "name": "Medical A", "md5Checksum": "same", "verified": True, "lifecycle": "FINAL"},
            {"source": "test", "id": "b", "name": "Medical B", "md5Checksum": "same", "verified": True, "lifecycle": "FINAL"},
        ])
        self.assertEqual(MODULE.build_registry_payload(rows)['exceptions']['exception_count'], 0)
        rows[0]['unresolved_review'] = True
        self.assertEqual(MODULE.build_registry_payload(rows)['exceptions']['exception_count'], 1)

    def test_explicit_area_is_case_insensitive_and_canonical(self):
        self.assertEqual(MODULE.area_for({"area": "KOVA", "name": "Notes.txt"}), "KOVA")
        self.assertEqual(MODULE.area_for({"area": "reagan", "name": "Notes.txt"}), "Reagan")

    def test_short_title_normalizes_kova_and_removes_copy_noise(self):
        item = {"name": "K9va_OS_Automation_Plan_FINAL (2).docx"}
        self.assertEqual(MODULE.short_title(item), "KOVA Operating System Automation Plan")

    def test_short_title_removes_atlas_numbering_without_renaming_source(self):
        item = {"name": "02-07-KOVA-Identity-and-Security.png"}
        self.assertEqual(MODULE.short_title(item), "KOVA Identity and Security")
        self.assertEqual(item["name"], "02-07-KOVA-Identity-and-Security.png")
        self.assertEqual(MODULE.short_title({"name": "03-00-KOVA-OS-Atlas-Cover.png"}), "KOVA Operating System Atlas Cover")

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
        self.assertEqual(MODULE.lifecycle_for({
            "name": "KOVA API Final Guide", "status": "FINAL",
            "modified": MODULE.datetime.now(MODULE.timezone.utc).isoformat(),
        })[0], "REVIEW")

    def test_boundary_matching_does_not_call_capital_an_api_topic(self):
        self.assertEqual(MODULE.topic_for({"name": "KOVA Capital Budget.txt"}), "KOVA Reference")
        self.assertEqual(MODULE.topic_for({"name": "KOVA API Plan.txt"}), "KOVA Connectors")

    def test_separator_sensitive_and_uninspected_state(self):
        self.assertEqual(MODULE.sensitivity_for({"name": "private-config-url.txt"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "credentials.json"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "passwords.txt"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "api-keys.txt"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "secrets.txt"})[0], "SENSITIVE")
        self.assertEqual(MODULE.sensitivity_for({"name": "ordinary-notes.txt"})[0], "UNKNOWN")
        self.assertEqual(
            MODULE.sensitivity_for({"name": "ordinary-notes.txt", "content_inspected": True})[0],
            "CLEAR",
        )

    def test_exact_duplicate_requires_hash_and_is_deterministic(self):
        items = [
            {"source": "test_connector", "id": "older", "name": "KOVA Plan.docx", "md5Checksum": "same", "modified": "2026-01-01T00:00:00Z"},
            {"source": "test_connector", "id": "newer", "name": "KOVA Plan.docx", "md5Checksum": "same", "modified": "2026-02-01T00:00:00Z"},
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
            {"source": "test_connector", "id": "older", "name": "KOVA Plan.docx", "blob_sha": "same", "modified": "2026-01-01T00:00:00Z"},
            {"source": "test_connector", "id": "newer", "name": "KOVA Plan.docx", "blob_sha": "same", "modified": "2026-02-01T00:00:00Z"},
        ])
        self.assertIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])

    def test_same_title_without_hash_is_only_a_review_candidate(self):
        rows = MODULE.build_registry([
            {"source": "test_connector", "id": "1", "name": "KOVA Plan.docx", "size": 9, "version": "1", "modified": "2026-01-01T00:00:00Z"},
            {"source": "test_connector", "id": "2", "name": "KOVA Plan.docx", "size": 9, "version": "2", "modified": "2026-02-01T00:00:00Z"},
        ])
        self.assertNotIn("DUPLICATE", rows[0]["flags"])
        self.assertNotIn("DUPLICATE", rows[1]["flags"])
        candidates = [row for row in rows if row["possible_duplicate_of"] is not None]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["lifecycle"], "REVIEW")

    def test_mixed_hash_likely_group_is_marked_for_review(self):
        rows = MODULE.build_registry([
            {"source": "test_connector", "id": "hashless-newer", "name": "KOVA Plan.docx", "size": 9, "version": "2", "modified": "2026-02-01T00:00:00Z"},
            {"source": "test_connector", "id": "hashed-older", "name": "KOVA Plan.docx", "size": 9, "md5Checksum": "abc", "modified": "2026-01-01T00:00:00Z"},
        ])
        candidates = [row for row in rows if row["possible_duplicate_of"] is not None]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["source_id"], "hashed-older")
        self.assertEqual(candidates[0]["lifecycle"], "REVIEW")

    def test_version_identity_includes_source(self):
        a = MODULE.version_key({"source": "test_connector", "id": "a", "md5Checksum": "same"})
        b = MODULE.version_key({"source": "test_connector", "id": "b", "md5Checksum": "same"})
        self.assertNotEqual(a, b)

    def test_version_identity_rejects_modified_timestamp_only_evidence(self):
        with self.assertRaises(ValueError):
            MODULE.version_key({"source": "test_connector", "id": "a", "modified": "2026-02-01T00:00:00Z"})

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
                "source": "test_connector", "id": "1", "name": "KOVA Guide.docx", "modified": "2026-01-01T00:00:00Z",
                "version": "1",
                "lifecycle": "FINAL", "verified": True, "verification_evidence": "Owner approved"
            }])
            MODULE.write_registry(old, output)
            MODULE.write_registry(MODULE.build_registry([]), output, full_snapshot=True)
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
                MODULE.write_registry(MODULE.build_registry([]), output, full_snapshot=True)

    def test_history_preserves_superseded_relationship(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "private" / "registry.json"
            original = MODULE.build_registry([{
                "source": "test_connector", "id": "1",
                "name": "KOVA Old Guide.docx",
                "superseded_by": "source:2",
                "version": "1",
                "modified": "2026-01-01T00:00:00Z",
            }])
            MODULE.write_registry(original, output)
            refresh = MODULE.build_registry([{
                "source": "test_connector", "id": "1",
                "name": "KOVA Old Guide.docx",
                "version": "1",
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
                "source": "test_connector", "id": "1",
                "name": "KOVA Plan A.docx",
                "md5Checksum": "same",
                "modified": "2026-01-01T00:00:00Z",
            }]), output)
            MODULE.write_registry(MODULE.build_registry([{
                "source": "test_connector", "id": "2",
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

    def test_current_version_is_independent_of_merge_order(self):
        old = {"version_key": "old", "source_id": "one", "observed_current": True, "version_evidence": {"source": "test", "revision_id": "1", "modified": "2026-01-01T00:00:00Z"}}
        new = {"version_key": "new", "source_id": "one", "observed_current": True, "version_evidence": {"source": "test", "revision_id": "2", "modified": "2026-02-01T00:00:00Z"}}
        for order in ([old, new], [new, old]):
            rows = {row["version_key"]: row for row in MODULE.merge_history(order, [])}
            self.assertFalse(rows["old"]["observed_current"])
            self.assertTrue(rows["new"]["observed_current"])

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
                    "source": "test_connector", "id": "1",
                    "name": "KOVA Guide.docx",
                    "version": "1",
                    "modified": "2026-01-01T00:00:00Z",
                    "lifecycle": "FINAL",
                    "verified": True,
                }]),
                registry,
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry), "--dry-run", "--full-snapshot"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["item_count"], 1)
            self.assertEqual(payload["current_count"], 0)
            self.assertEqual(payload["exception_count"], 1)

    def test_dry_run_does_not_print_retained_private_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "private" / "registry.json"
            inventory = root / "inventory.json"
            inventory.write_text("[]")
            MODULE.write_registry(MODULE.build_registry([{
                "source": "test", "id": "PRIVATE-ID-MARKER", "version": "1",
                "name": "PRIVATE-FILENAME-MARKER", "url": "https://example.test/?token=TOKEN-MUST-NOT-PRINT",
                "verification_reference": "PRIVATE-REFERENCE-MARKER",
            }]), registry)
            result = subprocess.run([sys.executable, str(SCRIPT), "--inventory", str(inventory), "--registry", str(registry), "--dry-run"], check=True, capture_output=True, text=True)
            self.assertEqual(json.loads(result.stdout)["item_count"], 1)
            for marker in ("PRIVATE-ID-MARKER", "PRIVATE-FILENAME-MARKER", "TOKEN-MUST-NOT-PRINT", "PRIVATE-REFERENCE-MARKER", "source_link"):
                self.assertNotIn(marker, result.stdout)

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
