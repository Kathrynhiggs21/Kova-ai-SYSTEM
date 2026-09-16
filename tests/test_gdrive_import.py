import importlib.util
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "scripts" / "gdrive_import.py"
SPEC = importlib.util.spec_from_file_location("gdrive_import", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class GoogleDriveImportTests(unittest.TestCase):
    def test_kiva_alias_is_searchable(self):
        self.assertIn("kiva", MODULE.KOVA_KEYWORDS)

    def test_save_inventory_uses_private_permissions(self):
        importer = MODULE.GoogleDriveImporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "kova_file_inventory"
            with mock.patch.object(MODULE, "datetime") as mocked_datetime:
                mocked_datetime.now.return_value = datetime(2026, 9, 16, 18, 0, 0)
                importer.save_inventory([{"category": "CORE"}], [], output_dir=output_dir)

            self.assertEqual(output_dir.stat().st_mode & 0o777, 0o700)
            self.assertEqual((output_dir / "inventory_20260916_180000.json").stat().st_mode & 0o777, 0o600)
            self.assertEqual((output_dir / "duplicates_20260916_180000.json").stat().st_mode & 0o777, 0o600)
            self.assertEqual((output_dir / "summary_20260916_180000.txt").stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
