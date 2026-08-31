# KOVA OS — Codex Operating Instructions

## Project identity

This repository is the canonical orchestration hub for KOVA OS. Treat it as the command center for coordinating KOVA services, repositories, integrations, automation, documentation, deployment, and validation.

The goal is one coherent KOVA system, not another parallel prototype.

## How to work in this repository

1. Inspect before changing. Read `README.md`, relevant implementation docs, current configuration, tests, and the files you intend to modify.
2. Prefer the existing architecture. Extend working components instead of creating duplicate apps, services, dashboards, repositories, scripts, or documentation trees.
3. Verify assumptions. Some historical KOVA documentation may be stale. Confirm current code and repository state before treating a document as authoritative.
4. Make the smallest complete change that solves the task. Avoid broad rewrites unless they are necessary and validated.
5. Keep work reviewable. Stay on the current task branch, make coherent commits, and do not push unreviewed changes directly to `main`.
6. Do the technical work when it is safe to do so. The project owner should not be required to write or debug code just to complete ordinary KOVA maintenance.
7. Explain results in plain English. End each task with what changed, what was verified, and any remaining decision that genuinely requires the owner.

## Canonical-system rule

Before creating a new KOVA component, search the repository and documented KOVA repos for an existing equivalent. Consolidate or repair an existing implementation when practical.

Do not create a new repository merely to work around an incomplete existing one.

For cross-repository work, treat `README.md`, `KOVA_REPOS_DOCUMENTATION.md`, and `MULTI_REPO_GUIDE.md` as starting references, then verify the actual current repositories and code before changing them.

## Safety and secrets

- Never commit passwords, API keys, access tokens, OAuth client secrets, recovery codes, private keys, or live credentials.
- Never print secret values into logs, PR descriptions, documentation, test output, or chat summaries.
- Keep real credentials in environment variables or the approved secret store. Commit only safe templates such as `.env.example`.
- If a tracked file appears to contain a real secret, do not repeat the value. Flag the location and replace/remediate it safely when the task allows.
- Do not delete data, repositories, deployments, integrations, or working functionality merely because they look old or duplicated. Establish that they are superseded first.
- Prefer reversible migrations and backups for destructive or structural changes.

## Validation

Use the checks that apply to the files you changed. Existing project checks include:

```bash
python3 scripts/validate_config.py
python3 scripts/test_multi_repo.py
```

For runtime or container changes, also use the relevant Docker/service health checks documented in `README.md` and `SETUP_GUIDE.md` when the environment supports them.

If a check cannot run because a required service, credential, or dependency is unavailable, report that clearly; do not claim it passed.

## Documentation quality

Update documentation when behavior, setup, architecture, repository ownership, or commands change. Keep docs consistent with the code and remove misleading instructions only when a verified replacement exists.

Avoid adding large generated summaries that duplicate existing docs. Prefer improving the canonical document.

## KOVA implementation priorities

When a task is broad, prioritize in this order:

1. Security and secret hygiene.
2. Build/test failures and broken production paths.
3. Canonical architecture and duplicate reduction.
4. Reliable integrations and automation.
5. Deployment, observability, and recovery.
6. Dashboard/user experience.
7. Documentation polish and optional enhancements.

## Completion standard

A task is complete only when the implementation is internally consistent and the relevant checks have been run or explicitly documented as unavailable.

In the final task summary include:

- what changed;
- files or components affected;
- tests/checks run and their results;
- anything still blocked by external credentials, permissions, or an owner-only decision.
