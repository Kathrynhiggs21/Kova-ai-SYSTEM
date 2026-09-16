# ADR-002: Canonical KOVA Web Application

- Status: Accepted
- Date: 2026-09-15
- Domain: `https://kovaos.com`

## Decision

KOVA OS has two active platform repositories:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` owns architecture, the control plane, connector contracts, automation policy, shared schemas, deployment coordination, and audits.
2. `Kathrynhiggs21/kovaos-site` owns the authenticated browser/PWA experience at `kovaos.com`.

Donor builds (including `kova-ai-dash` and the Lovable KOVA OS prototype) are feature donors only. Their unique dashboard, integration, command, and provenance features must move through reviewed pull requests into `kovaos-site`; donors remain non-canonical and cannot become runtime authorities by implementation convenience.

The proposed names `kova-core-system`, `kovaos-pwa`, `kova-memory-mem0`, and `kova-legacy-archive` are logical target labels, not authorization to create duplicate repositories or combine Git histories destructively. Existing repositories keep their names until redirects, deployment links, package imports, and history preservation are verified.

Scribbles, Reagan learning, and TAC for Hope are independent product/World boundaries. They may integrate with KOVA through contracts, but they are not folders inside the KOVA Core repository.

## Source evidence

- [Approved KOVA final architecture](https://drive.google.com/file/d/19B30gtiOE9F9IzYaKixQNrz3wUu6IROq/view)
- [KOVA target-state registry](https://drive.google.com/file/d/1vDdBFTgVxj1djLsSKI6Id5zGZpduq3mM/view)
- [KOVA remediation roadmap](https://drive.google.com/file/d/17NmHIlWPDeHnFQDg-27GQA4eWmH2_W63/view)
- [KOVA architecture package folder](https://drive.google.com/drive/folders/180rt6J7TuEtsErBvG_rt8ZPnEAICpako)
- [Structured KOVA/AI Drive](https://drive.google.com/drive/folders/1ASnxBdkrBtEhw7s5OlM27JF6dTuQ5WWl)

The general personal Drive folder is not a KOVA source of truth. The mixed KOVA working folder contains useful artifacts but also duplicates and converted copies; it is an intake/reference source, not executable truth.

## Consequences

- Runtime registry enables only Core and `kovaos-site`.
- Feature donors, experiments, and archives cannot be deployed by registry automation.
- Lovable donor migration decisions are tracked in `docs/architecture/KOVA_LOVABLE_DONOR_MIGRATION_MATRIX.md`; only `donor better` and `net-new` items are eligible for migration.
- GitHub owns executable truth; Drive owns user files and archival evidence.
- New KOVA repositories require a distinct deployable boundary and an update to this ADR and the runtime registry.
- Vercel cleanup retains clean project names only long enough to verify domains and environment variables; retaining a Vercel project does not promote its source repository to canonical status.
