"""Prevent published downloads from silently serving a stale reference client."""

from pathlib import Path
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class PublishedSiteArchiveTests(unittest.TestCase):
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
