# KOVA OS Current Guide

## What KOVA is

KOVA is one personal AI operating system with one control plane and one primary application. It should reduce manual work, not create a maze of dashboards, folders, and repositories.

## Canonical platform

- **Core:** `Kathrynhiggs21/Kova-ai-SYSTEM`
- **Authenticated app:** `Kathrynhiggs21/kovaos-site`
- **Primary domain:** `kovaos.com`
- **Hosting target:** Cloudflare edge/static delivery plus Railway persistent services; urgent Vercel exit, with verified rollback and current private Sites entry preserved until cutover.
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
- reproducible protected deployment of both active repositories; and
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

1. Merge and verify deterministic CI for `kovaos-site`.
2. Merge the MCP malformed-input hardening after all required security checks pass.
3. Finish the safe metadata-registry implementation and resolve all review findings.
4. Define and implement the versioned Core-to-app `/api/v1` contract.
5. Prove one AI-provider route and one connector route end to end.

Normal KOVA use should be no-code. Agents maintain code and integrations; the dashboard exposes understandable controls and asks for approval only for high-impact actions.

## Hosting migration priority — October 19, 2026

The owner has directed urgent replacement of Vercel across KOVA. The target already recorded by the canonical web repository is **Cloudflare edge/static delivery plus Railway persistent services**. Keep the existing FastAPI control plane and Node/Express web backend behind their current contracts; do not rewrite either into a Worker merely to change hosts.

- Vercel is legacy migration/rollback infrastructure, not the target for new KOVA deployment or service configuration.
- `kovaos.com` and `www.kovaos.com` currently belong to private ChatGPT Sites according to the October 19 registry decision and web PR #38. Keep that entry intact until the replacement is verified. A target architecture is not evidence of cutover.
- Follow the [canonical web deployment guide](https://github.com/Kathrynhiggs21/kovaos-site/blob/main/docs/deployment/cloudflare-railway.md) and reconcile [domain isolation PR #38](https://github.com/Kathrynhiggs21/kovaos-site/pull/38). Never attach wildcard KOVA routes or mix Scribbles identity/routing into KOVA.
- Inventory Vercel project/domain links, Git integrations, checks, environment **names**, callbacks, scheduled jobs, storage and analytics dependencies. Preserve source history and a tested rollback; never publish secret values.
- Stage Cloudflare-to-Railway routing and require real application health JSON, intended-account login, anonymous denial, secure callback/cookies, protected routes, logout and persistence. An Access login page returning HTTP 200 is not backend health.
- After replacement acceptance, disable Vercel automatic Git deployments and mandatory legacy checks, remove active setup instructions and retire projects/billing dependencies through the verified provider workflow. Historical references remain explicitly historical; package-lock mentions alone do not establish a hosting dependency.

Current Core integration and frontend-auth work remain staged: [Core PR #147](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/147) and [web PR #33](https://github.com/Kathrynhiggs21/kovaos-site/pull/33) are draft/unmerged as read October 19. No production cutover, project deletion, credential transfer or billing change is performed by this documentation update.
