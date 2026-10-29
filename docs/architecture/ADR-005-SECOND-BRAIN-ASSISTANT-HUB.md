# ADR-005: KOVA Second Brain and Assistant Hub

- Status: Accepted
- Date: 2026-10-21
- Scope: KOVA Core + canonical authenticated application

## Decision

KOVA is a persistent personal AI operating system and second brain with one assistant-first control surface.

The canonical system keeps the existing repository boundary:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` owns orchestration, memory contracts, capability registry, agent routing, action policy, audits, provenance, and the execution/learning loop.
2. `Kathrynhiggs21/kovaos-site` owns the authenticated user experience, including the Assistant, AI Hub, Connections, Widgets, Automations, AI World links, settings, and owner administration.

Hosting providers, model providers, connectors, and automation services are replaceable adapters. None becomes a source of truth merely because it is currently connected.

## Seven-layer functional model

### 1. Identity

Maintain one private KOVA profile with multiple authorized identities and account labels. Identity-specific data must preserve provenance without creating parallel KOVA profiles.

Personally identifying account details belong only in private runtime storage. Do not commit them to this public repository.

### 2. Durable second brain

KOVA memory has four semantic classes:

- fact: a verified or qualified statement about current or historical state;
- relationship: a directed connection between stable source and target entity identifiers with an explicit relationship type;
- procedure: an approved or learned way the owner prefers recurring work to be done;
- timeline: a dated material event, decision, action, or correction.

Vector search may index memory for retrieval, but vector storage is not authoritative for identity, permissions, canonical file ownership, action history, or audit state.

### 3. Knowledge graph

Relationships connect stable entity identifiers instead of copying entire source objects. Graph edges keep provenance, confidence, time validity, and sensitivity metadata.

### 4. Universal search

Search fans out only to authorized sources. Results normalize to stable IDs, canonical URLs/references, source/provider, modified time, access state, and provenance. Retrieval may rank semantically, but KOVA must distinguish current canonical records from historical or inferred material.

### 5. Capability graph

Every tool/connector declares explicit capabilities, risk class, access mode, current evidence state, evidence time, and canonical destination. Use the six evidence labels in the [canonical README](../../README.md#evidence-based-status): configured, connected, runtime verified, needs connection, broken, and unknown. Operational disablement or degradation does not replace the evidence label. Tool availability is not proof of authentication.

### Capability state contract and compatibility

The [capability registration v1 schema](../../schemas/capability-registration.v1.schema.json) uses uppercase machine spellings of the canonical labels:

| State | Evidence meaning |
|---|---|
| `CONFIGURED` | A setting or adapter exists; runtime has not been proven. Evidence may describe configuration only. |
| `CONNECTED` | Authentication and a current end-to-end read through the intended source succeeded. A provider name, open port, installed tool or staged mutation is insufficient. |
| `RUNTIME_VERIFIED` | A current check passed on the intended production path. A local test, mock, CI build or CONNECTED source read alone is insufficient. |
| `NEEDS_CONNECTION` | Required authorization or configuration is missing; do not invent grants. |
| `BROKEN` | A current check failed with recorded evidence. `last_verified_at` is the check time, not a claim of success. |
| `UNKNOWN` | No current evidence exists. Both current evidence fields must be null; keep any historical audit records in their canonical store. |

CONNECTED and RUNTIME_VERIFIED also require a nonblank `connector_ref` resolving to exactly one account-scoped connection. The registry binding must identify the provider and intended account; a provider brand, default account or display label alone is insufficient. Consumers must resolve the opaque reference, verify that its provider/account matches the intended action and evidence, and apply current authorization before routing. Schema validation checks presence, not the referenced account or its granted permissions.

`last_verified_at` and `evidence_ref` are both null or both populated. CONNECTED, RUNTIME_VERIFIED and BROKEN require a date-time plus a nonblank, nonsecret audit reference. For CONFIGURED or NEEDS_CONNECTION, an optional pair supports only the configuration/absence claim; it does not promote the state. UNKNOWN cannot carry a current-verification pair. Validators must enable RFC 3339 `date-time` format checking; a JSON Schema implementation that ignores formats is insufficient for these contracts.

Schema validity does not authenticate an actor, enumerate granted OAuth/API scopes, resolve an audit reference, prove an outcome, or establish freshness. Before displaying a current state or routing an action, the consuming system must verify the audit record's actual outcome, timestamp/freshness, intended source and exact environment/path. CONNECTED requires an authenticated end-to-end read; RUNTIME_VERIFIED requires the intended production check; BROKEN requires the failed check. Stale, future-dated or unavailable evidence cannot sustain a current verified claim. No freshness duration or runtime implementation is introduced by this ADR correction. Permission-scope evidence remains separate, as required by the [integration matrix](../command-center/KOVA_OS_INTEGRATION_MATRIX.md#provider-identity-and-granted-permissions). A valid registration never authorizes an action by itself.

#### Pre-merge v1 compatibility

These schemas are new in PR #153 and absent from main `83bb724092344b0eed3a5f1b0182049a246847e6`. The inspected Core and canonical web source contained no consumers of these schema IDs or registration records; deployed/external use was not verified. This corrects the **unmerged v1 candidate**, retaining its filename and `$id`; it does not claim a backward-compatible change to an already released contract.

Compared with PR head `289380ea44675c2088a50e86cadcc21a93e5e1c4`, the corrected v1 rejects `DEGRADED` and `DISABLED`, evidence-free CONNECTED/BROKEN claims, partial evidence pairs, whitespace-only evidence references, and current-verification metadata on UNKNOWN. Existing high-risk confirmation and required-field constraints remain. Do not automatically translate operational labels into a live state or manufacture evidence. Re-derive a canonical label from current authorized evidence; preserve any existing disable control in its owning policy rather than adding a new switch to this schema.

Any consumer or saved fixture pinned to an earlier PR candidate must be explicitly revalidated and migrated before adopting this head. If an external/deployed consumer is found, treat that as a compatibility blocker: retain its pinned contract and agree a versioned migration (a new schema ID/version where required) before release. Do not silently tighten a published v1 in place. No runtime migration, task store or new provider feature is implemented here.

#### Canonical schema location and privacy classification

The three contracts live only in the existing shared [schemas directory](../../schemas), beside [agent-ledger-entry.schema.json](../../schemas/agent-ledger-entry.schema.json). The old configuration subdirectory is removed rather than mirrored. File basenames and all three `$id` URIs are preserved, so identity-based consumers keep the same schema identities; relative filesystem consumers must update their paths. Git commit-pinned historical paths remain source history, not a second discovery root or a promise of deployed URL hosting.

The [memory record v1](../../schemas/memory-record.v1.schema.json) retains its prior relationship, sensitivity, dated-TIMELINE and supersession clauses. The [timeline event v1](../../schemas/timeline-event.v1.schema.json) now **requires** explicit `sensitivity` on every event, including corrections. A JSON Schema `default` is only an annotation and does not populate a record; the misleading default annotation is removed. Missing, null or invalid classification is rejected, never silently promoted to PUBLIC or assumed PRIVATE.

These are further incompatible corrections to the same unmerged v1 candidate: old filesystem paths, events missing sensitivity, and CONNECTED/RUNTIME_VERIFIED registrations lacking an account-scoped connector reference require explicit migration/revalidation. No `$id` or contract version changes here; the earlier pre-release compatibility and external-consumer blocker still apply. No runtime alias, data backfill, identity provisioning or provider change is implemented.


### 6. Agent router

Provider selection is policy-driven rather than hard-coded by brand. Routing may consider capability fit, authorization, privacy/sensitivity, quality, context size, reliability, latency, cost, owner preference, and prior validated outcomes.

### 7. Execution + learning loop

All consequential work follows:

`Plan -> Act -> Verify -> Record -> Learn`

- Plan: resolve intent, context, source of truth, policy, and approval requirements.
- Act: use the minimum authorized context and capabilities.
- Verify: read back provider state where possible.
- Record: append material outcome and provenance to run/timeline history.
- Learn: use explicit corrections and repeated confirmed choices to improve future routing and procedures.

Learning never silently overrides a hard policy, source-of-truth rule, explicit owner preference, or permission boundary.

## Action authority

KOVA may perform broad authorized discovery and low-risk read operations without repeated confirmation.

Mutations are classified by risk:

- low: reversible metadata/status changes within approved scope;
- medium: external writes or changes with material user impact;
- high: destructive deletion, money movement, DNS/domain changes, publishing, credential/security changes, or sensitive external communication.

High-risk actions require explicit confirmation in the v1 capability contract. A future contract may represent narrowly bounded delegation only with an explicit validated policy reference. Audit records must never contain secrets.

## Canonical source rules

- executable code/configuration: GitHub canonical repositories;
- user files/documents: canonical user storage, primarily Google Drive where approved;
- AI World material: AI World canonical registry/storage;
- runtime memory, relationship, action, and timeline records: private KOVA operational data store;
- design system: canonical app implementation plus approved design-source references;
- provider dashboards: evidence and management surfaces, never canonical product truth.

## User experience

The primary experience is assistant-first rather than dashboard-first.

Recommended canonical routes:

- `/assistant` primary conversational interface;
- `/hub` second-brain and capability overview;
- `/mcp` single canonical owner connection/capability registry UI (currently a dated source snapshot, not a live owner-protected registry claim);
- `/widgets` mobile/web widget catalog;
- `/automations` scheduled and event-driven workflows;
- `/world` AI World provenance surface;
- domain modules such as calendar, files, vault, finance, and travel;
- `/settings` private preferences and permissions;
- `/admin` owner-only governance.

### Registry ownership and route compatibility

Core owns capability/connection contracts, registry data and authorization; the canonical web app owns the one registry UI at `/mcp`. `/agents` is the agent-routing overview and may link to that registry; it must not own duplicate provider/account records. Core's HTTP `/mcp` JSON-RPC transport is a separate protocol endpoint, not a second web registry.

Source evidence: canonical web main [`28debe0`](https://github.com/Kathrynhiggs21/kovaos-site/commit/28debe0edaaa7fc818a617bf4ec11dc55ad8d97b), inspected in this session, maps [`/mcp` to ConnectionCenter and `/agents` to AgentHub](https://github.com/Kathrynhiggs21/kovaos-site/blob/28debe0edaaa7fc818a617bf4ec11dc55ad8d97b/client/src/App.tsx#L82). [ConnectionCenter](https://github.com/Kathrynhiggs21/kovaos-site/blob/28debe0edaaa7fc818a617bf4ec11dc55ad8d97b/client/src/pages/ConnectionCenter.tsx) explicitly describes a dated evidence snapshot; its current route does not wrap that component in AccessGate. This is source-route evidence, not proof of deployed behavior, live connection checks or owner authorization.

The older `/agents/capabilities` name in shared-agent-history guidance is a **compatibility alias name for `/mcp`**, not a second registry. No such route/redirect exists in the inspected web source; do not advertise that alias as working. Any future authorized compatibility implementation must redirect or reuse the same `/mcp` view and authorization, never fork its records or create a second registry page. This documentation repair adds no route or redirect. The [shared-agent-history surface contract](KOVA_SHARED_AGENT_HISTORY.md#canonical-surfaces) uses this same owner/alias rule. Other recommended routes above are product targets unless current source evidence establishes implementation.

The orb is the persistent assistant identity, not merely decoration. Its visual state may communicate idle, listening, thinking, tool use, waiting, alert, or offline state, subject to accessibility and reduced-motion settings.

## Privacy and provenance

Every durable memory record must have provenance and a confidence state. Sensitive material must be classified and access-controlled separately from searchability.

KOVA must support correction and supersession. Append-only event history does not mean an incorrect claim remains active forever; corrections point to the superseded record and current canonical state.

## Consequences

- New memory/provider implementations must conform to provider-independent contracts.
- New connectors must register explicit capabilities rather than adding hidden provider-specific fallback paths.
- The web application may display memory and capability state but does not become the orchestration authority.
- Manus remains historical/optional and is not a runtime dependency.
- Legacy one-click hosting remains retired from active KOVA runtime architecture.
