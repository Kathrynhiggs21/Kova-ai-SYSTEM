# KOVA Organization Guide

KOVA organizes files and records with metadata. It does not require a folder tree and does not move, rename, overwrite or delete governed source files during routine organization.

## Simple model

Each exact item version uses:

- **Area:** `KOVA`, `Personal`, `Reagan` or `Other`
- **Topic:** one useful subject; subtopic only when it improves retrieval
- **Lifecycle:** `ACTIVE`, `FINAL`, `REVIEW` or `ARCHIVE`
- **Flags:** `SENSITIVE` and verified `DUPLICATE` when applicable

File Type and Content Origin are descriptive fields. Legacy `UNREVIEWED` maps to `REVIEW`.

## Safe workflow

1. Run the read-only Google Drive inventory:

   ```bash
   python3 scripts/gdrive_import.py
   ```

2. Build or refresh the private registry:

   ```bash
   scripts/setup_kova_organization.sh
   ```

   By default, the registry is written to `${XDG_DATA_HOME:-$HOME/.local/share}/kova/private/status_registry.json`, outside the repository. Set `KOVA_PRIVATE_STATE_DIR` to another approved private location when needed.

3. Review only exceptions:

   - uninspected sensitivity remains `UNKNOWN`;
   - a matching name or similar title is a possible duplicate and stays `REVIEW`;
   - `DUPLICATE` requires a hash or equivalent revision evidence;
   - `FINAL` requires verification, not merely the word “final” in a filename.

4. Apply a destructive or structural change only through a separate approved task. Repository creation, deletions, permissions, credentials, payments, external messages, deployments and ambiguous moves require owner approval.

## Chats and AI World

KOVA-related chats can be `Decision`, `Requirement`, `Idea`, `Evidence`, `Historical`, `Mixed` or `Unknown`. Only a confirmed decision changes the canonical specification. An inaccessible shared-chat link remains `REVIEW`.

AI agent folders and general AI-platform content stay in AI World. KOVA records a purposeful relationship or source link instead of creating a mirrored copy.

## Repository boundary

The active pair is `Kathrynhiggs21/Kova-ai-SYSTEM` and `Kathrynhiggs21/kovaos-site`. Assistant, MCP, connectors, automation, memory/data, files/artifacts, security, jobs and observability remain Core modules until an approved independent deployment, security, scaling, release or ownership boundary exists.

The canonical policy is `config/automation_policy.v1.json`; the registry builder is `scripts/file_organizer.py`.
