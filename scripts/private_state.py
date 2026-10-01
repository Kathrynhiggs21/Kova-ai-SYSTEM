"""Validate private state paths without following linked filesystem entries."""

import os
import secrets
import stat
from contextlib import contextmanager
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


@contextmanager
def private_directory(path: Path, *, create: bool = False):
    """Pin every directory component without following a concurrently swapped link."""
    requested = validate_unlinked_path(path)
    descriptor = os.open(requested.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in requested.parts[1:]:
            if part in {".", ".."}:
                raise PermissionError("private state paths must use canonical components")
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise
                try:
                    os.mkdir(part, mode=0o700, dir_fd=descriptor)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        if os.fstat(descriptor).st_mode & 0o777 != 0o700:
            raise PermissionError("private state requires a dedicated user-only directory")
        yield descriptor
    finally:
        os.close(descriptor)


def validate_file_metadata(metadata) -> None:
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise PermissionError("private state files must be regular files with one link")


def read_text_at(directory: int, name: str, *, restrict_permissions: bool = False) -> str:
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        validate_file_metadata(os.fstat(descriptor))
        if restrict_permissions:
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "r", encoding="utf-8", closefd=False) as source:
            return source.read()
    finally:
        os.close(descriptor)


def read_private_text(path: Path, *, restrict_permissions: bool = False) -> str:
    requested = validate_unlinked_path(path)
    with private_directory(requested.parent) as directory:
        return read_text_at(directory, requested.name, restrict_permissions=restrict_permissions)


def write_text_at(directory: int, name: str, content: str) -> None:
    try:
        validate_file_metadata(os.stat(name, dir_fd=directory, follow_symlinks=False))
    except FileNotFoundError:
        pass
    temporary = f".{name}.{secrets.token_hex(16)}.tmp"
    descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600, dir_fd=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", closefd=False) as output:
            os.fchmod(descriptor, 0o600)
            output.write(content)
            output.flush()
            os.fsync(descriptor)
        os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
    finally:
        os.close(descriptor)
        try:
            os.unlink(temporary, dir_fd=directory)
        except FileNotFoundError:
            pass


def write_private_text(path: Path, content: str) -> None:
    requested = validate_unlinked_path(path)
    with private_directory(requested.parent, create=True) as directory:
        write_text_at(directory, requested.name, content)
