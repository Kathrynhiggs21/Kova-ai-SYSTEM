# KOVA Temporal synthetic pilot (not deployed)

Isolated TypeScript proof of concept in KOVA's canonical orchestration repository. This does not replace CORE's BullMQ, install a Temporal server, or change KOVA authentication. It has **no production permissions** and starts only when `KOVA_TEMPORAL_PILOT=enabled`.

## Purpose
- Submit a synthetic task with a stable workflow ID.
- Pause until an explicit `approve` signal.
- Execute a deterministic workflow and a separately retried activity.
- Record completion via Temporal's workflow history.
- Verify persistence/restart and retries in a test environment before evaluating production.

## Local development only
Requires Node.js and a running Temporal development server. In this folder, install dependencies with `npm install`, run `npm run check`, start a dev Temporal server using the verified CLI, then launch `KOVA_TEMPORAL_PILOT=enabled npm run worker` and `KOVA_TEMPORAL_PILOT=enabled npm run start` in separate terminals. The workflow waits for an approval signal; use the Temporal CLI's documented signal operation for `approve`. The dev server is never for production.

## Production design decisions pending
- CORE already has BullMQ and Redis. Compare restart/retry/approval behavior before adopting Temporal.
- For Temporal Cloud use namespace and API-key configuration through secure secret storage; this sample is intentionally local-only and lacks Cloud TLS/API-key wiring.
- Use a protected KOVA API to authorize signals; never expose Temporal admin endpoints to a browser.
- WorkOS/Auth0 are not configured by this pilot. `kova-auth` Auth0 tenant onboarding must be verified separately; do not point the legacy Manus-specific `OAUTH_SERVER_URL` at Auth0.
- Do not pass real personal records into workflow histories; store private data in KOVA's protected store and pass references.
- Before merging or deploying: dependency installation, typecheck, workflow tests, cancellation/restart tests, and security review. No tests executed in this connector-only session.
