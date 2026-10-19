# Railway deployment for KOVA Core

This is the deployment contract for the canonical FastAPI Core in `kova-ai/`.
It does not authorize a production cutover, DNS change, secret migration, or deletion
of an existing provider deployment.

## Service settings

- Repository: `Kathrynhiggs21/Kova-ai-SYSTEM`
- Branch: a reviewed production branch, normally `main` after merge
- Build: repository `railway.toml`
- Container: `kova-ai/Dockerfile`
- Health check: `GET /health`
- Runtime port: Railway-provided `PORT`, passed to the container by the start command

## Required configuration

Store real values only in Railway's service variables. At minimum, configure:

- `KOVA_OWNER_API_KEY`
- `KOVA_ALLOWED_ORIGINS=https://kovaos.com,https://www.kovaos.com`
- `DATABASE_URL` when database-backed routes are enabled
- provider credentials only for the integrations intentionally enabled

Do not copy unused Vercel variables. Rotate a credential if its prior storage or
exposure is uncertain.

## Preview gate

Before production routing, verify all of the following against the Railway preview URL:

1. `/health` returns HTTP 200.
2. An owner-only route rejects a request without `X-Kova-API-Key`.
3. The same route succeeds with the preview-only owner credential.
4. Browser requests from the Cloudflare preview origin pass CORS.
5. Browser requests from an unapproved origin fail CORS.
6. Logs and error responses contain no credential values.

## Cutover and rollback

Point the Cloudflare Worker preview at the verified Railway preview first. Production
cutover requires an explicit owner approval and a recorded rollback target. Keep the
last known working route available until the public domain, authentication flow, API
contract, and logout behavior pass end-to-end checks.
