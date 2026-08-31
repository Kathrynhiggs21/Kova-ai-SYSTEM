# KOVA OS — Codex Start Here

This is the first operating mission for Codex when beginning a new KOVA OS cleanup/build session.

## Objective

Turn `Kova-ai-SYSTEM` into the reliable canonical KOVA OS command center without creating another parallel KOVA implementation.

## First-pass mission

1. Read the root `AGENTS.md` and `README.md`.
2. Inspect the repository tree and identify the actual application entry points, services, scripts, CI configuration, deployment configuration, and active documentation.
3. Compare documented KOVA repositories with the current code/configuration. Flag stale names or duplicated responsibilities rather than assuming the docs are current.
4. Run the safe repository validation checks that are available without live secrets.
5. Identify:
   - broken or failing paths;
   - duplicate implementations;
   - obsolete documentation or configuration;
   - secret-management risks;
   - deployment/CI gaps;
   - integration stubs that are presented as complete but are not actually connected.
6. Produce a short prioritized plan using these buckets:
   - P0 — security/data-loss risk;
   - P1 — broken core functionality;
   - P2 — consolidation and reliability;
   - P3 — UX, automation, and polish.
7. Begin with the highest-value safe P0/P1 item that can be completed and verified in the current environment.

## Working rules

- Do not require the owner to write code for ordinary implementation work.
- Do not expose or invent credentials.
- Do not add a new repository or framework just because an existing component is messy.
- Prefer fixing the canonical path and deleting nothing until its replacement is verified.
- Use existing tests and add focused tests when changing behavior.
- Keep commits small enough to review and roll back.

## Useful existing checks

Start with these when their dependencies are available:

```bash
python3 scripts/validate_config.py
python3 scripts/test_multi_repo.py
```

For container/runtime work, follow the current commands documented in `README.md` and `SETUP_GUIDE.md` after verifying that the files and commands still exist.

## Definition of a useful Codex session

A session should end with at least one of the following, not merely another strategy document:

- a verified bug fix;
- a working integration improvement;
- a security/secret-hygiene repair;
- a duplicate-path consolidation;
- a build/test/deployment repair;
- a concrete, tested UX improvement.

Always summarize what was actually changed and verified separately from what is merely proposed.
