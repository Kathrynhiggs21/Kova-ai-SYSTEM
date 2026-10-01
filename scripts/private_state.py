"""Validate private state paths without following linked filesystem entries."""

import stat
from pathlib import Path


def validate_unlinked_path(path: Path) -> Path:
    requested = path.expanduser()
    if not requested.is_absolute():
        requested = Path.cwd() / requested
    current = Path(requested.anchor)
    for part in requested.parts[1:]:
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode):
            raise PermissionError("private state paths must not contain symbolic links")
        if current == requested and not stat.S_ISDIR(metadata.st_mode):
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                raise PermissionError("private state files must be regular files with one link")
    return requested
