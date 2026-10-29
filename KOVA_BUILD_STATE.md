# KOVA Build State

Reviewed: 2026-10-21. Repository and local-development evidence only; this session did not inspect or change production providers.

## Canonical ownership

- Core/control plane: `Kathrynhiggs21/Kova-ai-SYSTEM`.
- Authenticated web app: `Kathrynhiggs21/kovaos-site` (React/Vite, Express/tRPC, Drizzle/MySQL).
- Google Drive owns user documents. AI World remains separate; link by stable reference.
- Cloudflare edge/static delivery + Railway persistent services is the current hosting target. Core/FastAPI and the web Node backend retain separate contracts.
- Legacy one-click hosting is retired. Do not restore it as a deployment, fallback, credential requirement, or source of truth.

## Verified source state

- Current main re-read at `83bb724092344b0eed3a5f1b0182049a246847e6`, merging #145. Continued only the authorized open #153 branch `architecture/second-brain-v1-2026-10-21` from fetched head `289380ea44675c2088a50e86cadcc21a93e5e1c4`; these are dated observations, subject to the handoff selection gate.
- #153 now preserves the hosting ADR-004 and uses [ADR-005](docs/architecture/ADR-005-SECOND-BRAIN-ASSISTANT-HUB.md) for the existing accepted second-brain decision. Capability schema changes are a pre-merge v1 correction, not a released-contract compatibility claim or live runtime feature.

- Core main inspected at `c7188318a6e2b17b28dfc5311d365f2d0ed6e0de` (#150), including the October 19 legacy-host retirement decision and Railway Core configuration.
- [README hosting baseline](README.md#current-production-baseline) records the October 19 Railway backend observation. That supersedes this branch's October 9 staged-only status; it is not a fresh production probe.
- On 2026-10-21, continuity PR [#145](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/145) was the consolidation home; check the current default branch and PR disposition before selecting any continuation branch. Main is incorporated without reverting its hosting or security fixes.
- `docs/HANDOFF.md` was absent from main and all six audited PR heads. It is now a short navigation entry, not a second backlog.
- The local configuration validator previously accepted an empty ancestor `.git` directory as a repository root. Eleven of 26 existing tests failed under the cloud `/tmp/.git` marker. The fix requires checkout metadata and adds a deterministic regression.

- Follow-up #153 repair moves the three contracts into the existing `schemas/` root without changing their `$id` values, requires explicit timeline sensitivity and account-scoped bindings for actionable capabilities, and reconciles the one `/mcp` registry UI with the unimplemented `/agents/capabilities` compatibility name. Web source evidence is pinned in ADR-005; no alias/runtime feature is added.

## Evidence limits

- Git read works. GitHub REST and GraphQL requests return `Forbidden`; public PR/checks pages supply the read-only audit. See [handoff](docs/HANDOFF.md) for exact heads and checks.
- October 9 Worker-placeholder/Railway-staging observations are historical; they must not be reported as current blockers without a new provider read.
- Coordinator-supplied authenticated Railway read on 2026-10-21 reported the web app SLEEPING and MySQL OFFLINE. Stable resource IDs and UNKNOWN granted scopes are recorded only in the [canonical integration matrix](docs/command-center/KOVA_OS_INTEGRATION_MATRIX.md#provider-identity-and-granted-permissions). This session did not independently query Railway; the older healthy/sleeping baseline is not current application/database-health proof.
- OAuth/callback/session/logout, database-backed application behavior, CORE provider connectivity and private-data ingestion were not verified in this session.
- Provider account, billing, DNS, secrets, access and production data were not changed. No PR was closed or merged.

## Next action

CI gate follow-up from main `b95c57b`: `verify-platform` now waits for both
`verify-source` and `container-smoke`, preserving the existing required ruleset
context and manual Mergify queue. Failures, cancellation and skipped prerequisites
cannot yield a successful aggregate. Permission fixtures explicitly establish
their intended modes; all 196 Python tests pass under umask `0077`. This source
follow-up awaits current-head hosted Docker/aggregate checks and review. Docker
is unavailable locally; no provider, DNS, secret, billing or deployment change
is included.

Follow the [current-branch selection gate](docs/HANDOFF.md#before-selecting-a-continuation-branch), review the current authorized PR and exact-head CI, then resolve the distinct provider-adapter, Temporal and architecture review work in [KOVA_BACKLOG.md](KOVA_BACKLOG.md). A proposed design, green source check or configured service does not establish live integration readiness.
