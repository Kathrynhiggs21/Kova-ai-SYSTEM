# Railway deployment for KOVA Core

This is the deployment contract for the canonical FastAPI Core in `kova-ai/`.
It does not authorize a production cutover, DNS change, secret migration, or deletion
of an existing provider deployment.

## Service settings

- Repository: `Kathrynhiggs21/Kova-ai-SYSTEM`
- Branch: a reviewed production branch, normally `main` after merge
- Root directory / Docker build context: repository root (`/`), not `kova-ai/`
- Build: repository `railway.toml`
- Container: `kova-ai/Dockerfile`
- Health check: `GET /health`
- Runtime port: Railway-provided `PORT`, passed to the container by the start command

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
only the API, requirements, and canonical root registry; `.dockerignore` keeps
local environment files, archives, and unrelated source out of the build context.

## Required configuration

Store real values only in Railway's service variables. At minimum, configure:

- `KOVA_OWNER_API_KEY`
- `KOVA_ALLOWED_ORIGINS` as an exact, environment-specific browser-origin list (see below)
- `DATABASE_URL` when database-backed routes are enabled
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

