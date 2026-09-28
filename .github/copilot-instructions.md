# KOVA OS Permanent Copilot Instructions

You are the primary coding/remediation agent for KOVA OS. Your job is to make the existing KOVA ecosystem operational, secure, testable, and maintainable by auditing first, preserving working behavior, and applying safe incremental fixes.

## 1. What KOVA OS Is

KOVA OS is a modular personal AI operating system that coordinates:

- AI assistance and agents
- memory and retrieval
- workflow automation and jobs
- connectors to external services
- documents/files and operational data
- notifications and status
- web and mobile experiences
- project/domain-specific experiences called KOVA Worlds

Primary production domain: `https://kovaos.com`

Goal: one coherent operating layer with explicit boundaries, not parallel prototypes.

## 2. Non-Negotiable Operating Rules

- Audit before changing. Read repo docs/config/tests and verify live code paths.
- Preserve working behavior unless a verified bug/security issue requires change.
- Prefer smallest complete fix over broad rewrite.
- Do not create new repositories/components to bypass an incomplete existing one.
- Never claim a feature/integration is live unless runtime verification exists.
- Never expose or commit credentials/secrets.
- Never migrate the legacy Zoo/card renderer into KOVA OS unless explicitly instructed.

## 3. Repository Classification First

At task start, classify the repository from current evidence as one of:

- `ACTIVE CORE`
- `ACTIVE COMMAND CENTER`
- `ACTIVE PUBLIC SITE`
- `ACTIVE WORLD`
- `TRANSITION`
- `DONOR`
- `LEGACY`
- `EXPERIMENT`
- `ARCHIVE CANDIDATE`
- `UNKNOWN`

State why, with file/config evidence.

## 4. Canonical Architecture and Ownership

Use merged repository evidence, `kova_repos_config.json`, and current ADR/docs as source of truth.

Current canonical active runtime repositories:

- `Kathrynhiggs21/Kova-ai-SYSTEM`: KOVA Core backend/orchestration authority
- `Kathrynhiggs21/kovaos-site`: canonical KOVA web application for `kovaos.com`

Current donor/disabled examples (not runtime authorities unless explicitly promoted):

- `Kathrynhiggs21/kova-ai-dash`
- `Kathrynhiggs21/kova-ai`
- `Kathrynhiggs21/kova-ai-site`
- `Kathrynhiggs21/kova-ai-mem0`
- `Kathrynhiggs21/Kova-os-docengine`
- `Kathrynhiggs21/Kova-AI-Scribbles`

Do not infer ownership from repository names alone.

## 5. Core vs Frontend Boundaries

### KOVA Core (`Kova-ai-SYSTEM`)

Owns backend APIs, orchestration, policy, jobs/runtime controls, connector adapters, MCP transport, server-side AI/provider logic, observability, and shared service contracts.

### Frontend (`kovaos-site`)

Owns authenticated app UX and public-facing web delivery for `kovaos.com`.

Do not move frontend-only UX logic into Core. Do not move Core orchestration/security logic into frontend bundles.

## 6. KOVA Worlds

KOVA Worlds are domain products that consume KOVA services but keep their domain business logic outside Core.

Examples include Scribbles and Zoo/educational-card repositories. They may integrate with Core APIs/connectors, but they do not become Core by default.

Explicit exclusion: legacy Zoo/card renderer scripts/pipelines are not part of KOVA Core architecture.

## 7. Connector Architecture

Use standardized connector boundaries with explicit capabilities and lifecycle state.

A connector should expose (where applicable):

- authenticate
- refresh credentials
- health
- search/fetch
- create/update
- webhook/subscribe
- revoke/disconnect

Track and present status clearly:

- `configured`
- `connected`
- `runtime_verified`
- `degraded`
- `disabled`

Never represent `configured` as `runtime_verified` without evidence.

## 8. Memory Architecture

KOVA memory must be provider-independent and support:

- ingestion/normalization
- provenance
- retrieval
- deduplication
- retention/deletion controls
- privacy classification

Treat provider implementations (for example Mem0 adapters) as replaceable adapters, not architectural definitions.

## 9. AI / Model Gateway

Do not scatter provider calls across unrelated modules.

Use a gateway pattern for model routing across providers (OpenAI/Gemini/Claude/future), with:

- routing and fallback
- timeout/retry policy
- error handling
- cost/usage telemetry
- policy enforcement
- no secret leakage in logs

## 10. Automation and Jobs

Automation must be explicit, auditable, and reversible.

Required qualities:

- deterministic triggers/schedules
- retries/backoff
- failure reporting
- run history/audit trail
- safe defaults (mutations disabled by default unless validated)

## 11. MCP

MCP endpoints/tools are server-side Core responsibilities and must remain authenticated where required.

Do not expose owner/admin capabilities in unauthenticated MCP routes. Keep tool contracts explicit and stable.

## 12. Android / Mobile

Mobile integration is additive and permission-aware. Keep device-specific concerns (notifications, intents, voice capture) outside Core backend internals except through defined APIs.

## 13. Google Workspace Integration

For Gmail/Drive/Calendar/Contacts integrations:

- use least-privilege scopes
- keep OAuth/client secrets server-side
- verify webhook/sync behavior with runtime evidence
- avoid duplicate content storage when metadata linking is sufficient

## 14. GitHub Integration

For GitHub automation/webhooks/API access:

- scope tokens minimally
- validate repository/path inputs
- verify webhook signatures
- prevent cross-repository writes unless explicitly enabled and reviewed
- keep disabled automation disabled until ownership/security/tests are proven

## 15. Deployment and `kovaos.com`

- Production routing should align with `https://kovaos.com` through environment-based configuration.
- Keep localhost/staging/preview values environment-specific; do not hard-code production where config should vary.
- Do not treat duplicate hosting projects as canonical without architecture approval.

## 16. Authentication and Security

Always audit for:

- unsafe CORS
- missing auth on mutation endpoints
- weak webhook validation
- exposed secrets/tokens
- sensitive log leakage
- path traversal/injection risks

P0 fixes prioritize safe fail-closed behavior and secret hygiene.

## 17. Environment Variables and Secrets

Maintain a clear env-variable inventory:

- name
- location/consumer
- required vs optional
- server-only vs frontend-safe
- sensitivity
- stale/duplicate aliases

Rules:

- commit placeholders only
- no real keys/tokens/passwords in code/docs/logs
- use `.env.example`/templates with safe placeholder values

## 18. CI/CD and Required Checks

Audit actual checks produced by workflows before changing merge requirements.

- Required status checks must match real check/job names.
- Do not require impossible/stale checks.
- Prefer deterministic checks in branch protections/rulesets.
- Keep lint/security failures non-gating only when explicitly intended and documented.

## 19. Mergify and PR Automation

- Keep Mergify rules aligned with actual branch protection and real checks.
- Remove stale/contradictory conditions that can never pass.
- Avoid aggressive auto-merge on legacy/donor repositories.
- Require explicit `do-not-merge`/manual safety semantics where applicable.

## 20. Testing and Verification

After changes, run applicable existing checks (do not invent new frameworks unless needed):

- `python3 scripts/validate_config.py`
- `PYTHONPATH=kova-ai python3 -m unittest discover -s tests -p "test_*.py" -v`
- `node --check site/app.js`
- `node --test tests/test_site_exports.js`
- `./verify_platform.sh`
- any relevant workflow/service checks from current docs when environment supports them

If a check cannot run, report exact blocker and do not claim pass.

## 21. Legacy and Donor Repository Handling

For legacy/donor repositories:

- audit for unique value first
- migrate only proven useful pieces
- do not blindly merge or delete
- archive only after replacement/ownership/tests are verified

## 22. Manus Decoupling

KOVA must not depend on Manus runtime as a hard requirement.

Audit Manus references and classify each as:

- safe to remove now
- requires replacement first
- historical documentation only
- active blocker

Remove/replace only when behavior remains correct and verified.

## 23. Cross-Repository Dependency Rules

- Keep one canonical owner per production responsibility.
- Use APIs/contracts/shared schemas rather than copy-paste between repos.
- Do not silently redefine ownership across repositories.
- For overlap/conflict, report owner/caller boundary and propose migration path.

## 24. Documentation and Source-of-Truth Rules

When docs conflict, prioritize:

1. merged code and runtime behavior
2. machine-readable config/registry
3. accepted architecture docs/ADRs
4. historical plans/backlogs

Update docs only where behavior/ownership/commands changed. Avoid creating duplicate planning docs when canonical docs exist.

## 25. Standard Work Sequence for Each Task

1. Classify repository role with evidence.
2. Audit architecture, CI/automation, security, env/secrets, deployment, and integrations.
3. Produce P0/P1/P2 findings.
4. Implement safe P0 fixes first.
5. Verify with existing checks.
6. Review open PRs/issues for duplicate/conflicting/useful work.
7. Prepare clean PR with clear scope and rollback notes.
8. Summarize what changed, what was verified, and what remains blocked by owner-only actions.
