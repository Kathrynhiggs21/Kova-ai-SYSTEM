"""Shared repository-coordinate rules for the canonical KOVA registry."""

import re
from typing import Optional, Tuple


CANONICAL_GITHUB_OWNER = "Kathrynhiggs21"
CANONICAL_REPOSITORIES = (
    "Kathrynhiggs21/Kova-ai-SYSTEM",
    "Kathrynhiggs21/kova-ai-dash",
)

_GITHUB_OWNER_PATTERN = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$"
)
_GITHUB_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


def is_safe_github_owner(value: object) -> bool:
    """Return whether a value is a URL-safe GitHub owner coordinate."""
    return isinstance(value, str) and _GITHUB_OWNER_PATTERN.fullmatch(value) is not None


def parse_github_repository(value: object) -> Optional[Tuple[str, str]]:
    """Parse a strict ``owner/repository`` coordinate without URL semantics."""
    if not isinstance(value, str) or value.count("/") != 1:
        return None

    owner, repository = value.split("/", 1)
    if not is_safe_github_owner(owner):
        return None
    if (
        repository in {".", ".."}
        or _GITHUB_REPOSITORY_PATTERN.fullmatch(repository) is None
    ):
        return None
    return owner, repository


def repository_key(value: str) -> str:
    """Return the comparison key GitHub uses for repository coordinates."""
    return value.casefold()
