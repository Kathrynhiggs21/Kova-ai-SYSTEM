# KOVA OS Service Blueprints

These blueprints define missing logical boundaries before new repositories are created. Start as packages when practical; split only when independent deployment/security/ownership requires it.

## kova-mobile-android
Purpose: Native Android client for KOVA.

Minimum scope:
- authenticated KOVA Core client
- push/local notifications
- voice input/output hooks
- Android share intent and capture flows
- permission-aware device integrations
- background work only through Android-supported schedulers
- offline queue/cache with explicit retention

Must not contain long-lived provider API secrets.

## kova-connectors
Purpose: Standard integration contract and provider adapters.

Contract:
- authenticate / refresh / revoke
- capabilities
- health
- search/fetch
- create/update where explicitly permitted
- subscribe/webhook where supported
- rate-limit metadata
- data classification and scope declaration

First providers: Google Workspace, GitHub. Add Canva/Notion/Dropbox only after contracts stabilize.

## kova-memory
Purpose: Provider-independent KOVA memory and retrieval layer.

Minimum scope:
- ingestion adapters
- normalization
- deduplication
- provenance/source links
- privacy/data-classification labels
- retention/deletion controls
- semantic and lexical retrieval
- entity linking/knowledge graph interface
- audit trail for mutations

Mem0 may be one adapter; it must not define the public KOVA memory contract.

## kova-automation
Purpose: Durable jobs, schedules, triggers and delivery rules.

Minimum scope:
- job definitions
- idempotency keys
- retries/backoff
- dead-letter/failure reporting
- scheduler interface
- event-trigger interface
- execution history
- permission checks before mutations

## kova-ai-gateway
Purpose: One stable KOVA interface to model providers.

Minimum scope:
- provider adapters: OpenAI, Gemini, Anthropic
- model capability registry
- routing/fallback policies
- timeout/retry policy
- usage/cost telemetry
- structured-output validation
- content/data routing constraints
- no provider keys sent to browser/mobile clients

## kova-infra
Purpose: Reproducible deployments and operations.

Minimum scope:
- Docker/container definitions
- deployment manifests/IaC
- environment definitions
- secret references, never secret values
- backup/restore procedures
- observability bootstrap
- rollback procedures
- domain/TLS notes

## kova-docs
Purpose: Canonical product/system documentation.

Minimum scope:
- architecture
- ADRs
- API contracts
- connector catalog
- runbooks
- incident procedures
- privacy/security model
- release/change log strategy

## kova-design-system
Purpose: Shared visual language.

Minimum scope:
- design tokens
- typography/spacing
- icons
- KOVA orb/assistant states
- accessibility rules
- reusable web/mobile component specs

## kova-sdk
Purpose: Typed contracts/clients for KOVA Core.

Minimum scope:
- generated or source-of-truth API types
- authentication helpers
- connector status types
- job/event schemas
- error model
- version compatibility rules

## kova-labs
Purpose: Safe home for experiments.

Rules:
- no production credentials
- no production deployment assumptions
- experiments clearly tagged with owner/date/status
- promotion requires explicit migration into an owned production component
