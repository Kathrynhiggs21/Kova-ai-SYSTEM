#!/usr/bin/env python3
"""Build KOVA's non-destructive metadata registry.

The registry describes governed items; it never moves, renames, overwrites, or
deletes them. Labels stay deliberately small: area, topic, lifecycle, and flags.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from scripts.private_state import private_directory, read_private_text, read_text_at, validate_unlinked_path, write_private_text, write_text_at
except ModuleNotFoundError:
    from private_state import private_directory, read_private_text, read_text_at, validate_unlinked_path, write_private_text, write_text_at


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
    "credentials",
    "password",
    "passwords",
    "private key",
    "api key",
    "api keys",
    "access token",
    "refresh token",
    "config url",
    "secret",
    "secrets",
    "medical",
    "tax",
)

PLACEHOLDER_TITLES = {"untitled", "unknown", "new file", "new document", "untitled file", "untitled document"}


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
    raw = re.sub(r"^\s*\d+(?:[._-]\d+)*[._\s-]+(?=[A-Za-z])", "", raw)
    raw = re.sub(r"[_-]+", " ", raw)
    raw = canonicalize_kova(raw)
    raw = re.sub(r"\s*\(\d+\)\s*$", "", raw)
    raw = re.sub(r"(?:[-_ ]+(?:copy|final|draft|v\d+(?:\.\d+)*))+\s*$", "", raw, flags=re.I)
    title = raw.strip()
    if not title or title.casefold() in PLACEHOLDER_TITLES:
        title = "KOVA Item"
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
    if file_info.get("superseded_by"):
        return "ARCHIVE", "Known replacement recorded"
    explicit = str(file_info.get("lifecycle") or file_info.get("status") or "").upper()
    if explicit == "UNREVIEWED":
        explicit = "REVIEW"
    if explicit == "FINAL" and file_info.get("verified") is not True:
        return "REVIEW", "Final status requires verification"
    if explicit in LIFECYCLE_COLORS and (explicit != "FINAL" or file_info.get("verified") is True):
        return explicit, "Explicit source status"
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
    source = str(file_info.get("source") or "").casefold()
    path = file_info.get("path")
    if source == "local" and path:
        candidate = Path(str(path)).expanduser()
        if not candidate.is_absolute():
            raise ValueError("local inventories require absolute source paths")
        return str(candidate.resolve())
    if source == "github" and path:
        repository = file_info.get("repository_full_name") or file_info.get("repository") or file_info.get("repo")
        if not isinstance(repository, str) or not re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
            raise ValueError("GitHub file paths require a repository owner/name")
        parts = str(path).replace("\\", "/").split("/")
        if ".." in parts:
            raise ValueError("GitHub source paths must be canonical repository paths")
        return repository.casefold() + ":" + "/".join(part for part in parts if part and part != ".")
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


class InventorySnapshot(dict):
    """Internal per-build hash cache; JSON fields cannot supply this cache."""
    def __init__(self, item: dict[str, Any], local_hashes: dict[str, str]):
        super().__init__(item)
        self.local_hashes = local_hashes


def supported_revision(file_info: dict[str, Any]) -> str | None:
    evidence_fields = ("sha256", "headRevisionId", "blob_sha", "md5Checksum", "content_hash", "version")
    revision = next((str(file_info[key]).lower() if key in {"sha256", "md5Checksum", "blob_sha"} else str(file_info[key]) for key in evidence_fields if file_info.get(key)), None)
    if str(file_info.get("source") or "").casefold() == "google_drive" and file_info.get("version"):
        return json.dumps(["drive-version", str(file_info["version"]), revision], separators=(",", ":"))
    return revision


def populate_version_metadata(file_info: dict[str, Any]) -> None:
    """Populate revision/content metadata before deriving canonical identity."""
    local_path = file_info.get("path")
    if local_path and str(file_info.get("source") or "").casefold() == "local":
        candidate = Path(str(local_path))
        if candidate.is_file():
            cache = file_info.local_hashes if isinstance(file_info, InventorySnapshot) else {}
            cache_key = str(candidate.absolute())
            if cache_key not in cache:
                digest = hashlib.sha256()
                with candidate.open("rb") as source:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        digest.update(chunk)
                cache[cache_key] = digest.hexdigest()
            file_info["sha256"] = cache[cache_key]
    if not file_info.get("content_hash"):
        file_info["content_hash"] = file_info.get("sha256") or file_info.get("md5Checksum")
    revision = supported_revision(file_info)
    supplied = file_info.get("revision_id")
    digest_revision = next((field for field in ("sha256", "headRevisionId", "blob_sha", "md5Checksum", "content_hash", "version") if file_info.get(field)), None) in {"sha256", "blob_sha", "md5Checksum"}
    if supplied and (revision is None or (str(supplied) != revision and not (digest_revision and str(supplied).casefold() == revision.casefold()))):
        raise ValueError("supplied revision must match supported version evidence")
    if revision is not None:
        file_info["revision_id"] = revision


def version_key(file_info: dict[str, Any]) -> str:
    """Key an exact source version; hashes alone are duplicate evidence, not identity."""
    source = str(file_info.get("source") or "").strip().casefold()
    if not re.fullmatch(r"[a-z][a-z0-9_.-]*", source) or source == "unknown":
        raise ValueError("inventory item needs an explicit source namespace")
    file_info["source"] = source
    populate_version_metadata(file_info)
    revision = file_info.get("revision_id")
    if not revision:
        raise ValueError("inventory item needs supported version evidence")
    raw = json.dumps([source, source_identity(file_info), str(revision)], ensure_ascii=False, separators=(",", ":"))
    derived = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if file_info.get("version_key") and str(file_info["version_key"]) != derived:
        raise ValueError("supplied version key does not match source and revision evidence")
    return derived


def exact_duplicate_key(file_info: dict[str, Any]) -> str | None:
    populate_version_metadata(file_info)
    digest = digest_evidence(file_info)
    return json.dumps(digest, separators=(",", ":")) if digest else None


def digest_evidence(evidence: dict[str, Any]) -> tuple[str, str] | None:
    for field, algorithm in (("sha256", "sha256"), ("md5Checksum", "md5"), ("blob_sha", "git-blob-sha1"), ("content_hash", "opaque-content-hash")):
        if evidence.get(field):
            value = str(evidence[field])
            return algorithm, value.lower() if field != "content_hash" else value
    return None


def needs_hash_review(evidences: Iterable[dict[str, Any]]) -> bool:
    digests = [digest_evidence(evidence) for evidence in evidences]
    return any(digest is None for digest in digests) or len({digest[0] for digest in digests if digest}) > 1


def likely_duplicate_key(file_info: dict[str, Any], title: str) -> str:
    normalized = re.sub(r"\W+", "", title).lower()
    return f"title-size:{normalized}:{file_info.get('size', '')}"


def comparable_digest_conflict(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """A shared digest algorithm with different values proves two files differ."""
    for field in ("sha256", "md5Checksum", "blob_sha", "content_hash"):
        if field == "content_hash" and (any(left.get(k) for k in ("sha256", "md5Checksum", "blob_sha")) or any(right.get(k) for k in ("sha256", "md5Checksum", "blob_sha"))):
            continue
        if left.get(field) and right.get(field):
            lhs, rhs = str(left[field]), str(right[field])
            if (lhs != rhs) if field == "content_hash" else (lhs.casefold() != rhs.casefold()):
                return True
    return False


def modified_instant(value: Any) -> float:
    """Compare instants rather than ISO strings with different UTC offsets."""
    try:
        when = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        return when.timestamp()
    except (ValueError, OverflowError):
        return float("-inf")


def selection_rank(canonical: Any, verified: Any, lifecycle: Any, modified: Any, identity: Any) -> tuple[int, int, int, float, str]:
    return (
        1 if canonical is True else 0,
        1 if verified is True else 0,
        {"FINAL": 3, "ACTIVE": 2, "REVIEW": 1, "ARCHIVE": 0}.get(lifecycle, 0),
        modified_instant(modified),
        str(identity),
    )


def canonical_rank(file_info: dict[str, Any]) -> tuple[int, int, int, float, str]:
    """Deterministically prefer explicit/verified/current items, then a stable ID."""
    lifecycle = lifecycle_for(file_info)[0]
    return selection_rank(
        file_info.get("canonical"), file_info.get("verified"), lifecycle,
        file_info.get("modified") or file_info.get("modifiedTime"),
        version_key(file_info),
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
        "blob_sha": file_info.get("blob_sha"),
        "version": file_info.get("version"),
        "modified": file_info.get("modified") or file_info.get("modifiedTime"),
    }
    return {key: value for key, value in evidence.items() if value not in (None, "")}


def build_registry(inventory: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    local_hashes: dict[str, str] = {}
    items = [InventorySnapshot(item, local_hashes) for item in inventory]
    for item in items:
        populate_version_metadata(item)
    version_keys = [version_key(item) for item in items]
    identities = [(item["source"], source_identity(item)) for item in items]
    if len(set(identities)) != len(identities):
        raise ValueError("inventory must contain only one current version per source identity")
    exact_groups: dict[str, list[int]] = {}
    likely_groups: dict[str, list[int]] = {}
    titles: list[str] = []
    for index, item in enumerate(items):
        title = short_title(item)
        titles.append(title)
        exact = exact_duplicate_key(item)
        if exact:
            exact_groups.setdefault(exact, []).append(index)
        likely_groups.setdefault(likely_duplicate_key(item, short_title(item, limit=10_000)), []).append(index)

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
        if len(indexes) > 1 and needs_hash_review(items[idx] for idx in indexes)
    }
    rows: list[dict[str, Any]] = []

    for index, file_info in enumerate(items):
        title = titles[index]
        lifecycle, reason = lifecycle_for(file_info)
        source_lifecycle, source_reason = lifecycle, reason
        sensitivity, sensitivity_basis = sensitivity_for(file_info)
        flags = ["SENSITIVE"] if sensitivity == "SENSITIVE" else []
        exact = exact_duplicate_key(file_info)
        exact_canonical = canonical_indexes.get(exact) if exact else None
        if exact_canonical is not None and exact_canonical != index:
            flags.append("DUPLICATE")
        likely = likely_duplicate_key(file_info, short_title(file_info, limit=10_000))
        likely_canonical = likely_canonical_indexes.get(likely)
        possible_duplicate_of = None
        if likely in likely_groups_with_missing_hash and likely_canonical is not None and likely_canonical != index:
            possible_duplicate_of = version_keys[likely_canonical]
            if lifecycle not in ("FINAL", "ARCHIVE"):
                lifecycle, reason = "REVIEW", "Possible duplicate; comparable content hash unavailable"

        rows.append(
            {
                "version_key": version_keys[index],
                "source_name": file_info.get("name"),
                "source_size": file_info.get("size", ""),
                "duplicate_title": short_title(file_info, limit=10_000),
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
                "source_lifecycle": source_lifecycle,
                "source_decision_reason": source_reason,
                "verification": verification_for(file_info),
                "canonical": file_info.get("canonical") if isinstance(file_info.get("canonical"), bool) else None,
                "unresolved_review": file_info.get("unresolved_review") is True,
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
    snapshot_sources: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Retain exact-version history and prior decisions across scanner runs."""
    # Upgrade earlier delimiter-based keys without losing decisions or pointers.
    previous = [dict(row) for row in previous]
    key_updates = {}
    for row in previous:
        evidence = row.get("version_evidence", {})
        source = str(evidence.get("source") or "").strip().casefold()
        revision = supported_revision({**evidence, "source": source})
        if row.get("source_id") and revision and re.fullmatch(r"[a-z][a-z0-9_.-]*", source) and source != "unknown":
            raw = json.dumps([source, str(row["source_id"]), str(revision)], ensure_ascii=False, separators=(",", ":"))
            new_key = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            key_updates[row["version_key"]] = new_key
            row["version_key"] = new_key
    for row in previous:
        for field in ("canonical_version_key", "possible_duplicate_of"):
            if row.get(field) in key_updates:
                row[field] = key_updates[row[field]]
    if full_snapshot:
        merged = {
            row["version_key"]: {
                **row,
                "observed_current": False if snapshot_sources is None or row.get("version_evidence", {}).get("source") in snapshot_sources else row.get("observed_current", False),
            }
            for row in previous
        }
    else:
        merged = {row["version_key"]: dict(row) for row in previous}
    for row in current:
        # A newer observed version replaces current status, while preserving history.
        identity = (row.get("version_evidence", {}).get("source"), row.get("source_id"))
        # Choose the current version after merging; inventory iteration order is not evidence.
        prior = merged.get(row["version_key"], {})
        combined = {**prior, **row}
        if row.get("canonical") is None and prior.get("canonical") is not None:
            combined["canonical"] = prior["canonical"]
        prior_verification = prior.get("verification", {})
        current_verification = row.get("verification", {})
        preserve_prior_classification = prior_verification.get("verified") and (
            not current_verification.get("verified") or not any(
                current_verification.get(field) not in (None, "")
                for field in ("evidence", "reference")
            )
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
            for field in ("area", "topic", "subtopic", "file_type", "content_origin", "record_role", "lifecycle", "lifecycle_color", "decision_reason", "canonical", "unresolved_review"):
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
        if preserve_prior_classification:
            combined["flags"] = list(prior.get("flags", []))
        # Sensitivity flags describe the current classification, not history.
        if row.get("sensitivity") == "UNKNOWN" and prior.get("sensitivity") in {"CLEAR", "SENSITIVE"}:
            combined["sensitivity"] = prior["sensitivity"]
            combined["sensitivity_basis"] = prior.get("sensitivity_basis")
        if combined.get("sensitivity") in {"CLEAR", "SENSITIVE"}:
            combined["flags"] = [flag for flag in combined.get("flags", []) if flag != "SENSITIVE"]
            if combined["sensitivity"] == "SENSITIVE":
                combined["flags"].append("SENSITIVE")
        combined["flag_colors"] = [FLAG_COLORS[flag] for flag in combined.get("flags", [])]
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
        if prior.get("possible_duplicate_of") and "possible_duplicate_of" not in row:
            combined["possible_duplicate_of"] = prior["possible_duplicate_of"]
        if (
            prior.get("lifecycle")
            and not combined.get("superseded_by")
            and (
                (prior_verification.get("verified") and not current_verification.get("verified"))
                or (not current_verification.get("source_status") and row.get("decision_reason") in {
                    "Needs current verification",
                    "Possible duplicate; content hash unavailable",
                    "Possible duplicate; comparable content hash unavailable",
                    "Recent relevant work",
                })
            )
        ):
            combined["lifecycle"] = prior["lifecycle"]
            combined["lifecycle_color"] = LIFECYCLE_COLORS[prior["lifecycle"]]
            combined["decision_reason"] = prior.get("decision_reason", combined["decision_reason"])
        if combined.get("superseded_by"):
            combined["lifecycle"] = "ARCHIVE"
            combined["lifecycle_color"] = LIFECYCLE_COLORS["ARCHIVE"]
            combined["decision_reason"] = "Known replacement recorded"
        merged[row["version_key"]] = combined
    by_identity: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in merged.values():
        identity = (row.get("version_evidence", {}).get("source"), row.get("source_id"))
        if all(identity) and row.get("observed_current"):
            by_identity.setdefault(identity, []).append(row)
    incoming = {}
    for row in current:
        identity = (row.get("version_evidence", {}).get("source"), row.get("source_id"))
        if row.get("observed_current"):
            incoming.setdefault(identity, set()).add(row["version_key"])
    for identity, versions in by_identity.items():
        if len(versions) > 1:
            observed = [row for row in versions if row["version_key"] in incoming.get(identity, set())]
            winner = max(observed or versions, key=lambda row: (modified_instant(row.get("version_evidence", {}).get("modified")), str(row.get("version_evidence", {}).get("revision_id") or ""), row["version_key"]))
            for row in versions:
                row["observed_current"] = row is winner
    return sorted(merged.values(), key=lambda row: row["version_key"])


def reclassify_exact_duplicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reapply exact duplicate flags using current and previously-current hash evidence."""
    candidate_indexes = [
        index
        for index, row in enumerate(rows)
        if row.get("observed_current")
    ]
    exact_groups: dict[str, list[int]] = {}
    for index in candidate_indexes:
        version_evidence = rows[index].get("version_evidence", {})
        digest = digest_evidence(version_evidence)
        if digest:
            exact_groups.setdefault(json.dumps(digest, separators=(",", ":")), []).append(index)
            rows[index]["flags"] = [flag for flag in rows[index]["flags"] if flag != "DUPLICATE"]
            rows[index]["flag_colors"] = [FLAG_COLORS[flag] for flag in rows[index]["flags"]]
            rows[index]["canonical_version_key"] = None
    for indexes in exact_groups.values():
        if len(indexes) < 2:
            continue
        canonical = max(
            indexes,
            key=lambda idx: selection_rank(
                rows[idx].get("canonical"),
                rows[idx].get("verification", {}).get("verified"),
                rows[idx].get("lifecycle"),
                rows[idx].get("version_evidence", {}).get("modified"),
                rows[idx].get("version_key"),
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


def reclassify_likely_duplicates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Review hashless title/size matches across the complete merged current set."""
    groups: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        if row.get("observed_current"):
            row["possible_duplicate_of"] = None
            if row.get("decision_reason") in {"Possible duplicate; content hash unavailable", "Possible duplicate; comparable content hash unavailable"}:
                row["lifecycle"] = row.get("source_lifecycle") or "REVIEW"
                row["lifecycle_color"] = LIFECYCLE_COLORS[row["lifecycle"]]
                row["decision_reason"] = row.get("source_decision_reason") or "Needs current verification"
            full_title = row.get("duplicate_title") or short_title({"name": row.get("source_name") or row.get("display_title", "")}, limit=10_000)
            key = likely_duplicate_key({"size": row.get("source_size", "")}, full_title)
            groups.setdefault(key, []).append(index)
    for indexes in groups.values():
        if len(indexes) < 2 or not needs_hash_review(rows[i].get("version_evidence", {}) for i in indexes):
            continue
        conflicting = {i for offset, a in enumerate(indexes) for b in indexes[offset + 1:] if comparable_digest_conflict(rows[a].get("version_evidence", {}), rows[b].get("version_evidence", {})) for i in (a, b)}
        for index in indexes:
            row = rows[index]
            if index in conflicting:
                continue
            candidates = [i for i in indexes if i != index and not comparable_digest_conflict(row.get("version_evidence", {}), rows[i].get("version_evidence", {}))]
            if not candidates:
                continue
            canonical = max(candidates if conflicting else [index, *candidates], key=lambda i: selection_rank(
                rows[i].get("canonical"), rows[i].get("verification", {}).get("verified"),
                rows[i].get("lifecycle"), rows[i].get("version_evidence", {}).get("modified"), rows[i]["version_key"],
            ))
            if canonical != index:
                row["possible_duplicate_of"] = rows[canonical]["version_key"]
            if canonical != index and row.get("lifecycle") not in {"FINAL", "ARCHIVE"}:
                row["lifecycle"] = "REVIEW"
                row["lifecycle_color"] = LIFECYCLE_COLORS["REVIEW"]
                row["decision_reason"] = "Possible duplicate; comparable content hash unavailable"
    return rows


def build_registry_payload(
    rows: list[dict[str, Any]],
    previous: list[dict[str, Any]] | None = None,
    *,
    full_snapshot: bool = False,
    snapshot_sources: set[str] | None = None,
) -> dict[str, Any]:
    previous_rows = previous or []
    if snapshot_sources is not None and any(row.get("version_evidence", {}).get("source") not in snapshot_sources for row in rows):
        raise ValueError("snapshot inventory contains records outside the selected source namespaces")
    items = reclassify_likely_duplicates(reclassify_exact_duplicates(
        merge_history(rows, previous_rows, full_snapshot=full_snapshot, snapshot_sources=snapshot_sources),
    ))
    generated_at = datetime.now(timezone.utc).isoformat()
    exceptions = [
        row for row in items
        if row.get("lifecycle") == "REVIEW"
        or row.get("sensitivity") == "UNKNOWN"
        or (row.get("sensitivity") == "SENSITIVE" and not row.get("verification", {}).get("verified"))
        or row.get("unresolved_review")
        or (row.get("possible_duplicate_of") and not row.get("verification", {}).get("verified"))
    ]
    exception_payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "exception_count": len(exceptions),
        "items": exceptions,
    }
    return {
        "schema_version": 2,
        "generated_at": generated_at,
        "organization_mode": "metadata-first",
        "physical_changes": False,
        "items": items,
        "exceptions": exception_payload,
    }


def atomic_write_private(output: Path, payload: dict[str, Any]) -> None:
    """Atomically publish private JSON with user-only filesystem permissions."""
    write_private_text(output, json.dumps(payload, indent=2) + "\n")


def write_registry(rows: list[dict[str, Any]], output: Path, *, full_snapshot: bool = False, snapshot_sources: set[str] | None = None) -> int:
    output = validate_unlinked_path(output)
    legacy_exception_name = f"{output.stem}.exceptions.json"
    lock_path = validate_unlinked_path(output.with_name(f".{output.name}.lock"))
    with private_directory(output.parent, create=True) as directory:
        descriptor = os.open(lock_path.name, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory)
        with os.fdopen(descriptor, "a") as lock:
            metadata = os.fstat(lock.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1 or metadata.st_mode & 0o777 != 0o600:
                raise PermissionError("registry lock must be an unlinked private file")
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            previous: list[dict[str, Any]] = []
            try:
                existing = read_text_at(directory, output.name)
            except FileNotFoundError:
                pass
            else:
                previous_payload = json.loads(existing)
                previous = previous_payload.get("items", []) if isinstance(previous_payload, dict) else []
            payload = build_registry_payload(rows, previous, full_snapshot=full_snapshot, snapshot_sources=snapshot_sources)
            # Retire the derived cache before publishing the single authoritative payload.
            try:
                metadata = os.stat(legacy_exception_name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
                    raise PermissionError("legacy exceptions cache must be a regular unlinked file")
                os.unlink(legacy_exception_name, dir_fd=directory)
            write_text_at(directory, output.name, json.dumps(payload, indent=2) + "\n")
            return payload["exceptions"]["exception_count"]


def validate_registry_output_path(inventory: Path, registry: Path) -> Path:
    resolved_inventory = inventory.expanduser().resolve()
    resolved_registry = validate_unlinked_path(registry).resolve()
    exception_path = validate_unlinked_path(resolved_registry.with_name(f"{resolved_registry.stem}.exceptions.json")).resolve()
    if resolved_inventory in {resolved_registry, exception_path}:
        raise ValueError("--registry must not overwrite the input inventory")
    if resolved_registry.is_relative_to(PROJECT_DIR):
        raise ValueError("--registry must point outside the repository checkout")
    return resolved_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Build KOVA's non-destructive file status registry")
    parser.add_argument("base_path", nargs="?", help="Deprecated legacy argument; files are never moved")
    parser.add_argument("--inventory", type=Path, help="Inventory JSON produced by a source scanner")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Print the registry without writing it")
    parser.add_argument("--full-snapshot", action="store_true", help="Inventory contains every current source; mark absent records as historical")
    parser.add_argument("--snapshot-source", action="append", help="Limit full-snapshot expiry to this explicit source namespace; repeat for multiple sources")
    parser.add_argument("--execute", action="store_true", help="Deprecated; output is always non-destructive")
    args = parser.parse_args()

    if args.inventory is None:
        if args.base_path or args.execute:
            print("Legacy move/folder arguments were ignored; governed files were not changed.")
            return 0
        parser.error("--inventory is required unless using legacy compatibility arguments")
    if not args.inventory.is_file():
        parser.error("--inventory must point to a JSON file")
    try:
        registry_path = validate_registry_output_path(args.inventory, args.registry)
    except (ValueError, PermissionError) as exc:
        parser.error(str(exc))

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    if not isinstance(inventory, list):
        parser.error("inventory must be a JSON array")
    rows = build_registry(inventory)
    snapshot_sources = set(args.snapshot_source) if args.snapshot_source else None
    if snapshot_sources and not args.full_snapshot:
        parser.error("--snapshot-source requires --full-snapshot")
    if snapshot_sources and any(not re.fullmatch(r"[a-z][a-z0-9_.-]*", source) or source == "unknown" for source in snapshot_sources):
        parser.error("snapshot sources must be explicit normalized namespaces")
    if args.dry_run:
        previous: list[dict[str, Any]] = []
        if registry_path.exists():
            payload = json.loads(read_private_text(registry_path))
            previous = payload.get("items", []) if isinstance(payload, dict) else []
        preview = build_registry_payload(rows, previous, full_snapshot=args.full_snapshot, snapshot_sources=snapshot_sources)
        print(json.dumps({
            "organization_mode": preview["organization_mode"],
            "physical_changes": False,
            "item_count": len(preview["items"]),
            "current_count": sum(bool(row.get("observed_current")) for row in preview["items"]),
            "lifecycle_counts": {state: sum(row["lifecycle"] == state for row in preview["items"]) for state in LIFECYCLE_COLORS},
            "exception_count": preview["exceptions"]["exception_count"],
        }, indent=2))
    else:
        exception_count = write_registry(rows, registry_path, full_snapshot=args.full_snapshot, snapshot_sources=snapshot_sources)
        print(f"Wrote {len(rows)} current metadata records to {registry_path}")
        print(f"Included {exception_count} review exceptions in the registry")
    if args.base_path or args.execute:
        print("Legacy move/folder arguments were ignored; governed files were not changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
