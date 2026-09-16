# KOVA OS Repository Map

Status: Canonical remediation ownership map v1 · 2026-09-16

This document is the human source of truth for repository ownership during remediation. Runtime enablement remains machine-controlled by `kova_repos_config.json` (`repositories[].enabled`).

Do not enable destructive automation, destructive repo moves, or cross-repository mutation workflows until this ownership map is merged and stable.

## Active repositories

| Repository | Responsibility | Status |
|---|---|---|
| `Kathrynhiggs21/Kova-ai-SYSTEM` | Core/backend authority: orchestration, API, MCP, connector contracts, automation contracts, policy, shared schemas, observability | ACTIVE |
| `Kathrynhiggs21/kova-ai-dash` | Authenticated Command Center authority: operator dashboard, authenticated controls, integration command surfaces | ACTIVE |
| `Kathrynhiggs21/kovaos-site` | Public site authority: unauthenticated web presence, marketing/docs pages, public content for `kovaos.com` | ACTIVE |

## Disabled automation until ownership is stable

The following remain disabled in the runtime registry:

- auto-sync;
- auto-discovery;
- webhook-driven mutation flows;
- cross-repository PR automation; and
- unified changelog automation.

## Identity and migration boundaries

- `kova-ai` is a mixed legacy repository under identity remediation and remains disabled until ownership/content are fully inventoried.
- Zoo/card code migrates to the dedicated `Kathrynhiggs21/Scribbles-Zoo-Project` World boundary and does not become KOVA Core automation.
- Scribbles and Zoo repositories can integrate with KOVA contracts but are not part of Core runtime ownership.

## World repositories (catalog only)

| Repository | Relationship to KOVA | Lifecycle |
|---|---|---|
| `Kathrynhiggs21/scribbles-by-marcy` | Independent Scribbles World; optional KOVA consumer | REVIEW |
| `Kathrynhiggs21/Scribblesbymarcy` | Same-name migration candidate; audit before consolidation/archive | UNREVIEWED |
| `Kathrynhiggs21/Scribbles-Zoo-Project` | Dedicated Zoo/card World boundary and migration target | REVIEW |

## Rules

1. Keep one canonical owner per production responsibility.
2. Keep authenticated Command Center scope separate from public-site scope.
3. Keep mutation automation disabled until ownership and tests are proven.
4. Prefer module boundaries in Core before creating new repositories.
5. Keep secrets out of repositories and logs.
