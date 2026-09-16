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


def default_private_dir() -> Path:
    override = (os.environ.get("KOVA_PRIVATE_STATE_DIR") or "").strip()
    if override:
        return Path(override).expanduser()
    xdg_data_home = (os.environ.get("XDG_DATA_HOME") or "").strip()
    if xdg_data_home:
        return Path(xdg_data_home).expanduser() / "kova" / "private"
    return Path.home() / ".local" / "share" / "kova" / "private"


DEFAULT_PRIVATE_DIR = default_private_dir()
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
    if explicit in LIFECYCLE_COLORS and (explicit != "FINAL" or file_info.get("verified") is True):
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
    revision = file_info.get("revision_id")
    if not revision:
        raise ValueError(f"inventory item needs version evidence for {source_identity(file_info)}")
    raw = f"{file_info.get('source', 'unknown')}|{source_identity(file_info)}|{revision}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def exact_duplicate_key(file_info: dict[str, Any]) -> str | None:
    populate_version_metadata(file_info)
    content_hash = (
        file_info.get("sha256")
        or file_info.get("md5Checksum")
        or file_info.get("content_hash")
        or file_info.get("blob_sha")
    )
    return f"hash:{content_hash}" if content_hash else None


def likely_duplicate_key(file_info: dict[str, Any], title: str) -> str:
    normalized = re.sub(r"\W+", "", title).lower()
    return f"title-size:{normalized}:{file_info.get('size', '')}"


def canonical_rank(file_info: dict[str, Any]) -> tuple[int, int, int, str, str]:
    """Deterministically prefer explicit/verified/current items, then a stable ID."""
    lifecycle = lifecycle_for(file_info)[0]
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


def version_evidence_for(file_info: dict[str, Any]) -> dict[str, Any]:
    evidence = {
        "source": file_info.get("source"),
        "revision_id": file_info.get("revision_id"),
        "headRevisionId": file_info.get("headRevisionId"),
        "md5Checksum": file_info.get("md5Checksum"),
        "sha256": file_info.get("sha256"),
        "content_hash": file_info.get("content_hash"),
        "version": file_info.get("version"),
        "modified": file_info.get("modified") or file_info.get("modifiedTime"),
    }
    return {key: value for key, value in evidence.items() if value not in (None, "")}


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
    likely_groups_with_missing_hash = {
        key
        for key, indexes in likely_groups.items()
        if len(indexes) > 1 and any(exact_duplicate_key(items[idx]) is None for idx in indexes)
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
        if likely in likely_groups_with_missing_hash and likely_canonical is not None and likely_canonical != index:
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
                "version_evidence": version_evidence_for(file_info),
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


def merge_history(
    current: list[dict[str, Any]],
    previous: list[dict[str, Any]],
    *,
    full_snapshot: bool = False,
) -> list[dict[str, Any]]:
    """Retain exact-version history and prior decisions across scanner runs."""
    if full_snapshot:
        merged = {row["version_key"]: {**row, "observed_current": False} for row in previous}
    else:
        merged = {row["version_key"]: dict(row) for row in previous}
    for row in current:
        prior = merged.get(row["version_key"], {})
        combined = {**prior, **row}
        prior_verification = prior.get("verification", {})
        current_verification = row.get("verification", {})
        preserve_prior_classification = prior_verification.get("verified") and not any(
            current_verification.get(field) not in (None, "")
            for field in ("evidence", "reference", "checked_at")
        )
        if prior_verification.get("verified") and not current_verification.get("verified"):
            combined["verification"] = prior_verification
        else:
            combined["verification"] = {
                **prior_verification,
                **{
                    key: value
                    for key, value in current_verification.items()
                    if key == "verified" or value not in (None, "")
                },
            }
        if preserve_prior_classification:
            for field in ("area", "topic", "subtopic", "file_type", "content_origin", "record_role"):
                if field in prior:
                    combined[field] = prior[field]
        combined["version_evidence"] = {
            **prior.get("version_evidence", {}),
            **{
                key: value
                for key, value in row.get("version_evidence", {}).items()
                if value not in (None, "")
            },
        }
        if row.get("superseded_by") is None and prior.get("superseded_by") is not None:
            combined["superseded_by"] = prior["superseded_by"]
        if prior.get("flags"):
            combined["flags"] = list(dict.fromkeys([*prior.get("flags", []), *row.get("flags", [])]))
            combined["flag_colors"] = [FLAG_COLORS[flag] for flag in combined["flags"]]
        for field, fallback_values in (
            ("area", {"Other"}),
            ("topic", {"KOVA Reference"}),
            ("subtopic", {None, ""}),
            ("file_type", {"Other"}),
            ("content_origin", {"Unknown"}),
            ("record_role", {"Unknown"}),
        ):
            if field in prior and prior.get(field) not in fallback_values and combined.get(field) in fallback_values:
                combined[field] = prior[field]
        if prior.get("canonical_version_key") and not row.get("canonical_version_key"):
            combined["canonical_version_key"] = prior["canonical_version_key"]
        if prior.get("possible_duplicate_of") and not row.get("possible_duplicate_of"):
            combined["possible_duplicate_of"] = prior["possible_duplicate_of"]
        if (
            prior.get("lifecycle") in ("ACTIVE", "FINAL", "ARCHIVE")
            and row.get("lifecycle") == "REVIEW"
            and row.get("decision_reason") in {"Needs current verification", "Possible duplicate; content hash unavailable"}
        ):
            combined["lifecycle"] = prior["lifecycle"]
            combined["lifecycle_color"] = LIFECYCLE_COLORS[prior["lifecycle"]]
            combined["decision_reason"] = prior.get("decision_reason", combined["decision_reason"])
        merged[row["version_key"]] = combined
    return sorted(merged.values(), key=lambda row: row["version_key"])


def reclassify_exact_duplicates(
    rows: list[dict[str, Any]], historical_current: set[str]
) -> list[dict[str, Any]]:
    """Reapply exact duplicate flags using current and previously-current hash evidence."""
    candidate_indexes = [
        index
        for index, row in enumerate(rows)
        if row.get("observed_current") or row.get("version_key") in historical_current
    ]
    exact_groups: dict[str, list[int]] = {}
    for index in candidate_indexes:
        version_evidence = rows[index].get("version_evidence", {})
        content_hash = (
            version_evidence.get("sha256")
            or version_evidence.get("md5Checksum")
            or version_evidence.get("content_hash")
        )
        if content_hash:
            exact_groups.setdefault(f"hash:{content_hash}", []).append(index)
    for indexes in exact_groups.values():
        if len(indexes) < 2:
            continue
        canonical = max(
            indexes,
            key=lambda idx: (
                rows[idx].get("verification", {}).get("verified") is True,
                {"FINAL": 3, "ACTIVE": 2, "REVIEW": 1, "ARCHIVE": 0}.get(rows[idx].get("lifecycle"), 0),
                str(rows[idx].get("version_evidence", {}).get("modified") or ""),
                str(rows[idx].get("source_id") or ""),
            ),
        )
        for index in indexes:
            if index == canonical:
                continue
            if "DUPLICATE" not in rows[index]["flags"]:
                rows[index]["flags"].append("DUPLICATE")
                rows[index]["flag_colors"] = [FLAG_COLORS[flag] for flag in rows[index]["flags"]]
            rows[index]["canonical_version_key"] = rows[canonical]["version_key"]
    return rows


def atomic_write_private(output: Path, payload: dict[str, Any]) -> None:
    """Atomically publish private JSON with user-only filesystem permissions."""
    parent = output.parent
    if parent.exists():
        if parent.stat().st_mode & 0o777 != 0o700:
            raise PermissionError(f"refusing to write private data under non-private directory: {parent}")
    else:
        parent.mkdir(mode=0o700, parents=True, exist_ok=True)
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
    historical_current = {
        row["version_key"] for row in previous if row.get("observed_current") and row.get("version_key")
    }
    items = reclassify_exact_duplicates(
        merge_history(rows, previous, full_snapshot=not rows),
        historical_current,
    )
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
    parser.add_argument("--inventory", type=Path, help="Inventory JSON produced by a source scanner")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Print the registry without writing it")
    parser.add_argument("--execute", action="store_true", help="Deprecated; output is always non-destructive")
    args = parser.parse_args()

    if args.inventory is None:
        if args.base_path or args.execute:
            print("Legacy move/folder arguments were ignored; governed files were not changed.")
            return 0
        parser.error("--inventory is required unless using legacy compatibility arguments")

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
