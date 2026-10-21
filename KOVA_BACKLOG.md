# KOVA Backlog

Reviewed: 2026-10-21. One task list; TODO is not evidence of a broken live service. Read [build state](KOVA_BUILD_STATE.md) and [handoff](docs/HANDOFF.md) first.

| Priority | Work | Acceptance / current status |
|---|---|---|
| P0 | Consolidate continuity in Core #145 | Completed via merged #145 at main `83bb724` (2026-10-21); preserve its continuity, scope-evidence and branch-selection corrections. No other PR closure is implied. |
| P0 | Keep Core validation portable in cloud tasks | Reject empty ancestor `.git` markers as checkout roots; exercise existing config tests plus a deterministic regression without moving fixtures out of `/tmp`. Scope `umask 022` to tests whose permission fixtures require CI defaults. |
| P0 | Establish current authenticated runtime evidence | Independently verify Cloudflare-to-Railway health JSON, intended-account login/callback, secure cookies, anonymous denial, protected routes, logout and persistence with timestamps and exact source revision. Provider settings and dated observations do not prove acceptance. |
| P0 | Review authentication and retired dependencies | Map Core/web owner gates and remaining legacy Manus coupling. Do not point a Manus-specific OAuth variable at a different provider without an approved adapter design. No secret values in reports. |
| P1 | Review isolated CORE adapter (#147) | Preserve its versioned source and runtime-audit evidence. Incorporate current main; retain security/license review and prove synthetic authenticated provider operations before activation or private ingestion. |
| P1 | Review Temporal pilot (#148) | Keep separate from continuity. Its current root CI does not install/type-check/test the new integration; add repeatable dependency resolution and approval/retry/cancellation/restart evidence before adoption. Compare existing CORE BullMQ/Redis capabilities first. |
| P1 | Review second-brain contracts (#153) | Existing #153 branch incorporates main `83bb724`; second-brain decision renamed ADR-005, capability states aligned with README and pre-merge v1 compatibility documented. Contracts now use the canonical `schemas/` root; timeline classification, connector-account binding and one-registry route semantics are repaired. Schema regressions cover the earlier HIGH/TIMELINE guards. Await exact-head hosted checks/review; deployed-consumer compatibility and live runtime implementation remain unverified. |
| P1 | Connector and permission inventory | Record owner, read/write scopes, source, refresh/evidence dates, approvals and failure modes. Distinguish configured, connected and runtime verified. |
| P2 | Adaptive memory/event pipeline | Plan deduplication, contradictions, valid_from/valid_to, observed_at, explicit/inferred classification, confidence decay and private fixtures after the #153 contract review. |
| P2 | Maintain continuity | Update build state, this backlog, decision index and run log after substantial work. Preserve source links, commits and actual test results. |

## Hosting boundary

Use Cloudflare + Railway. Vercel retirement is already recorded on current main; its legacy check errors do not authorize restoring it. Any remaining provider-side cleanup is a separate owner/provider task, outside this pass. Preserve unique historical source evidence, not obsolete deployment instructions.
