# ADR-004: KOVA Second Brain and Assistant Hub

- Status: Proposed
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
- relationship: a directed connection between entities;
- procedure: an approved or learned way the owner prefers recurring work to be done;
- timeline: a dated material event, decision, action, or correction.

Vector search may index memory for retrieval, but vector storage is not authoritative for identity, permissions, canonical file ownership, action history, or audit state.

### 3. Knowledge graph

Relationships connect stable entity identifiers instead of copying entire source objects. Graph edges keep provenance, confidence, time validity, and sensitivity metadata.

### 4. Universal search

Search fans out only to authorized sources. Results normalize to stable IDs, canonical URLs/references, source/provider, modified time, access state, and provenance. Retrieval may rank semantically, but KOVA must distinguish current canonical records from historical or inferred material.

### 5. Capability graph

Every tool/connector declares explicit capabilities, risk class, access mode, current lifecycle state, evidence time, and canonical destination. Tool availability is not proof of authentication.

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

High-risk actions require explicit confirmation unless a narrowly bounded rule exists and the action type is eligible for delegation. Audit records must never contain secrets.

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
- `/mcp` owner connection/capability registry;
- `/widgets` mobile/web widget catalog;
- `/automations` scheduled and event-driven workflows;
- `/world` AI World provenance surface;
- domain modules such as calendar, files, vault, finance, and travel;
- `/settings` private preferences and permissions;
- `/admin` owner-only governance.

The orb is the persistent assistant identity, not merely decoration. Its visual state may communicate idle, listening, thinking, tool use, waiting, alert, or offline state, subject to accessibility and reduced-motion settings.

## Privacy and provenance

Every durable memory record must have provenance and a confidence state. Sensitive material must be classified and access-controlled separately from searchability.

KOVA must support correction and supersession. Append-only event history does not mean an incorrect claim remains active forever; corrections point to the superseded record and current canonical state.

## Consequences

- New memory/provider implementations must conform to provider-independent contracts.
- New connectors must register explicit capabilities rather than adding hidden provider-specific fallback paths.
- The web application may display memory and capability state but does not become the orchestration authority.
- Manus remains historical/optional and is not a runtime dependency.
- Vercel remains retired from active KOVA runtime architecture.
