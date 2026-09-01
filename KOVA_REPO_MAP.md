# KOVA OS — Canonical Repository Map

Updated: 2026-09-01

## Canonical rule

`Kathrynhiggs21/Kova-ai-SYSTEM` is the orchestration hub and canonical source of truth for KOVA OS architecture, repository roles, integration policy, deployment coordination, and cross-repository decisions.

`kovaos.com` is the working KOVA domain. No component repository should declare itself a separate KOVA system or replace the orchestration hub without an explicit migration recorded here.

## Core platform rule

KOVA must not depend on Manus to operate. Manus-era applications, URLs, exports, documents, and generated code are historical/reference material only unless they are explicitly migrated into the canonical KOVA stack and verified there.

Canonical operating stack:

- ChatGPT / OpenAI for conversational orchestration and user-facing AI workflows
- Codex for repository-aware coding, repair, testing, and implementation
- GitHub for canonical source code, version control, issues, pull requests, CI/CD, and architecture records
- Google Drive for canonical user-controlled files and AI export archives
- Gmail, Google Calendar, Google Contacts, and other approved Google services for live personal data where explicitly connected
- Notion for human-readable dashboards, project indexes, and operational views; Notion is not the canonical copy of code or files
- KOVA MCP for a small, auditable integration surface; read-only retrieval defaults to `search` and `fetch`, while writes are separate, narrowly scoped, and confirmation-gated
- `kovaos.com` for the KOVA web identity and approved web interfaces

Manus is not a production dependency, source of truth, deployment authority, or required connector for KOVA.

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
5. Treat historical documentation that names another "primary" KOVA repo, Manus app, Manus deployment, or Manus URL as stale unless this map records a migration.
6. Codex and other coding agents should read the orchestration repo's `AGENTS.md` and this map before cross-repo work.
7. ChatGPT/Work/Organization projects should reference the same canonical GitHub and Drive sources rather than maintaining independent KOVA copies.
8. Preserve historical Manus exports and artifacts in archive/reference storage until their useful content has been migrated; do not delete them merely to remove the dependency.
9. Any service currently calling a `*.manus.space` endpoint must be treated as migration-required and replaced with a KOVA-owned endpoint before being considered production-ready.
10. No-code workflows are preferred for user-manageable automations where reliable connectors exist; custom code is reserved for capabilities that cannot be delivered safely with supported integrations.

## KOVA AI World data model

- **Google Drive:** canonical file/data layer and immutable export archive.
- **GitHub:** canonical code/configuration/architecture layer.
- **Notion:** human-readable index, dashboard, roadmap, and status view.
- **ChatGPT / Work:** conversational operating interface over the canonical sources.
- **KOVA MCP:** controlled retrieval/action bridge across approved sources.
- **90_Archive:** superseded exports, converted copies, duplicate historical documentation, and Manus-era artifacts; excluded from normal retrieval unless history is requested.

## Domain

- Canonical domain: `kovaos.com`
- Domain status: working as of 2026-09-01, per project owner confirmation.
- DNS/domain changes should be documented in the orchestration hub before changing production routing.
