#!/usr/bin/env python3
"""Build KOVA's non-destructive file metadata registry.

The legacy organizer created a large folder tree and moved or renamed files.
KOVA now organizes with metadata first. This script reads an inventory and
writes lifecycle, topic, duplicate, and sensitivity decisions without touching
the governed files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


LIFECYCLE_COLORS = {
    "ACTIVE": "#0969DA",
    "FINAL": "#1F883D",
    "REVIEW": "#BF8700",
    "ARCHIVE": "#6E7781",
}

FLAG_COLORS = {
    "SENSITIVE": "#CF222E",
    "DUPLICATE": "#8250DF",
}

CATEGORY_KEYWORDS = {
    "KOVA Operating System": ("operating system", "architecture", "roadmap", "core"),
    "KOVA AI Assistant": ("assistant", "agent", "model", "prompt", "openai", "claude", "gemini"),
    "KOVA Automation": ("automation", "workflow", "zapier", "make.com", "n8n", "schedule", "trigger"),
    "KOVA Connectors": ("connector", "mcp", "oauth", "integration", "webhook", "api"),
    "KOVA Interface": ("dashboard", "command center", "site", "orb", "mobile", "android"),
    "KOVA Memory": ("memory", "mem0", "knowledge", "registry", "index"),
    "KOVA Worlds": ("scribbles", "reagan", "family", "travel", "health", "education", "zoo"),
}

SENSITIVE_MARKERS = (
    "credential",
    "password",
    "private key",
    "api key",
    "access token",
    "refresh token",
    "config url",
    "secret",
)

NOISE_WORDS = {
    "copy",
    "document",
    "file",
    "new",
    "old",
    "untitled",
    "unknown",
}


def canonicalize_kova(value: str) -> str:
    """Normalize common KOVA spellings without changing the source file."""
    value = re.sub(r"\b(?:k9va|kiva|kova)[-_ ]?os\b", "KOVA Operating System", value, flags=re.I)
    value = re.sub(r"\b(?:k9va|kiva|kova)[-_ ]?ai\b", "KOVA AI", value, flags=re.I)
    value = re.sub(r"\b(?:k9va|kiva|kova)\b", "KOVA", value, flags=re.I)
    return value


def short_title(file_info: dict[str, Any], limit: int = 80) -> str:
    """Return a readable topic/subtopic title; keep identifiers as metadata."""
    explicit = file_info.get("suggested_title") or file_info.get("title")
    raw = str(explicit or Path(str(file_info.get("name", "KOVA Item"))).stem)
    raw = re.sub(r"[_-]+", " ", raw)
    raw = canonicalize_kova(raw)
    raw = re.sub(r"\s*\(\d+\)\s*$", "", raw)
    raw = re.sub(r"(?:[-_ ]+(?:copy|final|draft|v?\d+(?:\.\d+)*))+\s*$", "", raw, flags=re.I)
    words = [word for word in raw.split() if word.lower() not in NOISE_WORDS]
    title = " ".join(words).strip() or "KOVA Item"
    if len(title) <= limit:
        return title
    return title[: limit - 1].rstrip() + "…"


def category_for(file_info: dict[str, Any]) -> str:
    haystack = " ".join(
        str(file_info.get(key, "")) for key in ("name", "title", "description", "path")
    ).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category
    return "KOVA Reference"


def is_sensitive(file_info: dict[str, Any]) -> bool:
    if file_info.get("sensitive") is True:
        return True
    haystack = " ".join(
        str(file_info.get(key, "")) for key in ("name", "title", "description", "text")
    ).lower()
    return any(marker in haystack for marker in SENSITIVE_MARKERS)


def lifecycle_for(file_info: dict[str, Any]) -> tuple[str, str]:
    """Classify lifecycle conservatively and explain the decision."""
    explicit = str(file_info.get("lifecycle") or file_info.get("status") or "").upper()
    if explicit in LIFECYCLE_COLORS:
        return explicit, "Explicit source status"
    if file_info.get("superseded_by"):
        return "ARCHIVE", "Known replacement recorded"
    if file_info.get("verified") is True and re.search(
        r"\b(final|approved|locked|canonical)\b", str(file_info.get("name", "")), re.I
    ):
        return "FINAL", "Verified final/canonical marker"

    modified = file_info.get("modified") or file_info.get("modifiedTime")
    if modified:
        try:
            when = datetime.fromisoformat(str(modified).replace("Z", "+00:00"))
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - when.astimezone(timezone.utc)).days
            if age_days <= 90 and category_for(file_info) != "KOVA Reference":
                return "ACTIVE", "Recent KOVA work"
        except ValueError:
            pass
    return "REVIEW", "Needs current verification"


def version_key(file_info: dict[str, Any]) -> str:
    """Create a stable key for an exact version without exposing private data."""
    for key in ("version_key", "sha256", "blob_sha", "md5Checksum"):
        if file_info.get(key):
            return str(file_info[key])
    identity = "|".join(
        str(file_info.get(key, ""))
        for key in ("id", "file_id", "name", "size", "modified", "modifiedTime")
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def duplicate_key(file_info: dict[str, Any], title: str) -> str:
    content_hash = file_info.get("sha256") or file_info.get("md5Checksum")
    if content_hash:
        return f"hash:{content_hash}"
    normalized = re.sub(r"\W+", "", title).lower()
    return f"title-size:{normalized}:{file_info.get('size', '')}"


def build_registry(inventory: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: dict[str, int] = {}

    for file_info in inventory:
        title = short_title(file_info)
        lifecycle, reason = lifecycle_for(file_info)
        flags = ["SENSITIVE"] if is_sensitive(file_info) else []
        dup_key = duplicate_key(file_info, title)
        canonical_row = seen.get(dup_key)
        if canonical_row is None:
            seen[dup_key] = len(rows)
        else:
            flags.append("DUPLICATE")

        rows.append(
            {
                "version_key": version_key(file_info),
                "source_name": file_info.get("name"),
                "display_title": title,
                "topic": category_for(file_info),
                "lifecycle": lifecycle,
                "lifecycle_color": LIFECYCLE_COLORS[lifecycle],
                "flags": flags,
                "flag_colors": [FLAG_COLORS[flag] for flag in flags],
                "reason": reason,
                "source_id": file_info.get("id") or file_info.get("file_id"),
                "source_link": file_info.get("web_link") or file_info.get("url"),
                "source_chat_id": file_info.get("chat_id") or file_info.get("agent_id"),
                "canonical_version_key": rows[canonical_row]["version_key"] if canonical_row is not None else None,
                "superseded_by": file_info.get("superseded_by"),
            }
        )
    return rows


def write_registry(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "organization_mode": "metadata-first",
        "physical_changes": False,
        "items": rows,
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build KOVA's non-destructive file status registry")
    parser.add_argument("base_path", nargs="?", help="Deprecated legacy argument; files are never moved")
    parser.add_argument("--inventory", required=True, type=Path, help="Inventory JSON produced by a source scanner")
    parser.add_argument("--registry", type=Path, default=Path("kova_file_inventory/status_registry.json"))
    parser.add_argument("--dry-run", action="store_true", help="Print the registry without writing it")
    parser.add_argument("--execute", action="store_true", help="Deprecated; metadata output is always non-destructive")
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    if not isinstance(inventory, list):
        parser.error("inventory must be a JSON array")

    rows = build_registry(inventory)
    if args.dry_run:
        print(json.dumps(rows, indent=2))
    else:
        write_registry(rows, args.registry)
        print(f"Wrote {len(rows)} metadata records to {args.registry}")
    if args.base_path or args.execute:
        print("Legacy move/folder arguments were ignored; governed files were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
