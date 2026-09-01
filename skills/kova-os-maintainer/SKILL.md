---
name: kova-os-maintainer
description: Maintain and evolve the KOVA OS orchestration repository with minimal, canonical, and secure changes. Use when handling KOVA platform tasks such as API/service updates, multi-repo automation changes, deployment and monitoring configuration updates, CI failure investigation, or documentation-to-code consistency fixes.
---

# KOVA OS Maintainer

## Purpose

Execute KOVA OS maintenance work safely and end-to-end in this repository.
Preserve the canonical architecture, avoid duplicate implementations, and validate changes before reporting completion.

## Workflow

1. Confirm scope and identify the canonical component to modify.
2. Read the relevant source files and docs before editing.
3. Make the smallest complete implementation change.
4. Validate with repository and runtime checks that apply.
5. Update documentation if behavior, setup, or ownership expectations changed.
6. Summarize what changed, what was verified, and what remains blocked by external access or owner decisions.

## Canonical Rules

- Treat this repository as the orchestration source of truth for KOVA OS.
- Extend existing scripts, services, dashboards, and docs instead of creating parallel replacements.
- Before introducing a new component, verify an equivalent does not already exist.
- Do not delete older systems just because they appear redundant; verify they are superseded first.

## Safety Rules

- Never commit or print live credentials, keys, tokens, or private secrets.
- Keep secrets in environment variables or approved secret stores; only commit safe templates such as `.env.example`.
- Prefer reversible migrations and backups for destructive or structural work.
- If a file appears to contain a secret, redact/remediate without repeating its value.

## Build and Validation

Run checks that match the changed scope. Baseline checks for this repository:

```bash
python3 scripts/validate_config.py
python3 scripts/test_multi_repo.py
```

For runtime/container changes, run the operational checks when environment access is available:

```bash
./verify_platform.sh
./setup_kova_system.sh
curl http://localhost:8000/health
curl -X POST http://localhost:8000/ai/command -H "Content-Type: application/json" -d '{"command":"test command"}'
```

If a required check cannot run due to missing credentials, services, or permissions, state that explicitly.

## CI and Workflow Failures

When debugging CI/build/test/workflow failures:

1. List recent workflow runs to locate failing runs.
2. Pull failed job logs for root-cause details.
3. Implement minimal fixes and re-run relevant local validations.

## Documentation Updates

Update canonical docs whenever changes affect behavior, setup, architecture, or repository ownership.
Do not add duplicative summary documents when existing canonical docs can be updated directly.

## Done Criteria

A task is complete only when:

- Implementation is internally consistent.
- Relevant checks were run, or blockers were explicitly documented.
- Final summary includes changed files/components, validation results, and remaining external blockers.

## Key Repository References

- `README.md`
- `AGENTS.md`
- `KOVA_REPOS_DOCUMENTATION.md`
- `MULTI_REPO_GUIDE.md`
- `SETUP_GUIDE.md`
