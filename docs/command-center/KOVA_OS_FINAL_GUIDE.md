# KOVA OS Current Guide

## What KOVA is

KOVA is one personal AI operating system with one control plane and one primary application. It should reduce manual work, not create a maze of dashboards, folders, and repositories.

## Canonical platform

- **Core:** `Kathrynhiggs21/Kova-ai-SYSTEM`
- **Authenticated app:** `Kathrynhiggs21/kovaos-site`
- **Primary domain:** `kovaos.com`
- **Hosting target:** Cloudflare for the public edge/static web; Railway for the persistent web Node backend after connection and preview verification. The Python/FastAPI Core remains a separate service until its target runtime and environment are proven.
- **Files:** Google Drive is the canonical user-file store.
- **Operational state:** a relational database will hold runs, jobs, connector health, and application state.
- **Notion:** a human-readable view, not a competing technical source of truth.

`kova-ai-dash` is a disabled feature donor. Other KOVA-named repositories remain disabled unless a verified module split is approved.

## Core modules

The Core repository keeps clear internal boundaries for:

- orchestration and shared contracts;
- AI Assistant and model routing;
- MCP interface;
- connectors and webhooks;
- automation and jobs;
- memory and operational data;
- files, artifacts, and exports;
- security and identity; and
- health and observability.

These are modules, not separate repositories by default. Split one only when it needs its own deployment, secrets/security boundary, scaling profile, or independent release cycle.

## Current reality

Implemented foundations include the FastAPI backend, authenticated owner routes, MCP status tools, repository registry, export controls, web application, authentication work, and automation/file-policy specifications.

Not yet proven production-complete:

- a live versioned Core-to-app `/api/v1` contract;
- durable run history, queueing, retries, and connector telemetry;
- one authenticated end-to-end AI-provider path;
- one authenticated end-to-end connector write/readback path;
- reproducible protected deployment of the web application and a separately verified FastAPI Core runtime; and
- completed migration of useful donor features into `kovaos-site`.

## File organization

KOVA organizes with metadata, not folder sprawl.

Use:

- **Area:** KOVA, Personal, Reagan, or Other
- **Topic:** one useful subject; subtopic only when it helps
- **Lifecycle:** ACTIVE, FINAL, REVIEW, or ARCHIVE
- **Flags:** SENSITIVE and verified DUPLICATE

File Type and Content Origin remain separate descriptive fields. Legacy `UNREVIEWED` maps to `REVIEW`.

KOVA-related chats are included as inputs and linked to their source. Each chat is classified as a decision, requirement, idea, evidence, historical reference, mixed record, or unknown. Only confirmed decisions update the canonical specification; inaccessible share links remain `REVIEW` until their content is available.

Routine automation does not move, rename, overwrite, or delete originals. Matching names are non-destructive review candidates, not proof of duplication. A private registry stores exact-version identity, canonical relationships, lifecycle and duplicate flags, verification evidence, and history.

AI agent folders and general AI-platform content stay in AI World. KOVA links to them when useful instead of copying them into KOVA.

## Connector rule

Prefer native connectors, then MCP, then official OAuth APIs, then automation bridges such as Zapier, Make, or n8n. A configured connector is not “active” until a live read or write/readback proves it.

The attached Zapier MCP starter pack is historical and sensitive. It contains a private configuration URL and describes twelve manual actions that are unnecessary when direct connectors are available. Keep it unchanged as `ARCHIVE` and `SENSITIVE`; do not publish it.

## Next build sequence

1. Land and verify the current `kovaos-site` Cloudflare Worker/Railway migration foundation without changing production DNS.
2. Land the current Core runtime-security hardening and keep canonical repository/webhook boundaries fail-closed.
3. Connect Railway and create a non-production web backend service from `kovaos-site`; do not claim production until deployment status is terminal-success and preview smoke tests pass.
4. Define and prove the versioned Core-to-app `/api/v1` contract. Keep the FastAPI Core runtime separate from the web Node backend.
5. Select a dedicated FastAPI Core destination only after its environment names/scopes are reconciled; preserve the current verified Core surface as rollback until then.
6. Prove one AI-provider route and one connector route end to end, then perform the public edge cutover with a tested rollback path.

Normal KOVA use should be no-code. Agents maintain code and integrations; the dashboard exposes understandable controls and asks for approval only for high-impact actions.
