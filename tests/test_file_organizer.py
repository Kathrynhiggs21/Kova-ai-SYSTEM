import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "file_organizer.py"
SPEC = importlib.util.spec_from_file_location("file_organizer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FileOrganizerTests(unittest.TestCase):
    def test_short_title_normalizes_kova_and_removes_copy_noise(self):
        item = {"name": "K9va_OS_Automation_Plan_FINAL (2).docx"}
        self.assertEqual(MODULE.short_title(item), "KOVA Operating System Automation Plan")

    def test_final_requires_verification(self):
        unverified = {"name": "KOVA Final Guide.docx"}
        verified = {"name": "KOVA Final Guide.docx", "verified": True}
        self.assertEqual(MODULE.lifecycle_for(unverified)[0], "REVIEW")
        self.assertEqual(MODULE.lifecycle_for(verified)[0], "FINAL")

    def test_registry_flags_sensitive_duplicate_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            original = Path(temp_dir) / "private-config-url.txt"
            original.write_text("unchanged", encoding="utf-8")
            items = [
                {"id": "1", "name": original.name, "size": 9, "description": "private config URL"},
                {"id": "2", "name": original.name, "size": 9, "description": "private config URL"},
            ]

            rows = MODULE.build_registry(items)

            self.assertEqual(rows[0]["flags"], ["SENSITIVE"])
            self.assertEqual(rows[1]["flags"], ["SENSITIVE", "DUPLICATE"])
            self.assertEqual(rows[1]["canonical_version_key"], rows[0]["version_key"])
            self.assertEqual(original.read_text(encoding="utf-8"), "unchanged")

    def test_write_registry_is_metadata_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "registry.json"
            MODULE.write_registry([], output)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["organization_mode"], "metadata-first")
            self.assertFalse(payload["physical_changes"])


if __name__ == "__main__":
    unittest.main()
