"""Prevent published downloads from silently serving a stale reference client."""

from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile
from scripts.export_kova_os import package_zip


ROOT = Path(__file__).resolve().parents[1]


class PublishedSiteArchiveTests(unittest.TestCase):
    def test_complete_archive_replaces_the_served_path_only_after_extra_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text("current")
            config = root / "dashboard.json"
            config.write_text("configuration")
            target = root / "site_final.zip"
            target.write_bytes(b"previous archive")
            original_write = zipfile.ZipFile.write
            def check_served_archive(archive, source, *args, **kwargs):
                self.assertEqual(target.read_bytes(), b"previous archive")
                return original_write(archive, source, *args, **kwargs)
            with mock.patch.object(zipfile.ZipFile, "write", check_served_archive):
                self.assertTrue(package_zip(site, target, extra_files={config: "config/dashboard.v1.json"}))
            with zipfile.ZipFile(target) as archive:
                self.assertEqual(archive.read("config/dashboard.v1.json"), b"configuration")

    def test_archive_build_failure_preserves_previous_download(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            site = root / "site"
            site.mkdir()
            (site / "index.html").write_text("current")
            target = root / "site_final.zip"
            target.write_bytes(b"previous archive")
            with mock.patch.object(zipfile.ZipFile, "write", side_effect=OSError("interrupted")):
                with self.assertRaises(OSError):
                    package_zip(site, target)
            self.assertEqual(target.read_bytes(), b"previous archive")
            self.assertEqual(list(root.glob("*.tmp")), [])

    def test_published_archive_matches_current_source_and_status_configuration(self):
        sources = {
            str(path.relative_to(ROOT / "site")): path
            for path in (ROOT / "site").rglob("*")
            if path.is_file()
        }
        sources["config/dashboard.v1.json"] = ROOT / "config/dashboard.v1.json"
        with zipfile.ZipFile(ROOT / "site_final.zip") as archive:
            self.assertEqual(set(archive.namelist()), set(sources))
            for name, source in sources.items():
                with self.subTest(path=name):
                    self.assertEqual(archive.read(name), source.read_bytes())


if __name__ == "__main__":
    unittest.main()
