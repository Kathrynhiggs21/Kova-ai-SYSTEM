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

### Next step
Wait for exact-head CI on PR #28. Railway deploy remains explicitly owner-gated; after approval, deploy the staged service, verify `/api/health`, obtain its HTTPS origin, then build the Cloudflare preview.
