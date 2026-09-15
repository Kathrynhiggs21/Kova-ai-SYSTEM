# KOVA Organization Guide

Status: Canonical automated workflow

KOVA organization is metadata-first. It does not require a weekly manual sorting session, a numbered folder tree, or destructive cleanup commands.

## Routine operation

1. A connected source supplies an inventory of new or changed items.
2. `scripts/file_organizer.py` generates a short display title, KOVA topic, lifecycle state, flags, provenance and duplicate relationship.
3. The canonical private registry is updated.
4. High-confidence reversible metadata changes complete automatically.
5. Only unresolved conflicts appear in an exception report.

Use:

```bash
./scripts/setup_kova_organization.sh path/to/inventory.json path/to/status_registry.json
```

If the paths are omitted, the script uses the newest `kova_file_inventory/inventory_*.json` and writes `kova_file_inventory/status_registry.json`.

## Lifecycle states

| State | Color | Meaning |
|---|---|---|
| `ACTIVE` | Blue `#0969DA` | Current work or an authoritative artifact in active use |
| `FINAL` | Emerald `#1F883D` | Verified and authoritative for a stated purpose |
| `REVIEW` | Amber `#BF8700` | Current evidence is insufficient or conflicting |
| `ARCHIVE` | Slate `#6E7781` | Superseded or historical, retained for context |

`SENSITIVE` and `DUPLICATE` are separate flags. Color is always paired with text.

## What KOVA never infers

- A filename containing “final” does not prove that an item is `FINAL`.
- Old age alone does not make an item `ARCHIVE`.
- A folder label does not automatically apply to every child.
- A similar filename does not authorize deletion.

## Physical folders

Create a folder only when new material cannot be represented clearly in an existing location or a separate operational boundary is genuinely required. Topics, subtopics and lifecycle states are metadata, not a reason to manufacture directories.

## Approval-only actions

Deletion, overwrite, permission changes, secret handling, external sends, financial commitments, ambiguous moves/renames, code merges and deployments require explicit approval. See [KOVA Automation Policy](docs/architecture/KOVA_AUTOMATION_POLICY.md).
