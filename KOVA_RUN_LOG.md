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

### Next step
Stage a canonical Railway web-runtime project/service without deploying, then prepare Cloudflare preview verification.
