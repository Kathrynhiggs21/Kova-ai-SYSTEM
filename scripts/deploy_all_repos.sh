#!/usr/bin/env bash
set -euo pipefail

# KOVA repository maintenance helper.
#
# This script intentionally does not deploy applications or copy the canonical
# registry into other repositories. It reads enabled repositories from
# kova_repos_config.json, keeps local checkouts current, and gates any future
# repository creation behind both policy and an explicit registry approval.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_PATH="$PROJECT_ROOT/kova_repos_config.json"

usage() {
    echo "Usage:"
    echo "  $0 status [--all]        Show local checkout status (default)"
    echo "  $0 update                Clone or fast-forward enabled repositories"
    echo "  $0 create <name> --owner-approved"
    echo
    echo "Repository creation also requires creation_approved: true in the"
    echo "canonical registry. Add that flag through a reviewed architecture PR."
}

require_tools() {
    command -v git >/dev/null || {
        echo "git is required" >&2
        exit 1
    }
    command -v python3 >/dev/null || {
        echo "python3 is required" >&2
        exit 1
    }
    python3 "$PROJECT_ROOT/scripts/validate_config.py" >/dev/null
}

list_repositories() {
    local include_all="${1:-false}"
    python3 - "$CONFIG_PATH" "$include_all" <<'PY'
import json
import sys

config_path, include_all = sys.argv[1], sys.argv[2] == "true"
with open(config_path, encoding="utf-8") as handle:
    config = json.load(handle)
collections = ("repositories", "worlds", "excluded_repositories") if include_all else ("repositories",)
for collection in collections:
    for repository in config.get(collection, []):
        if not include_all and not repository["enabled"]:
            continue
        print(repository["full_name"])
PY
}

repository_field() {
    local repository_name="$1"
    local field="$2"
    python3 - "$CONFIG_PATH" "$repository_name" "$field" <<'PY'
import json
import sys

config_path, repository_name, field = sys.argv[1:]
with open(config_path, encoding="utf-8") as handle:
    config = json.load(handle)
for repository in config["repositories"]:
    if repository["name"].casefold() == repository_name.casefold():
        value = repository.get(field)
        if isinstance(value, bool):
            print("true" if value else "false")
        elif value is not None:
            print(value)
        break
PY
}

policy_requires_owner_approval() {
    python3 - "$CONFIG_PATH" <<'PY'
import json
import pathlib
import sys

config_path = pathlib.Path(sys.argv[1])
with config_path.open(encoding="utf-8") as handle:
    config = json.load(handle)
policy_reference = config["repository_creation_policy"]["split_policy_file"]
with (config_path.parent / policy_reference).open(encoding="utf-8") as handle:
    policy = json.load(handle)
print("true" if policy["split_policy"]["requires_owner_approval"] else "false")
PY
}

checkout_path() {
    local full_name="$1"
    echo "$PROJECT_ROOT/../${full_name#*/}"
}

show_status() {
    local include_all="${1:-false}"
    while IFS= read -r full_name; do
        local path
        path="$(checkout_path "$full_name")"
        if [ ! -d "$path/.git" ]; then
            echo "$full_name | not cloned"
            continue
        fi
        local branch commit changes
        branch="$(git -C "$path" branch --show-current)"
        commit="$(git -C "$path" rev-parse --short HEAD)"
        changes="$(git -C "$path" status --porcelain | wc -l | tr -d ' ')"
        echo "$full_name | $branch | $commit | local changes: $changes"
    done < <(list_repositories "$include_all")
}

update_enabled() {
    while IFS= read -r full_name; do
        local path
        path="$(checkout_path "$full_name")"
        if [ ! -d "$path/.git" ]; then
            git clone "https://github.com/$full_name.git" "$path"
            continue
        fi
        if [ -n "$(git -C "$path" status --porcelain)" ]; then
            echo "Refusing to update dirty checkout: $path" >&2
            continue
        fi
        git -C "$path" fetch origin
        git -C "$path" pull --ff-only
    done < <(list_repositories false)
}

create_repository() {
    local repository_name="${1:-}"
    local approval_flag="${2:-}"
    if [ -z "$repository_name" ] || [ "$approval_flag" != "--owner-approved" ]; then
        echo "Repository creation requires a name and --owner-approved." >&2
        exit 1
    fi
    if [ "$(policy_requires_owner_approval)" != "true" ]; then
        echo "Policy error: repository creation must require owner approval." >&2
        exit 1
    fi
    if [ "$(repository_field "$repository_name" creation_approved)" != "true" ]; then
        echo "Repository creation is not approved in kova_repos_config.json." >&2
        echo "Use a reviewed architecture PR to set creation_approved: true first." >&2
        exit 1
    fi
    command -v gh >/dev/null || {
        echo "GitHub CLI (gh) is required for repository creation." >&2
        exit 1
    }
    local full_name
    full_name="$(repository_field "$repository_name" full_name)"
    if [ -z "$full_name" ]; then
        echo "Repository is not listed in the canonical registry." >&2
        exit 1
    fi
    gh repo create "$full_name" --private --description "KOVA OS - $repository_name"
}

main() {
    require_tools
    case "${1:-status}" in
        status)
            if [ "${2:-}" = "--all" ]; then
                show_status true
            else
                show_status false
            fi
            ;;
        update)
            update_enabled
            ;;
        create)
            create_repository "${2:-}" "${3:-}"
            ;;
        deploy|sync)
            echo "This command was retired because it was not a real deployment" >&2
            echo "and duplicated canonical configuration across repositories." >&2
            exit 2
            ;;
        help|-h|--help)
            usage
            ;;
        *)
            usage >&2
            exit 2
            ;;
    esac
}

main "$@"
