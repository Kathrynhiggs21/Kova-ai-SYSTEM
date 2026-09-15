# ADR-003: Modular Core Boundaries

- Status: Accepted
- Date: 2026-09-15

## Decision

KOVA uses two active repositories:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` for Core, backend, orchestration, MCP, shared contracts, connectors, automation, data, security, files, and observability.
2. `Kathrynhiggs21/kovaos-site` for the authenticated application served through `kovaos.com`.

Inside Core, major capabilities are explicit modules. They do not become separate repositories merely because they have different names or menu sections.

## Why

Separate repositories add coordination costs: duplicated CI and settings, more releases, more dependency updates, more permissions, cross-repository version drift, and a harder source-of-truth problem. KOVA does not yet have independent teams or production services that justify those costs.

A modular Core keeps boundaries visible while allowing one tested release. It also preserves an easy future split because module ownership and current paths are recorded in `config/core_modules.v1.json`.

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
- authenticated web application

Imports should flow through documented interfaces. New work should be placed in its owning module rather than adding another top-level repository or duplicating code in the application repo.

## Split threshold

A Core module may graduate to a repository only when at least one material boundary exists:

- it deploys independently;
- it needs distinct secrets, permissions, or a security boundary;
- it scales differently enough to require independent infrastructure;
- it has an independent release cycle or compatibility contract; or
- a distinct team or product owns it.

The split still requires owner approval, a migration plan, CI, deployment ownership, API/version contracts, and an update to the canonical repository registry.

Category names, speculative future use, temporary experiments, or visual neatness do not qualify.

## Current assessment

AI Assistant, MCP, connectors, automation, memory/data, files/artifacts, security, and observability remain Core modules. `kovaos-site` remains separate because it has a distinct application build and deployment lifecycle. No additional repository is justified today.

## Consequences

- KOVA keeps one Core release and one app release.
- Module boundaries are machine-readable and reviewable.
- New repositories are deliberate architecture decisions, not organizational decoration.
- Future service extraction remains possible without committing to premature multi-repo complexity.
