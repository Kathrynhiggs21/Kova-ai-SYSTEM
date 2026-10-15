# KOVA OS — CORE self-hosting and runtime integration gate

## Accepted decision — October 15, 2026

Use the official RedPlanetHQ CORE as a separately versioned, self-hosted service on Katy’s existing Railway infrastructure. KOVA owns identity, authorization, original-source references, and its action ledger. CORE is a replaceable memory/task provider behind `KovaCoreAdapter`; it is not the authority for KOVA permissions or family records. No duplicate deployment or fork is needed.

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


## October 15 read-only reconciliation

The Railway connector now works; the earlier browser sign-in blocker is superseded.
Both connected Railway entries returned the same four projects. Only the two KOVA
projects were inspected further.

| Component | Observed source | Current provider evidence |
| --- | --- | --- |
| CORE | `redplanethq/core:0.7.20` | Online, 1/1 running; deployed October 9 |
| PostgreSQL | `pgvector/pgvector:pg18-trixie` | Online, persistent volume |
| Neo4j | `redplanethq/neo4j:0.1.0` | Online, persistent volume |
| Redis | `redis:8.2.1` | Online, persistent volume |
| Bun function | `ghcr.io/railwayapp/function-bun:1.4.0` | Sleeping; execution not verified |
| KOVA web backend | `Kathrynhiggs21/kovaos-site@main` | Successful deployment October 13; service variable-name list still empty |

CORE's environment reported zero warnings, critical alerts, or failures in the
8-hour window, and no pending patch. An unauthenticated HTTPS request to the
existing CORE domain redirected to `/login`; the login page returned HTTP 200.
This proves reachability, not account ownership, AI-provider readiness, memory
processing, or agent execution. No login link, token, or secret was retrieved.

The upstream Git tag `0.7.20` resolves to commit
`4a5b18d8db55d66e5dfda41b18461f359b340c42`. This records the tag's source mapping;
it does not prove the running image digest or build provenance. Existing image
tags were observed, not changed. Immutable image digests, SBOM/container scans,
backup/restore verification, and source-to-image provenance remain outstanding.

## Adapter pilot

`kova-ai/app/integrations/core_adapter.py` implements MemoryPort, TaskPort,
ToolPort and HealthPort behind KOVA authorization callbacks. It is server-only,
not registered on a public route, and disabled by default. No upstream CORE
source was copied or modified.

- The pilot generates a fixed imaginary memory fixture; it cannot ingest caller
  text or real records. Read methods require KOVA resource authorization.
- Each outbound operation checks `/api/v1/me` against the configured dedicated
  synthetic workspace. Provider tokens and identity/profile data are not returned.
- Memory creation maps to `/api/v1/add`. Its response means **queued**, not stored
  or recalled. Session readback uses `/api/v1/episodes/session/:sessionId`; it
  verifies fixture ingestion, not temporal-graph retrieval quality.
- Task creation/readback maps to `/api/v1/tasks` and `/api/v1/tasks/:taskId`.
  Task writes require a separate runtime gate and a server-owned, consumed owner
  approval. The fixed test task is created as `Done`, without schedule input.
  **This alone does not guarantee no execution:** upstream task creation invokes
  `detectAndApplyRecurrence` even without a schedule. Keep task writes disabled
  until a dedicated synthetic workspace has no external connectors/gateway,
  recurrence side effects are controlled, and model spending is approved.
- Tool execution is always blocked in this pilot, including high-impact tests.
- Intent and result events use the existing agent-ledger schema. A failed intent
  write prevents network activity. The host must supply a durable sink; tests use
  an in-memory sink. A failed result write or uncertain network outcome requires
  reconciliation; no automatic retries or exactly-once claim is made.
- HTTPS origin configuration is server-owned; redirects are rejected, requests
  time out, provider error bodies are suppressed, and optional features do not
  silently fall back to CORE Cloud or Manus.

### Configuration contract (names only)

Keep these in the KOVA control-plane runtime secret/config store, never `VITE_*`:
`KOVA_CORE_ORIGIN`, `KOVA_CORE_TOKEN`, `KOVA_CORE_SYNTHETIC_WORKSPACE_ID`,
`KOVA_CORE_ENABLED`, `KOVA_CORE_TASK_WRITES_ENABLED`. No automatic environment
loader or application route is wired yet: the host must construct CoreConfig,
pass its authoritative authorization/approval services, and its durable ledger
sink. Both enable flags default to false. Do not place these on the web frontend.

### Remaining activation gates

1. Confirm Katy's CORE account and dedicated synthetic workspace through the
   existing login page; enter provider credentials in CORE's own protected setup.
   Do not paste credentials into chat or GitHub.
2. Configure a server-side CORE token and validate the expected workspace; supply
   KOVA's existing authenticated principal and resource authorization to the
   adapter. Restore the web backend's own authentication configuration separately.
3. Finish immutable image provenance and dependency/container review before
   enabling adapter writes. Preserve current deployment as rollback evidence.
4. Attach the durable KOVA ledger sink and verify a synthetic memory queued,
   processed and read back. Graph recall still needs its own acceptance test.
5. Resolve task recurrence/execution isolation; then approve and run a synthetic
   task roundtrip. Verify Scratchpad pickup separately. Never equate a created
   `Done` fixture with agent execution.
6. Only after the independent gates pass: connect approved Gmail, Calendar, and
   Drive read-only. Family-record ingestion remains disabled.

Any deployment, new infrastructure, or spending action still needs Katy's
explicit go under the October 15 setup plan. No such action was performed here.
The optional Claude gateway sign-in remains an owner account action and was not
installed or started.

### Sources

- [Official CORE repository](https://github.com/RedPlanetHQ/core)
- [Self-hosting overview](https://docs.getcore.me/self-hosting/overview)
- [Pinned API routes](https://github.com/RedPlanetHQ/core/tree/4a5b18d8db55d66e5dfda41b18461f359b340c42/apps/webapp/app/routes)
- [Pinned recurrence behavior](https://github.com/RedPlanetHQ/core/blob/4a5b18d8db55d66e5dfda41b18461f359b340c42/apps/webapp/app/services/tasks/recurrence.server.ts)
- [Web runtime configuration PR](https://github.com/Kathrynhiggs21/kovaos-site/pull/32)
- The separate web authentication-readiness PR #33 remains draft and unmerged;
  its configuration checker is not proof of a working login or a deployed gate.

This record supersedes the October 10 readiness observations above where a
fresh read is explicitly recorded; historical WorkOS/log claims were not retested.


### Local validation on October 15

- Reconciled with control-plane main `66752ad41d5e0681ea534ead0d2bf389b3be70dc`,
  preserving the newer database and runtime-security fixes.
- Python unit suite: 190 passed, including 12 new CORE adapter tests. All CORE
  memory/task tests use an HTTP mock, not the live Railway service.
- Repository configuration validation: passed, zero errors or warnings.
- New adapter and test formatting: Black passed.
- Live authenticated multi-repository smoke test requires a running local API
  and owner key; it is not an integration proof for CORE.
- No authenticated CORE memory/task operation, Scratchpad pickup, image scan,
  production deployment, or real-source import was performed.
