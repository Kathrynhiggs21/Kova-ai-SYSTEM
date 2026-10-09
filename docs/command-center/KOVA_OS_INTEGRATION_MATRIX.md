# KOVA OS Integration Matrix

## Evidence states

- **Runtime verified** - a current KOVA production read or write/readback succeeded through the intended runtime.
- **Assistant access** - the connected assistant can reach the service, but KOVA runtime integration is not proven.
- **Configured** - provider/resource configuration exists; end-to-end runtime behavior is not proven.
- **Designed** - a specification or adapter boundary exists.
- **Staged** - provider changes are prepared but not committed/live.
- **Blocked** - access, deployment, security, or an owner decision is required.
- **Disabled** - intentionally excluded from the active runtime.

Configuration, a successful build, an alias, or assistant access alone is never proof of runtime health.

| Integration | Current evidence | KOVA role | Next proof |
|---|---|---|---|
| GitHub | Assistant access; active repository reads/writes and current CI evidence verified | Code, PRs, CI, release evidence | Keep active-set and deployment evidence aligned with current default branches |
| KOVA repository active set | Machine-readable authority is `kova_repos_config.json` entries whose `enabled` value is `true` | Repository ownership boundary | Derive status from the registry; do not maintain a second active-pair list here |
| Cloudflare | Assistant access; account contains `kovaos-web`, but live metadata shows a 503 placeholder with no assets binding, backend binding, preview subdomain, or production route | Target public edge/static delivery and same-origin `/api/*` proxy | Publish a non-production preview from canonical `kovaos-site` after Railway provides a verified HTTPS origin |
| Railway | Assistant access; private `kovaos-runtime` project exists and `kovaos-app-backend` source/config are staged; environment reports zero live services and one pending patch | Target persistent Node/Express backend for `kovaos-site` | Explicit deployment approval, then verify `/api/health` and obtain HTTPS origin |
| KOVA Core runtime | Source and historical Vercel probes exist; long-term host ownership is still under reconciliation | FastAPI control plane, orchestration, MCP, shared services | Verify health plus authenticated Core-to-web contract on the intended runtime before promoting/retiring providers |
| Google Drive | Assistant access; KOVA runtime integration remains unverified | Canonical user files and private registry | Run a current KOVA-runtime metadata readback through the intended runtime with no source mutation |
| AI World | Assistant access to separate Drive root/registry; it is not KOVA Core storage | AI-provider/provenance system | Keep linked by stable ID/URL; verify each runtime automation independently |
| Gmail | Assistant access; KOVA runtime unverified | Triage and approved drafts/actions | Prove least-privilege runtime read, then approved send flow |
| Google Calendar | Assistant access; KOVA runtime unverified | Agenda, conflicts, reminders | Prove runtime read and approved event creation/readback |
| Notion | Assistant access; KOVA runtime unverified | Human-readable view only | Verify one canonical view without duplicate masters |
| OpenAI/model providers | Designed / provider-neutral boundary exists | AI Assistant | Prove one authenticated runtime provider route with logging and failure behavior |
| MCP | Implemented in Core; production call unverified | Standard owner-authenticated tool interface | Verify initialize/tool call on intended Core runtime |
| Zapier/Make/n8n | Optional fallback | Cross-app bridge only where direct routes are insufficient | Enable only a named workflow with evidence and bounded scope |
| Vercel | Historical/current migration surfaces exist; not the approved target topology | Rollback/migration evidence | Retain until Cloudflare + Railway passes preview and production cutover gates |
| Netlify / GitHub Pages / Manus | Legacy public/migration surfaces | Rollback or migration evidence only | Retire only after verified replacement, traffic/rollback review, and owner approval |

## Deployment target security records

These records are required before either target can be promoted from assistant-accessible/configured state to runtime-verified.

### Cloudflare — `kovaos-web`

- **Owner/account:** connected KOVA Cloudflare account `Kovaos`.
- **Purpose:** public TLS/edge/static delivery and same-origin proxy for `/api/*`.
- **Data read:** incoming HTTP request metadata/body needed to serve the SPA or proxy API calls.
- **Data written:** no KOVA application data is intended to persist at the Worker layer.
- **Authorization/scope:** assistant metadata read access verified; production deployment write authority is not treated as proven until an approved deploy succeeds.
- **Public build configuration:** `VITE_OAUTH_PORTAL_URL`, `VITE_APP_ID`.
- **Runtime binding:** `BACKEND_ORIGIN` only after Railway has a verified healthy HTTPS origin.
- **Secret location:** Cloudflare secret store only for future edge-only secrets; server secrets stay out of the browser bundle and Git.
- **Trigger:** owner-approved deploy from canonical web source; production route/DNS changes remain separately owner-gated.
- **Failure behavior:** missing or invalid backend origin returns 503; no silent fallback to legacy providers.
- **Privacy boundary:** pass through only request/response data needed for delivery/proxying; no content persistence or new logging without review.
- **Current evidence:** Worker exists but remains a 503 placeholder with no asset/backend binding, preview subdomain, or production route.

### Railway — `kovaos-runtime / kovaos-app-backend`

- **Owner/account:** connected personal Railway workspace used for KOVA; project `kovaos-runtime`.
- **Purpose:** persistent Node/Express backend for the canonical web application.
- **Data read:** authenticated API requests, session cookie, configured service responses, and application database state used by enabled routes.
- **Data written:** application database/audit state only through reviewed routes; deployment grants no new external-write authority by itself.
- **Authorization/scope:** staging write access verified; deployment execution not exercised and remains explicitly owner-gated.
- **Secret location:** Railway service variables/provider secret store. Values must not be copied into GitHub, chat, or registry prose.
- **Trigger:** canonical repository source only after the staged patch is accepted; automatic deploy behavior must be rechecked at that time.
- **Failure behavior:** bind exact Railway `PORT`, require `/api/health`, and fail closed when required runtime configuration is absent.
- **Privacy boundary:** project/service stays private until a reviewed HTTPS origin is intentionally created for Cloudflare; protected routes retain server-side authorization.
- **Current evidence:** source/build/start/health configuration is staged; Railway environment reports zero live services and one pending patch.

See ADR-004 for the deployment and production-cutover gate.

## Build rule

Before any integration is promoted to runtime-verified, record owner/account, purpose, data read, data written, OAuth/API scope, secret location, trigger, failure behavior, privacy boundary, and current verification evidence. Cloudflare and Railway records are complete above for the current staged migration; assistant-only integrations remain unverified until their own records and runtime proofs exist.

## Priority order

1. Cloudflare + Railway preview path
2. authenticated web migration smoke gate
3. Core runtime ownership and Core-to-web contract
4. one AI provider
5. Drive metadata registry runtime readback
6. Calendar and Gmail
7. optional bridges only where a direct connector cannot do the job
