#!/usr/bin/env bash
# Build KOVA's private metadata registry from the newest available inventory.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(dirname "$script_dir")"
inventory_dir="$project_dir/kova_file_inventory"
inventory_path="${1:-}"
private_state_dir="${KOVA_PRIVATE_STATE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/kova/private}"
registry_path="${2:-$private_state_dir/status_registry.json}"

if [[ -z "$inventory_path" ]]; then
  if [[ ! -d "$inventory_dir" ]]; then
    echo "No inventory found. Run the source scanner or provide an inventory JSON path." >&2
    exit 1
  fi
  inventory_path="$(python3 - "$inventory_dir" <<'PY'
from pathlib import Path
import sys

files = sorted(Path(sys.argv[1]).glob("inventory_*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
print(files[0] if files else "")
PY
)"
fi

if [[ -z "$inventory_path" || ! -f "$inventory_path" ]]; then
  echo "No inventory found. Run the source scanner or provide an inventory JSON path." >&2
  exit 1
fi

python3 "$script_dir/file_organizer.py" --inventory "$inventory_path" --registry "$registry_path"
echo "KOVA metadata registry updated. No governed files were moved, renamed, or deleted."
