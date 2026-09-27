# ADR-003: Modular Core Boundaries

- Status: Accepted
- Date: 2026-09-16

## Decision

KOVA uses three active repositories with one Core and two explicitly separated frontend responsibilities:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` for Core/backend orchestration, MCP, shared contracts, connectors, automation interfaces, memory/data, security, files/artifacts, and observability.
2. `Kathrynhiggs21/kova-ai-dash` for the authenticated Command Center application.
3. `Kathrynhiggs21/kovaos-site` for public `kovaos.com` pages and public content.

The active set is derived from `kova_repos_config.json` entries where `enabled` is true.

Inside Core, major capabilities remain explicit modules and do not become separate repositories without a real operational boundary.

## Why

Module-first Core boundaries reduce coordination and release overhead while preserving clear future split points. Frontend separation is intentionally explicit so authenticated operations are not mixed with public website responsibilities during remediation.

## Module boundaries

- orchestration and shared contracts
- AI Assistant and provider routing
- MCP transport and tools
- connectors and webhooks
- automation and jobs
- memory and operational data
- files, artifacts, and exports
- security and identity
- health and observability
- authenticated command center application
- public website application

## Split threshold

A Core module may graduate to a repository only when at least one material boundary exists:

- it deploys independently;
- it needs distinct secrets, permissions, or a security boundary;
- it scales differently enough to require independent infrastructure;
- it has an independent release cycle or compatibility contract; or
- a distinct team or product owns it.

The split still requires owner approval, a migration plan, CI, deployment ownership, API/version contracts, and an update to the canonical repository registry.

## Current assessment

AI Assistant, MCP, connectors, automation, memory/data, files/artifacts, security, and observability remain Core modules. `kova-ai-dash` and `kovaos-site` remain separate application repositories because they currently serve different trust boundaries.

## Consequences

- KOVA keeps one Core release plus separated authenticated/public frontend releases.
- Module boundaries are machine-readable and reviewable in `config/core_modules.v1.json`.
- New repositories remain deliberate architecture decisions rather than taxonomy-only splits.
