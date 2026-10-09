# KOVA Run Log

## 2026-10-09 — Continuous Builder resume

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
