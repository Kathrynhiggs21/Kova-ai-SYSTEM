#!/usr/bin/env python3
"""Build KOVA's non-destructive metadata registry.

The registry describes governed items; it never moves, renames, overwrites, or
deletes them. Labels stay deliberately small: area, topic, lifecycle, and flags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_POLICY_PATH = Path(
    os.environ.get("KOVA_AUTOMATION_POLICY_PATH", PROJECT_DIR / "config" / "automation_policy.v1.json")
)
DEFAULT_PRIVATE_DIR = Path(
    os.environ.get(
        "KOVA_PRIVATE_STATE_DIR",
        Path.home() / ".local" / "share" / "kova" / "private",
    )
)
DEFAULT_REGISTRY_PATH = DEFAULT_PRIVATE_DIR / "status_registry.json"


def load_policy(path: Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    """Load and validate the single machine-readable labeling policy."""
    policy = json.loads(path.read_text(encoding="utf-8"))
    required = ("lifecycle", "flags", "areas", "topics", "content_origins", "record_roles")
    missing = [key for key in required if key not in policy]
    if missing:
        raise ValueError(f"automation policy missing: {', '.join(missing)}")
    return policy


POLICY = load_policy()
LIFECYCLE_COLORS = POLICY["lifecycle"]
FLAG_COLORS = POLICY["flags"]
AREAS = tuple(POLICY["areas"])
TOPICS = POLICY["topics"]
CONTENT_ORIGINS = tuple(POLICY["content_origins"])
RECORD_ROLES = tuple(POLICY["record_roles"])


SENSITIVE_MARKERS = (
    "credential",
    "password",
    "private key",
    "api key",
    "access token",
    "refresh token",
    "config url",
    "secret",
    "medical",
    "tax",
)

NOISE_WORDS = {"copy", "document", "file", "new", "old", "untitled", "unknown"}


def normalized_words(value: str) -> str:
    """Normalize separators while retaining word boundaries."""
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def contains_phrase(haystack: str, phrase: str) -> bool:
    """Match whole tokens/phrases so `api` does not match `capital`."""
    words = normalized_words(haystack)
    target = normalized_words(phrase)
    return bool(target and re.search(rf"(?:^| ){re.escape(target)}(?: |$)", words))


def canonicalize_kova(value: str) -> str:
    """Normalize common KOVA spellings without changing the source file."""
    value = re.sub(r"\b(?:k9va|kiva|kova)[-_ ]?os\b", "KOVA Operating System", value, flags=re.I)
    value = re.sub(r"\b(?:k9va|kiva|kova)[-_ ]?ai\b", "KOVA AI", value, flags=re.I)
    return re.sub(r"\b(?:k9va|kiva|kova)\b", "KOVA", value, flags=re.I)


def short_title(file_info: dict[str, Any], limit: int = 80) -> str:
    """Return a readable display title while retaining the source name."""
    explicit = file_info.get("suggested_title") or file_info.get("title")
    raw = str(explicit or Path(str(file_info.get("name", "KOVA Item"))).stem)
    raw = re.sub(r"[_-]+", " ", raw)
    raw = canonicalize_kova(raw)
    raw = re.sub(r"\s*\(\d+\)\s*$", "", raw)
    raw = re.sub(r"(?:[-_ ]+(?:copy|final|draft|v\d+(?:\.\d+)*))+\s*$", "", raw, flags=re.I)
    words = [word for word in raw.split() if word.lower() not in NOISE_WORDS]
    title = " ".join(words).strip() or "KOVA Item"
    return title if len(title) <= limit else title[: limit - 1].rstrip() + "…"


def area_for(file_info: dict[str, Any]) -> str:
    explicit = str(file_info.get("area") or "")
    normalized_areas = {value.casefold(): value for value in AREAS}
    if explicit.casefold() in normalized_areas:
        return normalized_areas[explicit.casefold()]
    haystack = " ".join(str(file_info.get(key, "")) for key in ("name", "title", "description"))
    if contains_phrase(haystack, "Reagan"):
        return "Reagan"
    if any(contains_phrase(haystack, word) for word in ("KOVA", "K9VA", "Kiva")):
        return "KOVA"
    return "Other"


def topic_for(file_info: dict[str, Any]) -> str:
    explicit = str(file_info.get("topic") or "")
    if explicit in TOPICS:
        return explicit
    haystack = " ".join(
        str(file_info.get(key, "")) for key in ("name", "title", "description", "path")
    )
    for topic, keywords in TOPICS.items():
        if any(contains_phrase(haystack, keyword) for keyword in keywords):
            return topic
    return "KOVA Reference"


def file_type_for(file_info: dict[str, Any]) -> str:
    explicit = file_info.get("file_type")
    if explicit:
        return str(explicit)
    mime = str(file_info.get("mime_type") or file_info.get("mimeType") or "").lower()
    name = str(file_info.get("name") or "").lower()
    if "folder" in mime:
        return "Folder"
    if "spreadsheet" in mime or name.endswith((".xlsx", ".xls", ".csv")):
        return "Spreadsheet"
    if "presentation" in mime or name.endswith((".pptx", ".ppt")):
        return "Presentation"
    if mime.startswith("image/"):
        return "Image"
    if mime.startswith("video/"):
        return "Video"
    if mime.startswith("audio/"):
        return "Audio"
    if name.endswith((".zip", ".tar", ".gz", ".7z")):
        return "Archive"
    if name.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".json", ".yml", ".yaml")):
        return "Code"
    if name.endswith((".doc", ".docx", ".pdf", ".txt", ".md")) or "document" in mime:
        return "Document"
    return "Other"


def content_origin_for(file_info: dict[str, Any]) -> str:
    origin = str(file_info.get("content_origin") or "Unknown")
    normalized = {value.casefold(): value for value in CONTENT_ORIGINS}
    return normalized.get(origin.casefold(), "Unknown")


def record_role_for(file_info: dict[str, Any]) -> str:
    """Classify a chat/reference as an input type, never infer approval from prose."""
    role = str(file_info.get("record_role") or "Unknown")
    normalized = {value.casefold(): value for value in RECORD_ROLES}
    return normalized.get(role.casefold(), "Unknown")


def sensitivity_for(file_info: dict[str, Any]) -> tuple[str, str]:
    """Return SENSITIVE, CLEAR, or UNKNOWN plus the evidence basis."""
    if file_info.get("sensitive") is True:
        return "SENSITIVE", "Explicit source flag"
    haystack = " ".join(
        str(file_info.get(key, "")) for key in ("name", "title", "description", "text")
    )
    if any(contains_phrase(haystack, marker) for marker in SENSITIVE_MARKERS):
        return "SENSITIVE", "Metadata/content marker"
    if file_info.get("sensitivity_checked") is True or file_info.get("content_inspected") is True:
        return "CLEAR", "Inspected with no sensitive marker"
    return "UNKNOWN", "Content not inspected"


def lifecycle_for(file_info: dict[str, Any]) -> tuple[str, str]:
    """Classify lifecycle conservatively and explain the decision."""
    explicit = str(file_info.get("lifecycle") or file_info.get("status") or "").upper()
    if explicit == "UNREVIEWED":
        explicit = "REVIEW"
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
            if 0 <= age_days <= 90 and topic_for(file_info) != "KOVA Reference":
                return "ACTIVE", "Recent relevant work"
        except ValueError:
            pass
    return "REVIEW", "Needs current verification"


def source_identity(file_info: dict[str, Any]) -> str:
    identity = (
        file_info.get("source_identity")
        or file_info.get("id")
        or file_info.get("file_id")
        or file_info.get("path")
        or file_info.get("web_link")
        or file_info.get("url")
    )
    if not identity:
        raise ValueError("inventory item needs a stable source identity, ID, path, or URL")
    return str(identity)


def populate_version_metadata(file_info: dict[str, Any]) -> None:
    """Populate revision/content metadata before deriving canonical identity."""
    local_path = file_info.get("path")
    if local_path and not file_info.get("sha256"):
        candidate = Path(str(local_path))
        if candidate.is_file():
            digest = hashlib.sha256()
            with candidate.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            file_info["sha256"] = digest.hexdigest()
    if not file_info.get("content_hash"):
        file_info["content_hash"] = file_info.get("sha256") or file_info.get("md5Checksum")
    if not file_info.get("revision_id"):
        for key in ("headRevisionId", "blob_sha", "sha256", "md5Checksum", "content_hash", "version", "modified", "modifiedTime"):
            if file_info.get(key):
                file_info["revision_id"] = str(file_info[key])
                break


def version_key(file_info: dict[str, Any]) -> str:
    """Key an exact source version; hashes alone are duplicate evidence, not identity."""
    if file_info.get("version_key"):
        return str(file_info["version_key"])
    populate_version_metadata(file_info)
    revision = str(file_info.get("revision_id") or "unversioned")
    raw = f"{file_info.get('source', 'unknown')}|{source_identity(file_info)}|{revision}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def exact_duplicate_key(file_info: dict[str, Any]) -> str | None:
    content_hash = file_info.get("sha256") or file_info.get("md5Checksum") or file_info.get("content_hash")
    return f"hash:{content_hash}" if content_hash else None


def likely_duplicate_key(file_info: dict[str, Any], title: str) -> str:
    normalized = re.sub(r"\W+", "", title).lower()
    return f"title-size:{normalized}:{file_info.get('size', '')}"


def canonical_rank(file_info: dict[str, Any]) -> tuple[int, int, int, str, str]:
    """Deterministically prefer explicit/verified/current items, then a stable ID."""
    lifecycle = str(file_info.get("lifecycle") or file_info.get("status") or "").upper()
    if lifecycle == "UNREVIEWED":
        lifecycle = "REVIEW"
    explicit_rank = {"FINAL": 3, "ACTIVE": 2, "REVIEW": 1, "ARCHIVE": 0}.get(lifecycle, 0)
    modified = str(file_info.get("modified") or file_info.get("modifiedTime") or "")
    return (
        1 if file_info.get("canonical") is True else 0,
        1 if file_info.get("verified") is True else 0,
        explicit_rank,
        modified,
        source_identity(file_info),
    )


def verification_for(file_info: dict[str, Any]) -> dict[str, Any]:
    return {
        "verified": file_info.get("verified") is True,
        "source_status": file_info.get("lifecycle") or file_info.get("status"),
        "evidence": file_info.get("verification_evidence") or file_info.get("evidence"),
        "reference": file_info.get("verification_reference") or file_info.get("decision_reference"),
        "checked_at": file_info.get("verified_at") or file_info.get("checked_at"),
    }


def build_registry(inventory: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    items = [dict(item) for item in inventory]
    for item in items:
        populate_version_metadata(item)
    exact_groups: dict[str, list[int]] = {}
    likely_groups: dict[str, list[int]] = {}
    titles: list[str] = []
    for index, item in enumerate(items):
        title = short_title(item)
        titles.append(title)
        exact = exact_duplicate_key(item)
        if exact:
            exact_groups.setdefault(exact, []).append(index)
        likely_groups.setdefault(likely_duplicate_key(item, title), []).append(index)

    canonical_indexes = {
        key: max(indexes, key=lambda idx: canonical_rank(items[idx]))
        for key, indexes in exact_groups.items()
        if len(indexes) > 1
    }
    likely_canonical_indexes = {
        key: max(indexes, key=lambda idx: canonical_rank(items[idx]))
        for key, indexes in likely_groups.items()
        if len(indexes) > 1
    }
    version_keys = [version_key(item) for item in items]
    rows: list[dict[str, Any]] = []

    for index, file_info in enumerate(items):
        title = titles[index]
        lifecycle, reason = lifecycle_for(file_info)
        sensitivity, sensitivity_basis = sensitivity_for(file_info)
        flags = ["SENSITIVE"] if sensitivity == "SENSITIVE" else []
        exact = exact_duplicate_key(file_info)
        exact_canonical = canonical_indexes.get(exact) if exact else None
        if exact_canonical is not None and exact_canonical != index:
            flags.append("DUPLICATE")
        likely = likely_duplicate_key(file_info, title)
        likely_canonical = likely_canonical_indexes.get(likely)
        possible_duplicate_of = None
        if exact is None and likely_canonical is not None and likely_canonical != index:
            possible_duplicate_of = version_keys[likely_canonical]
            if lifecycle not in ("FINAL", "ARCHIVE"):
                lifecycle, reason = "REVIEW", "Possible duplicate; content hash unavailable"

        rows.append(
            {
                "version_key": version_keys[index],
                "source_name": file_info.get("name"),
                "display_title": title,
                "area": area_for(file_info),
                "topic": topic_for(file_info),
                "subtopic": file_info.get("subtopic") or file_info.get("suggested_subtopic"),
                "file_type": file_type_for(file_info),
                "content_origin": content_origin_for(file_info),
                "record_role": record_role_for(file_info),
                "lifecycle": lifecycle,
                "lifecycle_color": LIFECYCLE_COLORS[lifecycle],
                "flags": flags,
                "flag_colors": [FLAG_COLORS[flag] for flag in flags],
                "sensitivity": sensitivity,
                "sensitivity_basis": sensitivity_basis,
                "decision_reason": reason,
                "verification": verification_for(file_info),
                "source_id": source_identity(file_info),
                "source_link": file_info.get("web_link") or file_info.get("url"),
                "source_chat_id": file_info.get("chat_id") or file_info.get("agent_id"),
                "canonical_version_key": (
                    version_keys[exact_canonical]
                    if exact_canonical is not None and exact_canonical != index
                    else None
                ),
                "possible_duplicate_of": possible_duplicate_of,
                "superseded_by": file_info.get("superseded_by"),
                "observed_current": True,
            }
        )
    return rows


def merge_history(current: list[dict[str, Any]], previous: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retain exact-version history and prior decisions across scanner runs."""
    merged = {row["version_key"]: {**row, "observed_current": False} for row in previous}
    for row in current:
        prior = merged.get(row["version_key"], {})
        combined = {**prior, **row}
        if row.get("superseded_by") is None and prior.get("superseded_by") is not None:
            combined["superseded_by"] = prior["superseded_by"]
        if prior.get("verification", {}).get("verified") and not row.get("verification", {}).get("verified"):
            combined["verification"] = prior["verification"]
            if prior.get("lifecycle") in ("ACTIVE", "FINAL", "ARCHIVE"):
                combined["lifecycle"] = prior["lifecycle"]
                combined["lifecycle_color"] = LIFECYCLE_COLORS[prior["lifecycle"]]
                combined["decision_reason"] = prior.get("decision_reason", combined["decision_reason"])
        merged[row["version_key"]] = combined
    return sorted(merged.values(), key=lambda row: row["version_key"])


def atomic_write_private(output: Path, payload: dict[str, Any]) -> None:
    """Atomically publish private JSON with user-only filesystem permissions."""
    parent = output.parent
    created_parent = not parent.exists()
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if created_parent:
        os.chmod(parent, 0o700)
    serialized = json.dumps(payload, indent=2) + "\n"
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_name = temp_file.name
            os.chmod(temp_name, 0o600)
            temp_file.write(serialized)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_name, output)
        os.chmod(output, 0o600)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def write_registry(rows: list[dict[str, Any]], output: Path) -> int:
    previous: list[dict[str, Any]] = []
    if output.exists():
        payload = json.loads(output.read_text(encoding="utf-8"))
        previous = payload.get("items", []) if isinstance(payload, dict) else []
    items = merge_history(rows, previous)
    generated_at = datetime.now(timezone.utc).isoformat()
    exceptions = [
        row for row in items
        if row.get("lifecycle") == "REVIEW"
        or row.get("sensitivity") in ("SENSITIVE", "UNKNOWN")
        or row.get("flags")
        or row.get("possible_duplicate_of")
    ]
    exception_payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "exception_count": len(exceptions),
        "items": exceptions,
    }
    payload = {
        "schema_version": 2,
        "generated_at": generated_at,
        "organization_mode": "metadata-first",
        "physical_changes": False,
        "items": items,
        "exceptions": exception_payload,
    }
    atomic_write_private(output, payload)
    exception_output = output.with_name(f"{output.stem}.exceptions.json")
    atomic_write_private(exception_output, exception_payload)
    return len(exceptions)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build KOVA's non-destructive file status registry")
    parser.add_argument("base_path", nargs="?", help="Deprecated legacy argument; files are never moved")
    parser.add_argument("--inventory", required=True, type=Path, help="Inventory JSON produced by a source scanner")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Print the registry without writing it")
    parser.add_argument("--execute", action="store_true", help="Deprecated; output is always non-destructive")
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    if not isinstance(inventory, list):
        parser.error("inventory must be a JSON array")
    rows = build_registry(inventory)
    if args.dry_run:
        print(json.dumps(rows, indent=2))
    else:
        exception_count = write_registry(rows, args.registry)
        print(f"Wrote {len(rows)} current metadata records to {args.registry}")
        print(f"Wrote {exception_count} review exceptions to {args.registry.with_name(args.registry.stem + '.exceptions.json')}")
    if args.base_path or args.execute:
        print("Legacy move/folder arguments were ignored; governed files were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
