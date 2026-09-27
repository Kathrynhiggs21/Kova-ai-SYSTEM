# KOVA OS Remediation Roadmap

Status: Active remediation roadmap for issue #92.

## Goal
Make the current multi-repository KOVA OS understandable, safe to automate, and operational without destructive rewrites.

No destructive repo moves or automation enablement should happen until the Phase 0 ownership map is merged.

## Phase 0 (P0) — Canonical ownership freeze

- Adopt `docs/architecture/KOVA_REPOSITORY_MAP.md` as the human source of truth.
- Keep `Kova-ai-SYSTEM` as current Core/backend authority.
- Keep `kova-ai-dash` as current authenticated Command Center authority.
- Keep `kovaos-site` as the public-site authority and separate from authenticated Command Center responsibilities.
- Keep auto-sync, auto-discovery, webhook mutations, cross-repo PR automation, and unified changelog disabled until ownership is stable.
- Resolve `kova-ai` identity conflict and migrate Zoo/card code to `Scribbles-Zoo-Project`.

Exit criteria: repository map merged; runtime registry and fallback defaults match ownership and keep mutating automation disabled.

## Phase 1 (P1) — Contract and boundary definition

- Define provider-independent memory contract.
- Define connector contract and verified health semantics.
- Define AI gateway interface.
- Define durable automation/job contract.
- Define Android client boundary.
- Standardize CI/security gates across production repositories.

Exit criteria: each contract has clear API/interface shape, ownership, validation semantics, and CI coverage expectations.

## Operational definition

KOVA OS is operational when all of the following are true:

- Core deployment and health checks are reproducible.
- Authenticated Command Center reads verified Core/integration health through stable interfaces.
- Public site and authenticated Command Center responsibilities remain separated.
- At least one AI provider operates through the defined gateway interface.
- Memory and connector layers expose explicit privacy/provenance behavior.
- Automation jobs run with durability semantics (schedule, retry, audit, failure reporting).
- Android/web clients use documented boundaries.
- Secrets remain externalized.
- CI/security gates protect production branches.
- Backup/restore and rollback are documented and testable.
