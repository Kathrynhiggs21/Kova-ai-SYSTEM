# ADR-002: Command Center and Public Site Boundaries

- Status: Accepted
- Date: 2026-09-16
- Domain: `https://kovaos.com`

## Decision

KOVA OS currently operates with three active repositories and explicit frontend separation:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` owns Core/backend orchestration, APIs, MCP, shared contracts, connector and automation interfaces, and policy.
2. `Kathrynhiggs21/kova-ai-dash` owns the authenticated Command Center experience.
3. `Kathrynhiggs21/kovaos-site` owns public, unauthenticated web responsibilities for `kovaos.com`.

`kova-ai-dash` is not treated as a donor during this remediation phase; it is the current authenticated authority. `kovaos-site` must not absorb authenticated Command Center scope until ownership is explicitly re-decided.

## Rationale

The immediate risk in this phase is ownership ambiguity, not missing UI code. Separating authenticated operations from public presentation prevents accidental privilege expansion, confusing automation behavior, and incorrect deployment assumptions while repository boundaries are being stabilized.

## Consequences

- Runtime registry keeps all mutating cross-repository automation disabled.
- Authenticated and public frontend responsibilities are reviewed independently.
- Any future consolidation or migration requires an explicit ownership decision, versioned API boundaries, and tested rollout/rollback.
