# ADR-004: Cloudflare Edge and Railway Web Runtime

- Status: Accepted migration target
- Date: 2026-10-09
- Supersedes: provider-specific web-host assumptions that treat Vercel, Netlify, GitHub Pages, or Manus as the canonical target

## Decision

The canonical KOVA web application remains sourced from the repository set defined by `kova_repos_config.json`. Its approved target runtime topology is:

1. **Cloudflare** serves the public edge and static web assets.
2. Requests under **`/api/*`** are proxied by the Cloudflare Worker to the persistent Node/Express backend.
3. **Railway** runs that persistent Node/Express backend from the canonical web repository.
4. **KOVA Core/FastAPI** remains a separate control-plane runtime and is not collapsed into the web application's Railway service.
5. Existing Vercel, Netlify, GitHub Pages, and Manus surfaces remain migration/rollback evidence until the replacement path passes the full smoke gate.

The browser keeps one public origin and continues using `/api/*`; it does not receive a second public backend hostname as an application contract.

## Current provider resources

### Cloudflare

- Account: connected KOVA Cloudflare account named `Kovaos`.
- Worker: `kovaos-web`.
- Current evidence: Worker metadata is readable, but the Worker is only a 503 placeholder with no static-assets binding, backend binding, preview subdomain, or production route.
- Write/deploy status: production deployment was not exercised by this build session.

### Railway

- Workspace: connected personal Railway workspace used for KOVA projects.
- Project: private `kovaos-runtime`.
- Environment: `production`.
- Service: staged-only `kovaos-app-backend`.
- Source: `Kathrynhiggs21/kovaos-site`, branch `main`.
- Staged runtime contract:
  - Railpack builder
  - build `corepack pnpm build`
  - start `corepack pnpm start`
  - health check `/api/health`
  - restart on failure
- Current evidence: environment reports zero live services and one pending staged patch. No Railway deployment has been accepted.

## Security and data boundary

### Cloudflare edge record

- Owner/account: KOVA Cloudflare account `Kovaos`.
- Purpose: public TLS/edge/static delivery and same-origin API proxy.
- Data read: incoming HTTP request metadata/body required to serve the SPA or proxy `/api/*`.
- Data written: no KOVA application data is intended to persist at the Worker layer.
- Authorization/scope: connected assistant can read Worker/account metadata; deployment write authority is not treated as proven until an approved deploy succeeds.
- Public configuration: `VITE_OAUTH_PORTAL_URL` and `VITE_APP_ID` are build-time public values.
- Runtime binding: `BACKEND_ORIGIN` points to the verified Railway HTTPS origin after Railway is healthy.
- Secret location: KOVA server secrets do not belong in the browser bundle or GitHub. If Cloudflare-only secrets are ever required, store them in Cloudflare's secret store, never in source.
- Trigger: owner-approved deployment from canonical web source; production routes remain owner-gated.
- Failure behavior: missing/invalid backend origin must fail closed with 503; API failures must not silently fall back to a legacy provider.
- Privacy boundary: proxy only the minimum request/response data needed; do not add content logging or persistence at the edge without a separate reviewed decision.

### Railway web-runtime record

- Owner/account: connected personal Railway workspace used for KOVA; project `kovaos-runtime`.
- Purpose: persistent Node/Express application backend for the canonical web app.
- Data read: authenticated API requests, session cookie, configured external-service responses, and application database state required by enabled routes.
- Data written: application database/audit state only through reviewed routes; no new external write authority is implied by deployment.
- Authorization/scope: staging write access is verified. Deployment execution remains explicitly owner-gated.
- Secret location: Railway service variables/provider secret store. Never copy values into GitHub, chat, registry prose, or Cloudflare public build variables.
- Required server configuration names are documented in the web repository; secret values are not.
- Trigger after cutover: canonical repository source only. Automatic deploy behavior must be rechecked after staged source is committed.
- Failure behavior: deployment must bind the exact Railway `PORT`, pass `/api/health`, and fail closed when required runtime configuration is missing.
- Privacy boundary: the service is private by default until a reviewed public HTTPS origin is intentionally generated for Cloudflare; protected routes must continue to enforce server-side authorization.

## Deployment gate

The staged Railway patch must **not** be accepted merely because its provider configuration exists.

Before approving the first Railway deployment:

1. web PR #28 (exact Railway PORT binding) must be merged into the canonical web default branch;
2. the current default-branch commit must be re-read and recorded;
3. the staged Railway source must be confirmed to resolve to that commit, or be re-staged/pinned to the verified commit;
4. required runtime configuration names must be present in the Railway secret store without exposing their values;
5. only then may the owner explicitly approve accepting the staged deployment.

After deployment, verify `/api/health`, obtain the Railway HTTPS origin, and only then build a non-production Cloudflare preview.

Production DNS/domain changes remain a separate explicit approval after the full authentication/API/rollback smoke gate passes.

## Evidence rule

A configured provider resource, successful build, alias, staged patch, or deployment dashboard is not proof that KOVA is live. Record runtime status only from the exact path being claimed.
