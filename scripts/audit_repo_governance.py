#!/usr/bin/env python3
"""Audit Mergify and ruleset governance for repositories in kova_repos_config.json."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "kova_repos_config.json"


@dataclass
class RepoRecord:
    full_name: str
    collection: str
    enabled: bool
    repo_type: str


@dataclass
class CheckResult:
    full_name: str
    collection: str
    enabled: bool
    repo_type: str
    requires_enforcement: bool
    mergify_ok: bool | None
    ruleset_ok: bool | None
    status: str
    details: list[str]


class GitHubClient:
    def __init__(self, token: str):
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {token}",
        }

    def get_json(self, url: str) -> tuple[int | None, Any, str | None]:
        request = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                payload = response.read().decode("utf-8")
                return response.status, json.loads(payload), None
        except urllib.error.HTTPError as error:
            payload = ""
            try:
                payload = error.read().decode("utf-8")
            except Exception:
                payload = ""
            message = payload or str(error)
            return error.code, None, message
        except Exception as error:  # pragma: no cover
            return None, None, str(error)

    def get_text_file(self, owner: str, repo: str, path: str) -> tuple[int | None, str | None, str | None]:
        status, payload, error = self.get_json(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        )
        if status != 200:
            return status, None, error
        if not isinstance(payload, dict):
            return status, None, "Unexpected response payload"
        content = payload.get("content")
        encoding = payload.get("encoding")
        if not isinstance(content, str) or encoding != "base64":
            return status, None, "Unexpected content encoding"
        decoded = base64.b64decode(content).decode("utf-8", errors="replace")
        return status, decoded, None


def load_repo_records(config_path: Path) -> list[RepoRecord]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    records: list[RepoRecord] = []
    for repo in config.get("repositories", []):
        records.append(
            RepoRecord(
                full_name=str(repo.get("full_name", "")),
                collection="repositories",
                enabled=bool(repo.get("enabled", False)),
                repo_type=str(repo.get("type", "")),
            )
        )
    for world in config.get("worlds", []):
        records.append(
            RepoRecord(
                full_name=str(world.get("full_name", "")),
                collection="worlds",
                enabled=bool(world.get("enabled", False)),
                repo_type=str(world.get("type", "")),
            )
        )
    for excluded in config.get("excluded_repositories", []):
        records.append(
            RepoRecord(
                full_name=str(excluded.get("full_name", "")),
                collection="excluded_repositories",
                enabled=bool(excluded.get("enabled", False)),
                repo_type="excluded",
            )
        )
    return records


def ruleset_targets_main(ruleset: dict[str, Any]) -> bool:
    conditions = ruleset.get("conditions")
    if not isinstance(conditions, dict):
        return False
    ref_name = conditions.get("ref_name")
    if not isinstance(ref_name, dict):
        return False
    include = ref_name.get("include")
    if not isinstance(include, list):
        return False
    return any(entry == "refs/heads/main" for entry in include)


def active_main_ruleset_count(rulesets: list[dict[str, Any]]) -> int:
    count = 0
    for item in rulesets:
        if not isinstance(item, dict):
            continue
        if str(item.get("enforcement", "")).lower() == "disabled":
            continue
        if ruleset_targets_main(item):
            count += 1
    return count


def evaluate_repo(client: GitHubClient, record: RepoRecord) -> CheckResult:
    if "/" not in record.full_name:
        return CheckResult(
            full_name=record.full_name,
            collection=record.collection,
            enabled=record.enabled,
            repo_type=record.repo_type,
            requires_enforcement=False,
            mergify_ok=False,
            ruleset_ok=False,
            status="invalid",
            details=["Invalid repository coordinate in config"],
        )

    owner, repo = record.full_name.split("/", 1)
    requires_enforcement = (
        record.collection == "repositories"
        and record.enabled
        and record.repo_type in {"core", "frontend"}
    )
    details: list[str] = []

    mergify_status, mergify_text, mergify_error = client.get_text_file(owner, repo, ".mergify.yml")
    mergify_ok: bool | None
    if mergify_status == 200 and isinstance(mergify_text, str):
        mergify_ok = (
            "merge_queue:" in mergify_text
            and "branch_protection_injection_mode: queue" in mergify_text
        )
        if not mergify_ok:
            details.append(".mergify.yml exists but does not include required queue settings")
    elif mergify_status in {403, 404}:
        mergify_ok = None
        details.append(f".mergify.yml unreadable ({mergify_status})")
    else:
        mergify_ok = False
        details.append(f".mergify.yml check failed ({mergify_status}): {mergify_error or 'unknown error'}")

    ruleset_status, rulesets_payload, ruleset_error = client.get_json(
        f"https://api.github.com/repos/{owner}/{repo}/rulesets?includes_parents=false"
    )
    ruleset_ok: bool | None
    if ruleset_status == 200 and isinstance(rulesets_payload, list):
        main_rulesets = active_main_ruleset_count(
            [item for item in rulesets_payload if isinstance(item, dict)]
        )
        misleading_mergify_name = any(
            isinstance(item, dict)
            and str(item.get("name", "")).strip().casefold() == "mergify"
            for item in rulesets_payload
        )
        ruleset_ok = main_rulesets > 0
        if main_rulesets == 0:
            details.append("No active ruleset targeting refs/heads/main")
        if misleading_mergify_name:
            details.append("Ruleset named 'Mergify' still present; rename/remove if not queue policy")
    elif ruleset_status in {403, 404}:
        ruleset_ok = None
        details.append(f"Rulesets unreadable ({ruleset_status})")
    else:
        ruleset_ok = False
        details.append(f"Ruleset check failed ({ruleset_status}): {ruleset_error or 'unknown error'}")

    if requires_enforcement:
        if mergify_ok is True and ruleset_ok is True:
            status = "pass"
        elif mergify_ok is None or ruleset_ok is None:
            status = "blocked"
        else:
            status = "fail"
    else:
        status = "informational"

    if not details:
        details.append("Checks completed")

    return CheckResult(
        full_name=record.full_name,
        collection=record.collection,
        enabled=record.enabled,
        repo_type=record.repo_type,
        requires_enforcement=requires_enforcement,
        mergify_ok=mergify_ok,
        ruleset_ok=ruleset_ok,
        status=status,
        details=details,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(CONFIG_PATH),
        help="Path to kova_repos_config.json",
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        print("ERROR: GITHUB_TOKEN is required for governance audit", file=sys.stderr)
        return 2

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        return 2

    records = load_repo_records(config_path)
    client = GitHubClient(token)
    results = [evaluate_repo(client, record) for record in records]

    print("Repository governance audit")
    print("=========================")
    for result in results:
        requirement = "required" if result.requires_enforcement else "optional"
        print(
            f"- {result.full_name} [{result.collection}]"
            f" status={result.status} requirement={requirement}"
            f" mergify={result.mergify_ok} ruleset={result.ruleset_ok}"
        )
        for detail in result.details:
            print(f"    - {detail}")

    failures = [r for r in results if r.status == "fail"]
    blocked = [r for r in results if r.status == "blocked"]

    print("\nSummary")
    print("=======")
    print(f"Total repositories checked: {len(results)}")
    print(f"Required repositories failed: {len(failures)}")
    print(f"Required repositories blocked by access: {len(blocked)}")

    if failures:
        return 1
    if blocked:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
