# KOVA OS — Runtime Integration Gate (2026-10-10)

## Scope
Read-only evidence from authorized Railway/GitHub/WorkOS connections. No secrets copied, no production configuration changed.

## Verified Railway
Project `kova-apps-script-manager`, production:
- `core` image `redplanethq/core:0.7.20`: online, 1/1 replica, no recent failures.
- `Postgres` image `pgvector/pgvector:pg18-trixie`: online, mounted volume.
- `neo4j` image `redplanethq/neo4j:0.1.0`: online, mounted volume.
- `Redis` image `redis:8.2.1`: online, mounted volume.
- `function-bun`: sleeping, not a verified active worker.
- CORE deploy logs showed BullMQ queues initialized, with zero active/waiting/completed tasks in sampled reporting. This does NOT prove cross-chat execution.
- CORE service contains database, graph, queue, and session variable **names**, but values and successful authenticated operations were not inspected. Do not infer connectivity from variable names.

Project `kovaos-runtime`, production:
- `kovaos-app-backend` built from `Kathrynhiggs21/kovaos-site` `main`: online, 1/1 replica, Railway healthcheck configured at `/api/health`.
- Its Railway variable names list is empty. Boot logs report: `OAUTH_SERVER_URL is not configured!` and the server nevertheless starts listening. Running is not equivalent to owner-authenticated readiness.

## WorkOS
The connected OAuth identity responds, but WorkOS says no dashboard account backs this login; no operations are presently available. Do not switch auth provider or provision a new account without determining the intended owner/workspace and migration.

## Security
- KOVA is a private owner OS. `Kova-ai-SYSTEM` is currently GitHub-visible as PUBLIC (source visibility, not evidence that personal records are published); `kovaos-site` is PRIVATE.
- Never access or import Google password files. Do not store passwords in GitHub, prompts, plugin packages, logs, or task records. Use authorized OAuth/secret-manager connections.
- CORE's upstream license includes AGPLv3 and Commons Clause language: security/license review required before redistribution/modifications.
- Do not activate family-record ingestion or unrestricted external actions without audited private auth and scoped access.

## Ordered next implementation gates
1. Read `AGENTS.md`, current auth and server bootstrap, source registry, latest PRs and tests; reconcile conflicting historical branch snapshots.
2. Confirm owner-authenticated `kovaos-app-backend` health, OAuth callback configuration and fail-closed behavior. Repair missing `OAUTH_SERVER_URL` only after verifying the actual intended provider and host-secret configuration.
3. Verify CORE authenticated endpoints, queues, DB/Neo4j/Redis connectivity with synthetic records; no private ingestion during pilot.
4. Write and test a narrow KOVA-to-CORE adapter with temporal provenance + approval-gated actions on a feature branch; avoid cross-repo duplication.
5. Activate durable overnight task execution only after a deployed runner/trigger, scoped credentials, limits, testing and audit evidence are verified.

## Session checks
Railway environment-status and describe-service: performed 2026-10-10 (connector reads).
Railway deploy logs: reviewed; auth configuration error observed.
WorkOS whoami: checked, account not set up.
No application tests executed in this session; no production writes.
