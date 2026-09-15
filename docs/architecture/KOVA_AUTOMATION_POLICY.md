# KOVA Automation Policy

Status: Canonical v2

## Operating rule

KOVA automates predictable work by default. The owner should not repeatedly sort files, copy status between systems, retype data, run maintenance commands, or configure the same integration in several tools.

Automation is metadata-first and non-destructive. Originals stay unchanged unless a separate, explicit task authorizes a content change.

## Simple organization model

Every governed item uses the smallest useful set of metadata:

1. **Area** - `KOVA`, `Personal`, `Reagan`, or `Other`.
2. **Topic** - one useful subject; a subtopic is optional and added only when it improves retrieval.
3. **Lifecycle** - exactly one of `ACTIVE`, `FINAL`, `REVIEW`, or `ARCHIVE`.
4. **Flags** - `SENSITIVE` and verified `DUPLICATE` only when applicable.

File Type and Content Origin are descriptive fields, not competing label systems. Legacy `UNREVIEWED` maps to `REVIEW`.

Chat records also carry one descriptive Record Role: `Decision`, `Requirement`, `Idea`, `Evidence`, `Historical`, `Mixed`, or `Unknown`. A shared chat or brainstorming note never becomes an approved decision merely because it exists.

`FINAL` is never inferred from a filename alone. It requires verification or an explicit authoritative decision. A matching name or file size is only a possible duplicate; `DUPLICATE` requires strong content or revision evidence.

## Automatic path

When a new or changed item appears, KOVA should:

1. retain source identity, exact version, chat or agent ID, and link when available;
2. generate a short display title without renaming the source by default;
3. normalize K9VA, Kiva, Kova AI, and similar confirmed spellings in display metadata while retaining the original wording as an alias;
4. assign Area, Topic, Lifecycle, File Type, and Content Origin;
5. record sensitivity as `SENSITIVE`, `CLEAR`, or `UNKNOWN` so an uninspected file is never treated as safe by implication;
6. verify exact duplicates from hashes or equivalent evidence and queue weaker matches for `REVIEW`;
7. choose a deterministic canonical item for verified duplicate groups;
8. preserve prior exact-version history, decisions, and verification evidence;
9. update the private canonical registry and human-readable views; and
10. notify the owner only when an exception requires a decision.

## System boundaries

- AI agent folders and general AI-platform content stay inside the single AI World root.
- KOVA does not copy AI World material into KOVA storage. It stores a purposeful source link or relationship when needed.
- KOVA-specific operating-system records stay in KOVA.
- The ChatGPT KOVA project, Drive, Notion, and GitHub use canonical sources plus links or views; they do not maintain mirrored master copies.

## Repository rule

The active pair is:

- `Kathrynhiggs21/Kova-ai-SYSTEM` - Core, control plane, backend, and shared contracts.
- `Kathrynhiggs21/kovaos-site` - authenticated application and primary interface for `kovaos.com`.

AI Assistant, MCP, connectors, automation, memory/data, security, files/artifacts, and jobs/observability are modules inside Core. A module becomes a separate repository only when it has a distinct deployment, security or secrets boundary, scaling profile, or independent release cycle. A category name alone is not a reason to create a repository.

## Approval boundary

KOVA pauses before deleting or overwriting content; changing sharing, permissions, or identity mappings; exposing or rotating credentials; spending money; sending external messages; merging or deploying code; moving or renaming an ambiguous item; creating a physical folder without demonstrated operational need; or creating a repository.

Everything else should be handled automatically when confidence is high. Low-confidence cases become `REVIEW`; they do not become surprise folders.

## Connector routing

Use the shortest trustworthy route available:

1. native connector or app;
2. MCP action;
3. official API with OAuth;
4. Zapier, Make, n8n, or another automation bridge; then
5. webhook, export, or import fallback.

No automation vendor is a mandatory KOVA dependency. The Zapier starter-action guide is historical because direct Gmail, Drive, Calendar, Notion, and GitHub connections cover those tasks without manually registering twelve Zapier MCP actions.

## Failure behavior

- Retry bounded transient failures.
- Record the source, action, outcome, and error without secret values.
- Never report a connector as healthy solely because configuration exists.
- Do not mark an operation complete until a readback or equivalent evidence confirms it.
- Group unresolved exceptions into one short report; stay quiet on routine success.

The machine-readable policy is `config/automation_policy.v1.json`. The registry builder is `scripts/file_organizer.py`.
