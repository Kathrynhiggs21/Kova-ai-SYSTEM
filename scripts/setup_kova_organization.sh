#!/usr/bin/env bash
# Build KOVA's private metadata registry from an explicit inventory or fresh scan.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(dirname "$script_dir")"
inventory_path="${1:-}"
private_state_dir="${KOVA_PRIVATE_STATE_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/kova/private}"
registry_path="${2:-$private_state_dir/status_registry.json}"
snapshot_mode="${3:-drive-snapshot}"
snapshot_args=()
case "$snapshot_mode" in
  drive-snapshot) snapshot_args+=(--full-snapshot --snapshot-source google_drive) ;;
  full-snapshot) snapshot_args+=(--full-snapshot) ;;
  incremental) ;;
  *) echo "Third argument must be drive-snapshot, full-snapshot, or incremental." >&2; exit 1 ;;
esac

if [[ -z "$inventory_path" ]]; then
  inventory_path="$(python3 - "$script_dir" <<'PY'
from contextlib import redirect_stdout
import sys

sys.path.insert(0, sys.argv[1])
with redirect_stdout(sys.stderr):
    from gdrive_import import GoogleDriveImporter
    inventory = GoogleDriveImporter().run()
print(inventory)
PY
)"
fi

if [[ -z "$inventory_path" || ! -f "$inventory_path" ]]; then
  echo "No inventory found. Run the source scanner or provide an inventory JSON path." >&2
  exit 1
fi

python3 "$script_dir/file_organizer.py" --inventory "$inventory_path" --registry "$registry_path" "${snapshot_args[@]}"
echo "KOVA metadata registry updated. No governed files were moved, renamed, or deleted."
