# KOVA Backlog

Updated: 2026-10-09

## P0 — Migration path

### Stage canonical Railway web runtime
Acceptance criteria:
- Create one private Railway project for the `kovaos-site` web runtime.
- Create one application-backend service from `Kathrynhiggs21/kovaos-site`.
- Configure build `corepack pnpm build`, start `corepack pnpm start`, and healthcheck `/api/health`.
- Keep all changes staged until explicit deployment approval.
- Do not copy secret values into GitHub, chat, or docs.

### Make Cloudflare preview real
Acceptance criteria:
- Replace the placeholder `kovaos-web` Worker with the repository Worker and static assets in a non-production preview.
- Configure `BACKEND_ORIGIN` only after Railway provides a verified HTTPS origin.
- Keep production domain routes unchanged until preview smoke tests pass.

### Pass the web migration smoke gate
Acceptance criteria:
- `/` and client routes serve the SPA.
- `/api/health` returns 2xx through Cloudflare to Railway.
- anonymous protected API calls fail closed.
- OAuth start and callback work.
- callback preserves secure session cookie.
- protected pages enforce access.
- logout clears the session.
- rollback target is tested.

## P1 — Control-plane/runtime cleanup

### Reconcile KOVA Core runtime ownership
- Treat `Kova-ai-SYSTEM` FastAPI as a separate control-plane service.
- Choose its long-term host from runtime evidence, not provider build status.
- Verify health and authenticated Core-to-web contract before retiring legacy Core deployments.

### Retire legacy hosting only after cutover
- Keep Vercel, Netlify, GitHub Pages, and Manus surfaces as rollback/migration evidence until replacement is proven.
- Domain reassignment, provider deletion, and destructive unlinking require explicit owner approval.

### Keep current issues/docs aligned
- Update stale Vercel-centric issue text after the Cloudflare + Railway preview is verifiable.
- Keep the KOVA System Registry aligned with live runtime evidence.

## P2 — Continuity

- Maintain `KOVA_BUILD_STATE.md`, `KOVA_BACKLOG.md`, `KOVA_DECISIONS.md`, `KOVA_RUN_LOG.md`, and `KOVA_INTEGRATION_MATRIX.md` in every substantial build session.
- Record only verified state; do not promote plans or URLs to “live”.
