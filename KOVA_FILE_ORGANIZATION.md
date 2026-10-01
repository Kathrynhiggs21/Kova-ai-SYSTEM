# KOVA File Organization

This document is the file-specific companion to the [KOVA Organization Guide](KOVA_ORGANIZATION_GUIDE.md) and [KOVA Automation Policy](docs/architecture/KOVA_AUTOMATION_POLICY.md).

## Canonical record

The private status registry is authoritative. Each exact version records:

- stable source/version key;
- original filename and source identifier;
- short display title;
- topic and optional subtopic;
- lifecycle state and accessible color;
- `SENSITIVE` or `DUPLICATE` flags;
- canonical duplicate target or `superseded_by` relationship;
- source chat or agent ID and link when available; and
- decision reason and verification evidence.

Source files remain in place and keep their original contents and names by default.

## Automatic classification

The registry builder performs deterministic, conservative classification. It may mark a recent KOVA item `ACTIVE`, but it marks uncertain items `REVIEW`. `FINAL` requires verification; `ARCHIVE` requires an explicit state or a recorded replacement.

Exact content hashes take priority for duplicate detection. Filename and size similarity may raise a duplicate candidate but never authorizes deletion.

## Connector behavior

Use native connectors first, followed by MCP, official OAuth APIs, optional automation bridges, then export/import fallbacks. Connector configuration is not proof of health; each active claim needs a current safe read or readback.

The legacy Zapier starter-action pack is retained only as historical setup reference. Direct Gmail, Drive, Calendar, Notion and GitHub connections remove the need to manually register those twelve actions.

## Local registry builder

```bash
python3 scripts/file_organizer.py --inventory path/to/inventory.json
```

Legacy positional paths and `--execute` are accepted only to prevent accidental breakage; they are ignored and never move governed files.

Every item needs an explicit source namespace, a stable source identifier, and supported revision or content-hash evidence. Local paths must be absolute and use their canonical path as identity. GitHub path records require a repository owner/name; their identity combines that repository with the file path, while blob hashes identify versions. Direct registry updates are incremental by default, including an empty update. Use `--full-snapshot` only with a complete inventory; add `--snapshot-source google_drive` to expire only absent Drive records. The setup runner uses this scoped Drive snapshot for a fresh scan and defaults explicit inventories to incremental updates. Pass `drive-snapshot` or `full-snapshot` as its third argument only when the inventory covers the indicated sources. A dry run performs the same history merge and canonical selection as a write.

With no inventory argument, the setup runner performs a fresh successful Drive scan. A successful empty scan publishes an empty snapshot; authentication or scan failures stop without reusing an older inventory. To use an independently verified inventory, pass its path as the first argument. Registry updates hold a private interprocess lock across the history merge and both output writes. Structured version keys avoid delimiter collisions; existing keys and duplicate pointers are upgraded while preserving decisions.

Private state operations pin directory descriptors and use no-follow, descriptor-relative reads and atomic writes. A concurrent link replacement cannot redirect credentials or registry output. Published ZIP exports are assembled completely at a temporary path before replacing the served archive.

Dry runs print only redacted aggregate counts. They do not print filenames, source IDs, links or verification references. Multiple current revisions for the same source identity in one batch are rejected; history is retained from prior scans. Local files are hashed once per build, and probable title/size duplicates are reviewed across merged incremental records.

The optional Google Drive inventory tool stores client credentials and JSON tokens under the private state directory, outside the repository by default. It requests read-only access and never loads a legacy `token.pickle`. Put the owner-approved client credentials in `<private state>/google-drive/credentials.json`, or supply an explicit `--credentials` path. Existing pickle tokens require a fresh, explicit sign-in; do not copy them into source control. This local tool is not evidence that the deployed KOVA connection is working.
