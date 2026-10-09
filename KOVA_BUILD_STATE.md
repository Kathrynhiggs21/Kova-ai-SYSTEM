# KOVA Build State

Last verified: 2026-10-09
Active branch: `chore/continuous-builder-oct9`
Current phase: Cloudflare edge + Railway application-backend migration

## Canonical code

- Core/control plane: `Kathrynhiggs21/Kova-ai-SYSTEM`
- Authenticated web app: `Kathrynhiggs21/kovaos-site`
- AI World remains a separate Drive/provider provenance system and is not copied into Core.

## Verified state

- Core `main` latest verified baseline includes production-evidence commit `a878811`.
- Web `main` includes merged Cloudflare + Railway migration foundation commit `9d43977`.
- Cloudflare account contains a Worker named `kovaos-web`, but it is only a placeholder that returns HTTP 503. It has no assets binding, backend binding, production route, or workers.dev preview enabled.
- Railway now contains a private `kovaos-runtime` project with a staged-only `kovaos-app-backend` service sourced from `Kathrynhiggs21/kovaos-site/main`. Build, start, Railpack, restart, and `/api/health` settings are staged. Environment status confirms zero live services and one pending staged patch. The existing `kova-apps-script-manager` project remains separate and was not repurposed.
- The approved web target is:
  - Cloudflare Worker/static assets for the public edge.
  - Railway persistent Node/Express service for the `kovaos-site` application backend.
  - Same-origin browser API shape through `/api/*`.
- KOVA Core/FastAPI remains a separate control-plane runtime concern and must not be conflated with the web app's Node backend.
- Existing Vercel/Netlify/legacy surfaces are migration/rollback evidence only until the Cloudflare + Railway path is independently verified.

## Current blockers

1. The Railway `kovaos-app-backend` service is staged but not deployed; deployment requires explicit approval.
2. The Cloudflare `kovaos-web` Worker is not a functional preview and has no Railway origin yet.
3. OAuth callback, secure session cookie, protected routes, logout, and `/api/health` have not passed the Cloudflare -> Railway path.
4. Production DNS/provider retirement requires explicit owner approval after preview verification.
5. The shared ChatGPT handoff URL supplied on 2026-10-09 was not fetchable from the connected web reader, so no decisions were imported from it without evidence.

## Next action

The private Railway runtime project/service is staged and ready for review. The next provider action is an explicit deployment approval to commit the staged Railway patch. After a healthy Railway HTTPS origin exists, configure a non-production Cloudflare preview from the repository Worker/static bundle and run the migration smoke-test gate.

## Completion rule

Do not call the migration live until:
- Cloudflare serves the current Vite app;
- `/api/health` reaches Railway successfully;
- protected API calls fail closed anonymously;
- sign-in/callback/session-cookie/logout pass;
- owner routes enforce access;
- rollback is tested;
- only then is production domain cutover approved.
