import importlib.util
import json
from contextlib import chdir
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
    def test_non_object_tokens_fail_closed_before_provider_access(self):
        for content in ("null", "[]", '"token"', "42"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                with mock.patch.dict(MODULE.os.environ, {"KOVA_PRIVATE_STATE_DIR": directory}):
                    importer = MODULE.GoogleDriveImporter()
                importer.auth_dir.mkdir(mode=0o700)
                token = importer.auth_dir / "token.json"
                token.write_text(content)
                with mock.patch.object(MODULE, "GDRIVE_AVAILABLE", True), mock.patch.object(MODULE, "Credentials", create=True) as credentials:
                    self.assertFalse(importer.authenticate())
                    credentials.from_authorized_user_info.assert_not_called()
                self.assertEqual(token.read_text(), content)

    def test_malformed_provider_token_errors_return_false(self):
        for error in (TypeError("malformed"), AttributeError("malformed")):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory:
                with mock.patch.dict(MODULE.os.environ, {"KOVA_PRIVATE_STATE_DIR": directory}):
                    importer = MODULE.GoogleDriveImporter()
                importer.auth_dir.mkdir(mode=0o700)
                token = importer.auth_dir / "token.json"
                token.write_text("{}")
                with mock.patch.object(MODULE, "GDRIVE_AVAILABLE", True), mock.patch.object(MODULE, "Credentials", create=True) as credentials:
                    credentials.from_authorized_user_info.side_effect = error
                    self.assertFalse(importer.authenticate())
                self.assertEqual(token.read_text(), "{}")

    def test_successful_empty_scan_publishes_a_new_empty_snapshot(self):
        importer = MODULE.GoogleDriveImporter()
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(importer, "authenticate", return_value=True), \
                mock.patch.object(importer, "search_kova_files", return_value=[]), \
                mock.patch.dict(MODULE.os.environ, {"KOVA_PRIVATE_STATE_DIR": directory}):
            inventory = importer.run()
            self.assertEqual(json.loads(inventory.read_text()), [])

    def test_failed_scan_cannot_publish_an_empty_or_stale_snapshot(self):
        importer = MODULE.GoogleDriveImporter()
        importer.service = mock.Mock()
        importer.service.files.return_value.list.return_value.execute.side_effect = RuntimeError("test provider error")
        with mock.patch.object(importer, "authenticate", return_value=True), \
                mock.patch.object(importer, "save_inventory") as save:
            with self.assertRaisesRegex(RuntimeError, "Drive scan failed"):
                importer.run()
            save.assert_not_called()

    def test_linked_parent_is_rejected_before_credential_access(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / 'target'
            target.mkdir(mode=0o700)
            alias = root / 'alias'
            alias.symlink_to(target, target_is_directory=True)
            with mock.patch.dict(MODULE.os.environ, {'KOVA_PRIVATE_STATE_DIR': str(alias)}):
                importer = MODULE.GoogleDriveImporter()
            with mock.patch.object(MODULE, 'GDRIVE_AVAILABLE', True), \
                    mock.patch.object(MODULE, 'Credentials', create=True) as credentials:
                self.assertFalse(importer.authenticate())
                credentials.from_authorized_user_info.assert_not_called()
            self.assertEqual(list(target.iterdir()), [])

    def test_hardlinked_token_is_rejected_without_chmod_or_read(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            with mock.patch.dict(MODULE.os.environ, {'KOVA_PRIVATE_STATE_DIR': str(root)}):
                importer = MODULE.GoogleDriveImporter()
            importer.auth_dir.mkdir(mode=0o700)
            target = root / 'original.json'
            target.write_text('{}')
            target.chmod(0o644)
            (importer.auth_dir / 'token.json').hardlink_to(target)
            with mock.patch.object(MODULE, 'GDRIVE_AVAILABLE', True), \
                    mock.patch.object(MODULE, 'Credentials', create=True) as credentials:
                self.assertFalse(importer.authenticate())
                credentials.from_authorized_user_info.assert_not_called()
            self.assertEqual(target.stat().st_mode & 0o777, 0o644)
            self.assertEqual(target.read_text(), '{}')

    def test_authentication_writes_private_json_and_ignores_legacy_pickle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state = Path(temp_dir) / 'state'
            credentials = Path(temp_dir) / 'credentials.json'
            credentials.write_text('{}')
            # Invalid bytes must never be deserialized as executable pickle.
            legacy = Path(temp_dir) / 'token.pickle'
            legacy.write_bytes(b'not a credential')
            with mock.patch.dict(MODULE.os.environ, {'KOVA_PRIVATE_STATE_DIR': str(state)}):
                importer = MODULE.GoogleDriveImporter(str(credentials))
            creds = mock.Mock(valid=True)
            creds.to_json.return_value = json.dumps({'token': 'test-only-token'})
            flow = mock.Mock()
            flow.run_local_server.return_value = creds
            with mock.patch.object(MODULE, 'GDRIVE_AVAILABLE', True), \
                    mock.patch.object(MODULE, 'InstalledAppFlow', create=True) as flows, \
                    mock.patch.object(MODULE, 'build', create=True) as build, \
                    chdir(temp_dir):
                flows.from_client_config.return_value = flow
                self.assertTrue(importer.authenticate())
                build.assert_called_once_with('drive', 'v3', credentials=creds)
            token = state / 'google-drive' / 'token.json'
            self.assertEqual(json.loads(token.read_text()), {'token': 'test-only-token'})
            self.assertEqual(token.stat().st_mode & 0o777, 0o600)
            self.assertEqual(token.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(legacy.read_bytes(), b'not a credential')

    def test_invalid_token_fails_closed_without_overwrite_or_sign_in(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(MODULE.os.environ, {'KOVA_PRIVATE_STATE_DIR': temp_dir}):
                importer = MODULE.GoogleDriveImporter()
            importer.auth_dir.mkdir(mode=0o700)
            token = importer.auth_dir / 'token.json'
            token.write_text('invalid')
            with mock.patch.object(MODULE, 'GDRIVE_AVAILABLE', True), \
                    mock.patch.object(MODULE, 'Credentials', create=True) as credentials, \
                    mock.patch.object(MODULE, 'InstalledAppFlow', create=True) as flows:
                credentials.from_authorized_user_info.side_effect = ValueError('invalid')
                self.assertFalse(importer.authenticate())
                credentials.from_authorized_user_info.assert_not_called()
                flows.from_client_config.assert_not_called()
            self.assertEqual(token.read_text(), 'invalid')

    def test_linked_token_is_rejected_without_loading_credentials(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(MODULE.os.environ, {'KOVA_PRIVATE_STATE_DIR': temp_dir}):
                importer = MODULE.GoogleDriveImporter()
            importer.auth_dir.mkdir(mode=0o700)
            target = Path(temp_dir) / 'original.json'
            target.write_text('{}')
            (importer.auth_dir / 'token.json').symlink_to(target)
            with mock.patch.object(MODULE, 'GDRIVE_AVAILABLE', True), \
                    mock.patch.object(MODULE, 'Credentials', create=True) as credentials:
                self.assertFalse(importer.authenticate())
                credentials.from_authorized_user_info.assert_not_called()
            self.assertEqual(target.read_text(), '{}')

    def test_only_contextual_kiva_aliases_are_searchable(self):
        self.assertNotIn("kiva", MODULE.KOVA_KEYWORDS)
        self.assertIn("kiva os", MODULE.KOVA_KEYWORDS)
        self.assertIn("kiva-ai", MODULE.KOVA_KEYWORDS)

    def test_save_inventory_uses_private_permissions(self):
        importer = MODULE.GoogleDriveImporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "kova_file_inventory"
            with mock.patch.object(MODULE, "datetime") as mocked_datetime:
                mocked_datetime.now.return_value = datetime(2026, 9, 16, 18, 0, 0)
                inventory = importer.save_inventory([{"category": "CORE"}], [], output_dir=output_dir)

            self.assertEqual(output_dir.stat().st_mode & 0o777, 0o700)
            self.assertTrue(inventory.name.startswith("inventory_20260916_180000_"))
            self.assertEqual(inventory.stat().st_mode & 0o777, 0o600)
            self.assertTrue(all(path.stat().st_mode & 0o777 == 0o600 for path in output_dir.iterdir()))

    def test_save_inventory_defaults_to_private_state_directory(self):
        importer = MODULE.GoogleDriveImporter()
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(MODULE.os.environ, {"KOVA_PRIVATE_STATE_DIR": temp_dir}, clear=False):
                with mock.patch.object(MODULE, "datetime") as mocked_datetime:
                    mocked_datetime.now.return_value = datetime(2026, 9, 16, 18, 0, 0)
                    importer.save_inventory([{"category": "CORE"}], [])

            output_dir = Path(temp_dir) / "inventory"
            self.assertEqual(output_dir.stat().st_mode & 0o777, 0o700)
            self.assertEqual(len(list(output_dir.glob("inventory_20260916_180000_*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
