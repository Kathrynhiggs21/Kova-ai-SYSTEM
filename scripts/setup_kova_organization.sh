#!/usr/bin/env bash
# Build KOVA's metadata registry from the newest available inventory.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(dirname "$script_dir")"
inventory_dir="$project_dir/kova_file_inventory"
inventory_path="${1:-}"
registry_path="${2:-$inventory_dir/status_registry.json}"

if [[ -z "$inventory_path" ]]; then
  inventory_path="$(find "$inventory_dir" -maxdepth 1 -type f -name 'inventory_*.json' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 1 | cut -d' ' -f2-)"
fi

if [[ -z "$inventory_path" || ! -f "$inventory_path" ]]; then
  echo "No inventory found. Run the source scanner or provide an inventory JSON path." >&2
  exit 1
fi

python3 "$script_dir/file_organizer.py" \
  --inventory "$inventory_path" \
  --registry "$registry_path"

echo "KOVA metadata registry updated. No governed files were moved, renamed, or deleted."
