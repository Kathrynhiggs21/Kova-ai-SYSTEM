# KOVA File Organization Summary

KOVA now uses an automated, non-destructive metadata system.

- Repetitive inventory, title cleanup, topic classification, lifecycle tagging, sensitivity detection, duplicate grouping, provenance linking and registry updates are automatic.
- `ACTIVE`, `FINAL`, `REVIEW` and `ARCHIVE` are the only lifecycle states.
- `SENSITIVE` and `DUPLICATE` are independent flags.
- Originals are not moved, renamed, overwritten or deleted by routine automation.
- Physical folders are created only when a real operational boundary requires one.
- Routine success stays quiet; true exceptions are grouped for a decision.
- Destructive, external, financial, credential, permission, merge and deployment actions remain approval-only.

Implementation:

- Policy: `docs/architecture/KOVA_AUTOMATION_POLICY.md`
- Machine rules: `config/automation_policy.v1.json`
- Registry builder: `scripts/file_organizer.py`
- Runner: `scripts/setup_kova_organization.sh`
- Tests: `tests/test_file_organizer.py`
