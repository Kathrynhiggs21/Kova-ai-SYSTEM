# KOVA OS — Prioritized Development Backlog

Statuses: TODO, IN PROGRESS, BLOCKED, VERIFIED. A TODO is not evidence of a broken live service.

| Priority | Task | Acceptance criteria | Status |
|---|---|---|---|
| P0 | Review security and authentication in canonical hub and web app | Map login/callback/session boundaries, owner gating, legacy Manus dependencies, and concrete migration risks; no secrets in reports | TODO |
| P0 | Establish current deployment/runtime evidence | Record current DNS/route, backend health, auth, cookie and API checks with timestamps and exact environment | TODO |
| P0 | Run existing CI/test gates | Capture commands, exit codes and failures for hub and web repositories | TODO |
| P1 | Audit RedPlanetHQ/CORE for adoption | Verify source, license, maintenance, dependencies, privacy boundaries, and integration seam; no code import before audit | TODO |
| P1 | Temporal memory contract | Specify valid_from/valid_to, observed_at, provenance, confidence, explicit/inferred classification, privacy scopes and deletion behavior; add tests | TODO |
| P1 | Connector and permission inventory | Record verified read/write scopes, source, refresh status, approvals and failure modes; distinguish planned vs connected | TODO |
| P1 | CORE integration spike | Implement isolated, reversible adapter with tests only after audit; preserve canonical KOVA services | BLOCKED: CORE audit |
| P2 | Durable cross-chat handoff workflow | Update build state/backlog/decisions/run log after each coding session; link commits and tests | IN PROGRESS |
| P2 | Adaptive memory and event pipeline | Prototype deduplication, contradiction handling, temporal links and confidence decay with private test fixtures | TODO |

## Operating rules
- Work on a branch and open a PR; no unreviewed main changes.
- Prefer existing services and docs; never create duplicate dashboards or document stores.
- Keep user records private, fail closed, and require approval for sensitive or destructive actions.
- At the end of each work session, update this backlog and `KOVA_BUILD_STATE.md` with verified evidence, not aspirational statuses.
