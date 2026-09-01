# KOVA OS Remediation Roadmap

## Goal
Create a safe, understandable, operational KOVA OS from the existing repositories without deleting working code or enabling unsafe automation prematurely.

## Phase 0 — Freeze ambiguity
- Keep `Kova-ai-SYSTEM` as current Core authority.
- Keep `kova-ai-dash` as current Command Center authority.
- Keep cross-repo auto-sync, auto-discovery, webhook mutations and cross-repo PR automation disabled.
- Treat `kova-ai` as a mixed legacy repository until content is inventoried; legacy renderer code is explicitly outside KOVA OS.
- Treat starter/template repos as non-production unless explicitly promoted.

Exit criteria: repository map accepted and runtime registry matches active production roles.

## Phase 1 — Repository identity repair
- Update READMEs/descriptions to state exact role, lifecycle and replacement/migration target.
- Standardize default branch naming where practical.
- Add `ARCHITECTURE.md`, `SECURITY.md`, `CONTRIBUTING.md` and ownership notes to production repos.
- Add lifecycle markers: ACTIVE, TRANSITION, WORLD, EXPERIMENT, ARCHIVED.
- Inventory `kova-ai` for genuinely generic KOVA code while excluding renderer scripts/workflows from the KOVA architecture.

Exit criteria: a developer or agent can identify the correct repo for any KOVA change without guessing.

## Phase 2 — World boundaries
- Define Scribbles by Marcy and Zoo/Educational Cards as KOVA Worlds with independent domain data and product logic.
- Do not migrate the legacy renderer into either KOVA Core or the canonical Zoo/Educational Card World.
- Keep KOVA Core limited to generic research, AI, storage, memory, connector, notification and automation capabilities.
- Select any future presentation/export implementation independently.

Exit criteria: no renderer-specific workflow is required anywhere in KOVA OS.

## Phase 3 — Frontend separation
- Treat `kova-ai-dash` as authenticated Command Center.
- Treat `kovaos-site` as public site/docs/entry portal.
- Remove duplicate full-stack responsibilities from the public site.
- Define API boundary from Command Center to KOVA Core.

Exit criteria: public web and private command center deploy independently and have distinct responsibilities.

## Phase 4 — Platform services
Establish clear service boundaries for:
- Memory
- Connectors
- Automation
- AI gateway
- Android/mobile
- Infrastructure/observability
- Shared SDK/contracts

These can begin inside `Kova-ai-SYSTEM` as packages while interfaces stabilize. Split into standalone repos only when deployment, security or ownership needs justify it.

Exit criteria: each service has a documented interface, tests, health status and data classification.

## Phase 5 — Security and CI hardening
Required checks for production repos:
1. secret scanning
2. dependency/security scanning
3. lint
4. type checking
5. unit tests
6. integration tests
7. build
8. preview/staging deploy where applicable
9. smoke tests
10. protected production promotion

Never embed owner/API keys in browser code. Prefer OAuth and managed secrets. Redact logs.

Exit criteria: main branches cannot accept broken or secret-bearing changes through the normal workflow.

## Phase 6 — Connector operationalization
Every connector must declare:
- provider
- capabilities
- auth/scopes
- read/write level
- data classification
- sync strategy
- rate limits
- webhook support
- health check
- last successful sync
- revocation procedure

Exit criteria: Command Center health badges reflect verified state rather than configured state.

## Phase 7 — Controlled automation
Only after prior phases:
- enable signed GitHub webhooks
- enable repository discovery for approved naming/owners
- enable unified changelog
- enable cross-repo notifications
- enable narrowly scoped cross-repo PR automation

Mutating automation must use least privilege and produce an audit trail.

## Phase 8 — KOVA Worlds
Formalize domain worlds that consume KOVA services without contaminating Core:
- Scribbles by Marcy
- Zoo / Educational Cards
- Personal / Family
- Education
- Creative
- Travel

Each World owns its data model and business logic.

## Definition of operational
KOVA OS is operational when:
- Core has a reproducible deployment and health check.
- Command Center can authenticate and read verified Core/integration health.
- At least one AI provider works through a controlled gateway.
- Memory and connector layers have explicit privacy/provenance behavior.
- A scheduled automation can run, log, retry and report failure safely.
- Android/web clients can use documented APIs.
- Secrets are externalized.
- CI protects production branches.
- Backup/restore and rollback are documented and tested.
