# KOVA Run Log

## 2026-10-09 — Continuous Builder resume (historical)

This entry records that session only. Its staged-only Railway and pending web #28 claims are superseded where later source evidence disagrees; see the October 21 entry.

### Evidence reviewed
- Canonical Core and web repository state.
- Latest merged Core production-baseline evidence.
- Latest merged Cloudflare + Railway migration foundation in `kovaos-site`.
- Cloudflare live account and Worker metadata.
- Railway live project inventory.
- Open GitHub issues and pull requests.

### Findings
- Core did not yet contain the Continuous Builder durable state files.
- Core README still described Vercel as the canonical deployment host even though the web repo had moved to a Cloudflare + Railway target.
- Cloudflare `kovaos-web` exists but is a 503 placeholder with no assets, backend binding, preview subdomain, or production route.
- Railway is connected but no canonical KOVA web-runtime project exists.
- Existing Railway `kova-apps-script-manager` is unrelated to the web runtime and must not be reused.

### Changes in this branch
- Initialized the five Continuous Builder durable files.
- Updated Core hosting language to match the approved migration target.
- Recorded blockers and the next safe migration step.

### Tests
- Documentation/state-only batch. No runtime test claimed.
- GitHub CI must pass before merge.

### Provider staging completed
- Created private Railway project `kovaos-runtime`.
- Staged `kovaos-app-backend` from `Kathrynhiggs21/kovaos-site/main`.
- Staged Railpack build, `corepack pnpm build`, `corepack pnpm start`, `/api/health`, and restart policy.
- Verified the Railway environment has zero live services and one pending staged patch; nothing was deployed.

### Web hardening started
- Opened `kovaos-site` PR #28 to bind the exact Railway `PORT` in production, retain local development fallback, and add focused tests.

### Deployment precondition from review

The staged Railway service follows `kovaos-site/main`, but the required exact-PORT hardening is still in web PR #28. Green PR-head CI does not put that fix on `main`.

Do **not** accept the Railway staged deployment until:
1. PR #28 is merged into the canonical web default branch;
2. the new default-branch commit is read back;
3. the staged Railway source is confirmed to resolve to that commit, or is re-staged/pinned to the verified commit.

### Next step

Keep Railway staged and undeployed. Web PR #28 is green and review-clean but still requires explicit merge approval. After it is merged and the staged source revision is verified, Railway deployment remains a separate explicit owner approval.


## 2026-10-21 — Core continuity consolidation

- Inspected AGENTS.md, README, repository map/module policy, main `c718831`, six fetched PR heads and their public checks pages. `docs/HANDOFF.md` did not exist; added a navigation/audit entry.
- Continued existing #145 branch. Incorporated current main, preserving its security fixes, Railway Core contract and Vercel retirement. No PR was closed or merged on GitHub.
- Consolidated #146's unique auth, CORE, memory and connector tasks into the backlog; retained #151's deployment/auth/domain source links without importing stale private-Sites or Vercel-rollback claims.
- Reproduced 11 failures in the 26-test config-validator suite under the platform's empty `/tmp/.git` marker. Added a deterministic regression (12 failures out of 27 before fix); require HEAD metadata for directory checkout markers. All 27 then passed without the old `/var/tmp` workaround.
- Updated README, state/backlog, hosting ADR and guide to distinguish dated provider evidence from current source policy. Preserved original #145 provider-metadata provenance in the handoff.
- GitHub REST/GraphQL reads returned `Forbidden`; Git refs and public PR/checks pages were readable. Original-head Core CI passed for all six PRs; legacy Vercel deployment errors are separate. Updated-head CI still requires rechecking after push.
- No deployment, billing, DNS, secrets, access, production-data or cross-task messaging changes.

### Validation on the consolidated tree

- `bash verify_platform.sh`: passed (27 validator tests included).
- `python scripts/validate_config.py`: passed against the canonical configuration.
- `(umask 022; PYTHONPATH=kova-ai python -m unittest discover -s tests -p "test_*.py" -v)`: 181 passed using normal `/tmp`, no skipped tests.
- `python -m compileall -q kova-ai/app`, `node --check site/app.js`: passed.
- `node --test tests/test_site_exports.js`: 9 passed.
- `git diff --check`: passed. Container and live-provider checks were not rerun for this validator/documentation change.
