"""Race regressions for descriptor-relative private state operations."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import private_state


class PrivateStateTests(unittest.TestCase):
    def test_parent_swap_cannot_redirect_a_private_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "private"
            retained = root / "retained"
            foreign = root / "foreign"
            parent.mkdir(mode=0o700)
            foreign.mkdir(mode=0o700)
            original_open = os.open
            swapped = False
            def racing_open(name, flags, *args, **kwargs):
                nonlocal swapped
                descriptor = original_open(name, flags, *args, **kwargs)
                if name == "private" and not swapped:
                    swapped = True
                    parent.rename(retained)
                    parent.symlink_to(foreign, target_is_directory=True)
                return descriptor
            with mock.patch.object(private_state.os, "open", racing_open):
                private_state.write_private_text(parent / "registry.json", "private-value")
            self.assertEqual(list(foreign.iterdir()), [])
            self.assertEqual((retained / "registry.json").read_text(), "private-value")

    def test_parent_swap_cannot_redirect_a_credential_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "private"
            foreign = root / "foreign"
            parent.mkdir(mode=0o700)
            foreign.mkdir(mode=0o700)
            (parent / "token.json").write_text("approved-token")
            (foreign / "token.json").write_text("foreign-token")
            original_open = os.open
            swapped = False
            def racing_open(name, flags, *args, **kwargs):
                nonlocal swapped
                descriptor = original_open(name, flags, *args, **kwargs)
                if name == "private" and not swapped:
                    swapped = True
                    parent.rename(root / "retained")
                    parent.symlink_to(foreign, target_is_directory=True)
                return descriptor
            with mock.patch.object(private_state.os, "open", racing_open):
                self.assertEqual(private_state.read_private_text(parent / "token.json"), "approved-token")

    def test_new_nested_state_directories_are_private_from_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_state.write_private_text(root / "new" / "private" / "state.json", "{}")
            self.assertEqual((root / "new").stat().st_mode & 0o777, 0o700)
            self.assertEqual((root / "new" / "private").stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
