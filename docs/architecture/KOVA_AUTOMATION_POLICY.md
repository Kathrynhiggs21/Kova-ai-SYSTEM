# KOVA Automation Policy

Status: Canonical v1

## Operating rule

KOVA automates predictable work by default. The owner should not repeatedly sort files, copy status between systems, retype data, run maintenance commands, or configure the same integration in several tools.

Automation is metadata-first and non-destructive. Originals stay unchanged unless a separate, explicit task authorizes a content change.

## Automatic path

When a new or changed item appears, KOVA should:

1. retain its source identity, exact version, chat/agent ID and link when available;
2. generate a short topic/subtopic display title without renaming the source by default;
3. normalize K9VA, Kiva, Kova AI and similar project spellings to the appropriate KOVA display name;
4. assign one lifecycle state: `ACTIVE`, `FINAL`, `REVIEW` or `ARCHIVE`;
5. add independent `SENSITIVE` and `DUPLICATE` flags when applicable;
6. identify the canonical source for duplicate groups;
7. update the private canonical registry and any human-readable views; and
8. notify the owner only when an exception requires a decision.

`FINAL` is never inferred from a filename alone. It requires verification or an explicit authoritative decision.

## Approval boundary

KOVA pauses before an action that can create material harm or cannot be cleanly reversed:

- deleting or overwriting content;
- changing sharing, permissions or identity mappings;
- exposing, moving or rotating credentials;
- spending money or creating a financial commitment;
- sending external messages;
- merging or deploying code;
- moving or renaming an ambiguous item; or
- creating a physical folder without a demonstrated operational need.

Everything else should be handled automatically when confidence is high. Low-confidence cases become `REVIEW`; they do not become surprise folders.

## Connector routing

Use the shortest trustworthy route available:

1. native connector or app;
2. MCP action;
3. official API with OAuth;
4. Zapier, Make, n8n or another automation bridge; then
5. webhook, export or import fallback.

No automation vendor is a mandatory KOVA dependency. The archived Zapier starter-action guide is historical because direct Gmail, Drive, Calendar, Notion and GitHub connections can perform the same work without manually registering twelve Zapier MCP actions.

## Folder rule

Topics, subtopics, lifecycle and relationships are metadata. Do not automatically create a physical folder for every category. Create one only when the material does not fit an existing location or a separate file boundary is operationally necessary.

## Failure behavior

- Retry bounded transient failures.
- Record the source, action, outcome and error without secret values.
- Never report a connector as healthy solely because configuration exists.
- Do not mark an operation complete until a readback or equivalent evidence confirms it.
- Group unresolved exceptions into one short report; stay quiet on routine success.

The machine-readable policy is `config/automation_policy.v1.json`. The metadata registry builder is `scripts/file_organizer.py`.
