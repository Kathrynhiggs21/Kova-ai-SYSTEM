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


## 2026-10-21 — Follow-up on two #145 review threads

- `PRRT_kwDOPrB4Yc6qrVNc`: added explicit stable provider identity, actual granted OAuth/API scopes and completeness fields to the canonical integration matrix. Unknown grants remain UNKNOWN; observed reads, pushes or staging do not establish scope lists. Recorded coordinator-supplied Railway workspace/project IDs, app SLEEPING and MySQL OFFLINE with source/date attribution, not a new provider probe.
- `PRRT_kwDOPrB4Yc6u_G_n`: replaced permanent #145 branch instructions with a current default-branch/PR-state/head/checks selection gate. Retained #145 and its branch as dated provenance. Re-read remote default `main` at `c718831` and the open PR targeting main at `bbc5f4f` before editing.
- Coordinator verified hosted container-smoke, verify-platform, CodeQL and CircleCI success on `bbc5f4fd83692dd111fd583e1000204e69546986`. This does not establish checks on the follow-up commit.
- Documentation-only correction. No PR description/thread-state, merge/closure or provider changes; coordinator owns thread resolution.
- Follow-up validation: all changed Markdown local links/anchors and table widths passed; `git diff --check` passed; `python scripts/validate_config.py` passed with zero errors/warnings. Runtime suites were not rerun for this documentation-only correction.


## 2026-10-21 — Existing second-brain PR #153 consolidation

- Re-read current main `83bb724092344b0eed3a5f1b0182049a246847e6` and the open #153 page/branch at `289380ea44675c2088a50e86cadcc21a93e5e1c4`, including published reviews and earlier safety fixes. Continued only `architecture/second-brain-v1-2026-10-21` and merged main locally without conflicts or reverting its changes.
- Renamed the existing accepted second-brain ADR from the conflicting ADR-004 to next-free ADR-005, updating its heading and current decision/handoff/backlog references. The hosting ADR-004 is preserved.
- Aligned the capability schema with the README's six canonical evidence labels; required evidence for CONNECTED/BROKEN as well as RUNTIME_VERIFIED, enforced complete metadata pairs/nonblank references, and kept UNKNOWN free of current-verification claims. Existing high-risk confirmation guards remain. Documented static-schema limits and pre-merge v1 incompatibilities; no automatic promotions, deployed migration or version-compatibility claim.
- Added Draft 2020-12 schema validation and synthetic accepted/rejected-record checks, with RFC 3339 format assertions and prior memory/timeline review guards. The tests first reproduced 17 failing subcases across 12 tests before correction, then all 12 passed. Schema-validation dependencies are test-only and wired into existing CI/README instructions, not runtime images.
- Preserved the fetched memory/timeline schema contents and all current main deployment/provider configuration. No new architecture, task store, PR, runtime/provider feature, production mutation, review-thread resolution or cross-task message.

### Validation on the #153 consolidation tree

- All three contract schemas pass Draft 2020-12 meta-schema validation with format-aware instance validation in the new tests. All 12 schema/ADR tests pass; the memory/timeline files are byte-identical to the fetched #153 head.
- Core unit suite: 193 passed, no skips, under scoped `umask 022`; platform verification and canonical config validation passed.
- Python app compilation and site JavaScript syntax passed; browser-export tests: 9 passed.
- Changed Markdown local links/anchors/table widths, ADR path/heading uniqueness, workflow YAML and `git diff --check` passed. No stale second-brain ADR-004 paths/headings remain. Dependency consistency passed.
- Hosted checks must be re-read on the pushed head. Provider/runtime evidence validity, freshness and external consumer compatibility are not established by these static tests.
