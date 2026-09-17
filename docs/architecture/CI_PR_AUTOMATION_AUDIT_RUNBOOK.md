# CI/PR Automation Audit Runbook (KOVA Core)

## Repository role and scope
- Classification: **ACTIVE CORE** (`Kova-ai-SYSTEM`).
- Scope of this runbook: repository-local CI and PR automation safety for canonical KOVA Core.

## Verified current automation state
- GitHub Actions workflow file: `.github/workflows/ci.yml`
  - Workflow name: `CI`
  - Job ID (and emitted check name): **`verify-platform`**
  - This is the only verified GitHub Actions CI check-name candidate to require today.
- CircleCI workflow file: `.circleci/config.yml`
  - External context: `build-test-deploy` (plus a commit-specific variant in CircleCI/GitHub checks)
  - Sub-jobs: `build-and-test`, `lint-check`, `security-scan`
  - `lint-check` and `security-scan` currently mask failures with `|| echo ...`, so they are informational/non-gating in practice.

## Verified absent repository-file automation
- No `.mergify.yml` or `mergify.yml`
- No `.github/dependabot.yml`
- No `renovate.json`
- No repository-file auto-merge path is currently configured.

## Branch protection / ruleset recommendations (GitHub-native)
1. Require deterministic checks only, by exact verified names.
2. For now, require only: **`verify-platform`**.
3. Keep CircleCI contexts non-required until owner-approved migration/retirement is complete.
4. Do not require external deployment, Codex, or CodeQL contexts until their trigger/scope/stability are explicitly confirmed for this repo.
5. Keep direct-push protections on `main` and require PR review per owner policy.

## Safety policy for future merge automation
- Preserve a `do-not-merge` safety mechanism.
- If any future auto-merge path is introduced, it **must** block when the `do-not-merge` label is present.

## P1 owner/settings decision (not changed in this PR)
- Do **not** remove or harden `.circleci/config.yml` in this change set.
- CircleCI failure-masking removal can flip currently green commits to red and needs an owner-approved transition plan plus branch-protection update window.
