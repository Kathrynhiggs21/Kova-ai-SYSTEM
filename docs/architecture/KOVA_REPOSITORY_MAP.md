# KOVA OS Repository Map

Status: Canonical remediation map v2 · 2026-09-15

This document and `kova_repos_config.json` supersede older repository maps. The runtime active set is exactly the registry entries whose `enabled` value is `true`.

## Active repositories

| Repository | Responsibility | Status |
|---|---|---|
| `Kathrynhiggs21/Kova-ai-SYSTEM` | Core, backend, orchestration, MCP, shared contracts and internal service modules | ACTIVE |
| `Kathrynhiggs21/kovaos-site` | Canonical web application for `kovaos.com` | ACTIVE |

`kova-ai-dash` is a disabled feature donor. `kova-ai`, `kova-ai-mem0`, `Kova-os-docengine`, `Kova-AI-Scribbles` and `kova-ai-site` remain disabled migration, experimental or legacy sources until the registry explicitly promotes one.

Scribbles and Zoo/educational-card repositories are independent Worlds/products. They may integrate with KOVA but do not become Core repositories.

## Modular Core

The following are internal modules in `Kova-ai-SYSTEM`, not repositories by default:

- orchestration and shared contracts;
- AI Assistant and current/future provider adapters;
- MCP transport and tools;
- connectors and webhooks;
- automation and jobs;
- memory and operational data;
- files, artifacts and exports;
- security and identity; and
- health and observability.

The exact current ownership paths and the single machine-readable split policy are in `config/core_modules.v1.json`.

## Repository split rule

A module can become a repository only when an independent deployment, security/secrets boundary, materially different scaling profile, independent release cycle, or separate product/team ownership exists. The split also requires owner approval, CI, deployment ownership, versioned interfaces, rollback and a registry update.

A category name, future idea, temporary experiment or visual neatness is not enough.

## Explicit exclusion

The existing Zoo/card renderer and `scripts/batch_renderer.py` are not KOVA Core automation. Do not migrate them into Assistant, MCP, connectors, memory, automation, infrastructure or the canonical site.

## Rules

1. Keep one canonical owner per production responsibility.
2. Prefer modules before repositories.
3. Do not show disabled or unverified integrations as live.
4. Keep secrets out of repositories.
5. Keep cross-repository writes disabled until ownership, authentication and tests are proven.
6. Use pull requests and exact-head checks for production work.
