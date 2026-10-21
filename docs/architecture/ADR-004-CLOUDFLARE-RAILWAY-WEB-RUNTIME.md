# ADR-004: Cloudflare Edge and Railway Web Runtime

- Status: Accepted migration target
- Date: 2026-10-09
- Reviewed: 2026-10-21 against current main; provider observations below remain dated
- Supersedes: provider-specific web-host assumptions that treat Vercel, Netlify, GitHub Pages, or Manus as the canonical target

## Decision

The canonical KOVA web application remains sourced from the repository set defined by `kova_repos_config.json`. Its approved target runtime topology is:

1. **Cloudflare** serves the public edge and static web assets.
2. Requests under **`/api/*`** are proxied by the Cloudflare Worker to the persistent Node/Express backend.
3. **Railway** runs that persistent Node/Express backend from the canonical web repository.
4. **KOVA Core/FastAPI** remains a separate control-plane runtime and is not collapsed into the web application's Railway service.
5. Vercel is retired under the October 19 decision on current main. It is not a deployment or rollback target. Other legacy observations are historical evidence, not authorization to restore an old provider.

The browser keeps one public origin and continues using `/api/*`; it does not receive a second public backend hostname as an application contract.

## Dated provider observations — October 9, 2026

The following resource snapshot explains the original migration work. It is not current provider state. The [README October 19 baseline](../../README.md#current-production-baseline) records a later healthy/sleeping Railway web backend and Vercel retirement. Cloudflare placeholder status and the old zero-live-service count were not reverified on October 21.

### Cloudflare

- Account: connected KOVA Cloudflare account named `Kovaos`.
- Worker: `kovaos-web`.
- October 9 evidence: Worker metadata is readable, but the Worker is only a 503 placeholder with no static-assets binding, backend binding, preview subdomain, or production route.
- Write/deploy status: production deployment was not exercised by this build session.

### Railway

- Workspace: connected personal Railway workspace used for KOVA projects.
- Project: private `kovaos-runtime`.
- Environment: `production`.
- Service on October 9: staged-only `kovaos-app-backend`; superseded by the later README observation.
- Source: `Kathrynhiggs21/kovaos-site`, branch `main`.
- Staged runtime contract:
  - Railpack builder
  - build `corepack pnpm build`
  - start `corepack pnpm start`
  - health check `/api/health`
  - restart on failure
- October 9 evidence: environment reports zero live services and one pending staged patch. No Railway deployment has been accepted.

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
- Authorization/scope: staging write access was recorded on October 9. This session does not establish current provider access; deployment execution remains explicitly owner-gated.
- Secret location: Railway service variables/provider secret store. Never copy values into GitHub, chat, registry prose, or Cloudflare public build variables.
- Required server configuration names are documented in the web repository; secret values are not.
- Trigger after cutover: canonical repository source only. Automatic deploy behavior must be rechecked after staged source is committed.
- Failure behavior: deployment must bind the exact Railway `PORT`, pass `/api/health`, and fail closed when required runtime configuration is missing.
- Privacy boundary: the service is private by default until a reviewed public HTTPS origin is intentionally generated for Cloudflare; protected routes must continue to enforce server-side authorization.

## Historical first-deployment gate — October 9, 2026

This was the gate at the time of staging, not a claim that Railway remains undeployed or web #28 remains open. Re-read exact source and current provider evidence before a separately authorized deployment. Do not replay this historical staging workflow.

The staged Railway patch must **not** be accepted merely because its provider configuration exists.

Before approving the first Railway deployment:

1. web PR #28 (exact Railway PORT binding) must be merged into the canonical web default branch;
2. the current default-branch commit must be re-read and recorded;
3. the staged Railway source must be confirmed to resolve to that commit, or be re-staged/pinned to the verified commit;
4. required runtime configuration names must be present in the Railway secret store without exposing their values;
5. only then may the owner explicitly approve accepting the staged deployment.

After deployment, verify `/api/health`, obtain the Railway HTTPS origin, and only then build a non-production Cloudflare preview.

Production DNS/domain changes remain a separate explicit approval after the full authentication/API/rollback smoke gate passes.

## Current acceptance boundary

Cloudflare edge/static delivery and Railway persistent services remain the target. Core/FastAPI remains separate from the web Node/Express service. Follow the [canonical web guide](https://github.com/Kathrynhiggs21/kovaos-site/blob/main/docs/deployment/cloudflare-railway.md) and [Core Railway contract](../deployment/railway-core.md). Require health JSON, authenticated login/callback/cookies, anonymous denial, protected routes, logout and persistence on the exact path claimed. A rollback must use reviewed canonical source and the current hosting path; it must not reactivate Vercel.

This pass changes source/documentation only: no provider deployment, billing, DNS, secrets, access or production data changes. Source review links, including domain-isolation web #38, are preserved in [the handoff](../HANDOFF.md#preserved-source-links); they do not establish domain ownership or production cutover.

## Evidence rule

A configured provider resource, successful build, alias, staged patch, or deployment dashboard is not proof that KOVA is live. Record runtime status only from the exact path being claimed.
