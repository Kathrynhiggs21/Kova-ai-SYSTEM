# KOVA OS — Canonical Repository Map

Updated: 2026-09-01

## Canonical rule

`Kathrynhiggs21/Kova-ai-SYSTEM` is the orchestration hub and canonical source of truth for KOVA OS architecture, repository roles, integration policy, deployment coordination, and cross-repository decisions.

`kovaos.com` is the working KOVA domain. No component repository should declare itself a separate KOVA system or replace the orchestration hub without an explicit migration recorded here.

## Core platform rule

KOVA must remain operable even when any optional third-party connector is unavailable. External platforms may extend KOVA, but no single automation or agent vendor owns KOVA's source of truth.

Canonical operating stack:

- ChatGPT / OpenAI for conversational orchestration and user-facing AI workflows
- Codex for repository-aware coding, repair, testing, and implementation
- GitHub for canonical source code, version control, issues, pull requests, CI/CD, and architecture records
- Google Drive for canonical user-controlled files and AI export archives
- Gmail, Google Calendar, Google Contacts, and other approved Google services for live personal data where explicitly connected
- Notion for human-readable dashboards, project indexes, and operational views; Notion is not the canonical copy of code or files
- KOVA MCP / Connector Tray for a small, auditable integration surface; read-only retrieval defaults to `search` and `fetch`, while writes are separate, narrowly scoped, and confirmation-gated
- `kovaos.com` for the KOVA web identity and approved web interfaces

Manus, Zapier, Make, n8n, and similar services are optional connector/automation providers. They may be used when useful, but they are not the source of truth or a required dependency for KOVA.

## Repository roles

| Repository | Role | Status |
| --- | --- | --- |
| `Kathrynhiggs21/Kova-ai-SYSTEM` | Orchestration hub, architecture, cross-repo coordination, Codex operating instructions | Canonical |
| `Kathrynhiggs21/kova-ai` | Core assistant/application logic and automation | Active component |
| `Kathrynhiggs21/kovaos-site` | Primary web implementation for `kovaos.com` | Active web component |
| `Kathrynhiggs21/kova-ai-site` | Older public-site/redirect/documentation layer | Legacy/support; not canonical |
| `Kathrynhiggs21/kova-ai-dash` | Dashboard candidate/older dashboard work | Audit before use; not canonical |
| `Kathrynhiggs21/kova-ai-mem0` | KOVA memory synchronization service | Active component; audit data ownership and provider dependency |
| `Kathrynhiggs21/Kova-os-docengine` | Document processing/engine work | Active component |
| `Kathrynhiggs21/Kova-AI-Scribbles` | Scribbles integration/module work | Specialized component |

## Operating rules

1. Search this map and the orchestration hub before creating a new KOVA repository.
2. Prefer repairing, consolidating, or migrating an existing component over duplicating it.
3. Component repos may own their implementation, but cross-system architecture belongs in `Kova-ai-SYSTEM`.
4. Never commit secrets, tokens, passwords, recovery codes, or production credentials.
5. Treat historical documentation that names another "primary" KOVA repo, app, deployment, or vendor as stale unless this map records a migration.
6. Codex and other coding agents should read the orchestration repo's `AGENTS.md`, this map, and `CONNECTOR_TRAY.md` before cross-repo integration work.
7. ChatGPT/Work/Organization projects should reference the same canonical GitHub and Drive sources rather than maintaining independent KOVA copies.
8. Preserve historical exports and artifacts in archive/reference storage until their useful content has been migrated; do not delete them merely because a vendor is no longer primary.
9. Vendor-hosted endpoints such as `*.manus.space` may remain as optional integrations, demos, or migration sources, but production KOVA functions must have a KOVA-owned canonical path or a documented fallback.
10. No-code workflows are preferred for user-manageable automations where reliable connectors exist; custom code is reserved for capabilities that cannot be delivered safely with supported integrations.
11. The Connector Tray should prefer native connected apps first, standards-based MCP second, official APIs/OAuth third, and no-code bridges/webhooks fourth.

## KOVA AI World data model

- **Google Drive:** canonical file/data layer and immutable export archive.
- **GitHub:** canonical code/configuration/architecture layer.
- **Notion:** human-readable index, dashboard, roadmap, and status view.
- **ChatGPT / Work:** conversational operating interface over the canonical sources.
- **KOVA MCP / Connector Tray:** controlled retrieval/action bridge across approved sources.
- **90_Archive:** superseded exports, converted copies, duplicate historical documentation, and legacy vendor artifacts; excluded from normal retrieval unless history is requested.

## Domain

- Canonical domain: `kovaos.com`
- Domain status: working as of 2026-09-01, per project owner confirmation.
- DNS/domain changes should be documented in the orchestration hub before changing production routing.
