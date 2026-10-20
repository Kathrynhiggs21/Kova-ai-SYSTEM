# Railway deployment for KOVA Core

This is the deployment contract for the canonical FastAPI Core in `kova-ai/`.
It does not authorize a production cutover, DNS change, secret migration, or deletion
of an existing provider deployment.

## Service settings

- Repository: `Kathrynhiggs21/Kova-ai-SYSTEM`
- Branch: a reviewed production branch, normally `main` after merge
- Root directory / Docker build context: repository root (`/`), not `kova-ai/`
- Build: explicit Railway service settings below; no legacy Config as Code file
- Container: `kova-ai/Dockerfile`
- Health check: `GET /health`
- Runtime port: Railway-provided `PORT`, passed to the container by the start command

## Current Railway configuration (verified October 20, 2026)

[Config as Code](https://docs.railway.com/config-as-code.md) is deprecated:
new services cannot use `railway.toml` or `railway.json`, and existing services
stop reading them on **December 1, 2026**. This repository no longer supplies a
legacy TOML file. Configure the existing intended service in the dashboard:

| Setting | Value |
| --- | --- |
| Root directory / build context | Repository root `/` |
| Builder | Dockerfile |
| Dockerfile path | `kova-ai/Dockerfile` (`RAILWAY_DOCKERFILE_PATH` if needed) |
| Start command override | Leave unset; use the image's PORT-aware command |
| Health check path / timeout | `/health` / 120 seconds |
| Restart policy / maximum retries | On failure / 5 |

Verify these effective settings on the deployment details before starting a
preview; the guide itself does not configure the service. If an existing service
still points to a legacy Config as Code file, reconcile and detach it so that it
cannot override the dashboard settings.

Railway's supported [Infrastructure as Code](https://docs.railway.com/infrastructure-as-code.md)
alternative is `.railway/railway.ts`. For a later owner-approved migration, link
the exact existing project/environment, use `railway config pull` without
`--include-variables` (preserving secrets), inspect `railway config plan`, and
review before any apply. Do not generate a second project or manage one service
with both configuration systems. No IaC apply or provider setting change is part
of this PR.

## Reproducible container verification

From the repository root:

```bash
docker build --file kova-ai/Dockerfile --tag kova-core:local .
docker run --detach --name kova-core-smoke \
  --env PORT=8765 \
  --env POSTGRES_PASSWORD=ci-only-database-password \
  --env KOVA_OWNER_API_KEY=ci-only-owner-key \
  kova-core:local
docker exec -i kova-core-smoke python - < scripts/smoke_core_container.py
docker rm --force kova-core-smoke
```

These are synthetic test values, never production credentials. The smoke check
requires real health JSON on the configured port, a non-root process, anonymous
denial, and owner-authenticated access to the bundled canonical registry. It does
not prove database connectivity or a production deployment. CI runs the same
image build and smoke check in its `container-smoke` job.

Docker Compose uses the same repository-root context via
`docker compose -f kova-ai/docker-compose.yml build api`. The Dockerfile copies
the API, requirements, canonical root registry, and published ZIP archives; `.dockerignore` keeps
local environment files, unpublished archives, and unrelated source out of the build context.

Published `/api/export/site` and `/api/export/images` downloads, plus MCP export
status, use the bundled archives at `/app`. The image works from `/app/kova-ai`
so the existing repository-root resolution remains valid. Local rebuild/Drive
upload is not mounted (`KOVA_EXPORT_UPLOAD_ENABLED=false`): its script, build
inputs, Google SDK and owner-authorized credential workflow are not bundled. Do
not enable it on the minimal image. Non-container/local installations retain
the existing owner-authenticated upload route by default.

## Required configuration

Store real values only in Railway's service variables. At minimum, configure:

- `KOVA_OWNER_API_KEY`
- `KOVA_ALLOWED_ORIGINS` as an exact, environment-specific browser-origin list (see below)
- `DATABASE_URL` when database-backed routes are enabled. Railway's `postgresql://`
  (or `postgres://`) URL is normalized to `postgresql+asyncpg://` before async
  engine creation; existing explicit async URLs and encoded credentials are preserved.
- provider credentials only for the integrations intentionally enabled

Do not copy unused Vercel variables. Rotate a credential if its prior storage or
exposure is uncertain.

## Preview gate

On the isolated staging Railway service, set `KOVA_ALLOWED_ORIGINS` to the
actual Cloudflare preview origin, for example
`https://kovaos-preview.example.workers.dev`. This is an example only: replace it
with the exact approved preview origin, including scheme and any non-default
port, with no path or trailing slash. Do not use `*` or wildcard subdomains.
Restart/redeploy that staging service after changing its variables. Do not add
preview origins to the production service or put the owner API key in browser code.

Before production routing, verify all of the following against the Railway preview URL:

1. `/health` returns HTTP 200.
2. An owner-only route rejects a request without `X-Kova-API-Key`.
3. The same route succeeds with the preview-only owner credential.
4. Browser requests from the Cloudflare preview origin pass CORS.
5. Browser requests from an unapproved origin fail CORS.
6. Logs and error responses contain no credential values.

## Cutover and rollback

At approved production cutover, use the production-only value
`KOVA_ALLOWED_ORIGINS=https://kovaos.com,https://www.kovaos.com` on the production
service. Re-run the browser-origin checks: both production origins must pass,
and the former preview origin and another unapproved origin must be denied.
CORS is a browser policy, not a substitute for owner authentication.

Point the Cloudflare Worker preview at the verified Railway preview first. Production
cutover requires an explicit owner approval and a recorded rollback target. Keep the
last known working route available until the public domain, authentication flow, API
contract, and logout behavior pass end-to-end checks.
