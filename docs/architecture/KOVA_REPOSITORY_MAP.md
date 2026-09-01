# KOVA OS Repository Map

Status: Proposed canonical map for remediation v1

## Active production roles

| Repository | Role | Status | Action |
|---|---|---|---|
| `Kathrynhiggs21/Kova-ai-SYSTEM` | KOVA Core / backend / orchestration | ACTIVE | Keep as current core; target future rename to `kova-core` |
| `Kathrynhiggs21/kova-ai-dash` | Authenticated Command Center | ACTIVE | Keep; target future rename to `kova-command-center` |
| `Kathrynhiggs21/kovaos-site` | Public KOVA website / docs portal | TRANSITION | Remove duplicated app/backend responsibilities over time |
| `Kathrynhiggs21/scribbles-by-marcy` | Scribbles by Marcy business/product repository | ACTIVE WORLD | Keep independent from KOVA Core |
| `Kathrynhiggs21/Scribbles-Zoo-Project` | Zoo / educational-card world | TARGET WORLD | Define product/data/design scope independently of the legacy renderer |

## Repositories requiring remediation

| Repository | Finding | Required disposition |
|---|---|---|
| `Kathrynhiggs21/kova-ai` | Identity conflict: README describes KOVA assistant while current workflows/code include legacy Zoo/card rendering | Inventory generic KOVA code separately; explicitly exclude renderer scripts/workflows from KOVA OS; archive or repurpose only after review |
| `Kathrynhiggs21/kova-ai-mem0` | Memory-service concept exists but repo is minimally defined | Rebuild as provider-independent KOVA Memory service, with Mem0 as an adapter |
| `Kathrynhiggs21/Kova-os-docengine` | Stub repository | Rebuild as docs engine only if needed; otherwise archive |
| `Kathrynhiggs21/Kova-AI-Scribbles` | Duplicate/underspecified Scribbles identity | Archive or repurpose as a narrowly scoped Scribbles connector |

## Explicit exclusion: legacy renderer

The existing Zoo/card renderer implementation and renderer-specific workflows are not part of KOVA OS. They must not be migrated into KOVA Core, Command Center, connectors, memory, automation, AI gateway, infrastructure, or the canonical Zoo/educational-card World. Any future presentation/export implementation should be selected independently.

## Historical / experimental repositories

Starter, generated, `sb1-*`, `TheCenter*`, generic Next/Vite templates, and similar repositories are not production KOVA components unless explicitly promoted through this map and the runtime registry.

## Missing logical services

The following boundaries are required for a complete KOVA OS. They may begin as folders/packages and later become repositories when independent deployment or ownership justifies it.

1. `kova-mobile-android` — native Android assistant, notifications, voice, share/capture and permission-aware device integrations.
2. `kova-connectors` — connector contracts and provider adapters for Google, GitHub, Canva, Notion, Dropbox and future services.
3. `kova-memory` — ingestion, normalization, provenance, retrieval, retention, privacy labels and knowledge graph interfaces.
4. `kova-automation` — jobs, schedules, triggers, workflow definitions and delivery rules.
5. `kova-ai-gateway` — OpenAI/Gemini/Claude provider abstraction, routing, fallback, cost and reliability telemetry.
6. `kova-infra` — deployment manifests, infrastructure as code, environment definitions, observability bootstrap and disaster recovery.
7. `kova-docs` — canonical architecture decisions, runbooks and system specifications.
8. `kova-design-system` — reusable KOVA UI tokens, visual states, icons and shared components.
9. `kova-sdk` — typed clients/contracts used across apps and Worlds.
10. `kova-labs` — explicitly non-production experiments.

## KOVA Worlds

KOVA Core must remain domain-neutral. Specialized products consume Core capabilities through APIs/connectors.

- Personal / Family
- Scribbles by Marcy
- Zoo / Educational Cards
- Education
- Creative
- Travel
- Future verticals

A World owns its own domain data and product code. It may use KOVA memory, automation, research, AI gateway, connectors and notifications without placing domain-specific rendering/business logic in Core.

## Rules

1. One canonical owner for each production responsibility.
2. Runtime registry must match this map.
3. Disabled or experimental integrations must not be shown as live/healthy.
4. No secrets in repositories; examples only.
5. Cross-repository synchronization remains disabled until ownership and tests are stable.
6. All production changes flow through PRs with CI checks.
7. Every new service must define owner, API contract, data classification, health endpoint, deployment target and rollback procedure.
8. The legacy renderer is explicitly outside KOVA OS.