# KOVA OS — Canonical Repository Map

Updated: 2026-09-01

## Canonical rule

`Kathrynhiggs21/Kova-ai-SYSTEM` is the orchestration hub and canonical source of truth for KOVA OS architecture, repository roles, integration policy, deployment coordination, and cross-repository decisions.

`kovaos.com` is the working KOVA domain. No component repository should declare itself a separate KOVA system or replace the orchestration hub without an explicit migration recorded here.

## Repository roles

| Repository | Role | Status |
| --- | --- | --- |
| `Kathrynhiggs21/Kova-ai-SYSTEM` | Orchestration hub, architecture, cross-repo coordination, Codex operating instructions | Canonical |
| `Kathrynhiggs21/kova-ai` | Core assistant/application logic and automation | Active component |
| `Kathrynhiggs21/kovaos-site` | Primary web implementation for `kovaos.com` | Active web component |
| `Kathrynhiggs21/kova-ai-site` | Older public-site/redirect/documentation layer | Legacy/support; not canonical |
| `Kathrynhiggs21/kova-ai-dash` | Dashboard candidate/older dashboard work | Audit before use; not canonical |
| `Kathrynhiggs21/kova-ai-mem0` | KOVA memory synchronization service | Active component |
| `Kathrynhiggs21/Kova-os-docengine` | Document processing/engine work | Active component |
| `Kathrynhiggs21/Kova-AI-Scribbles` | Scribbles integration/module work | Specialized component |

## Operating rules

1. Search this map and the orchestration hub before creating a new KOVA repository.
2. Prefer repairing, consolidating, or migrating an existing component over duplicating it.
3. Component repos may own their implementation, but cross-system architecture belongs in `Kova-ai-SYSTEM`.
4. Never commit secrets, tokens, passwords, recovery codes, or production credentials.
5. Treat historical documentation that names another "primary" KOVA repo as stale unless this map records a migration.
6. Codex and other coding agents should read the orchestration repo's `AGENTS.md` and this map before cross-repo work.
7. ChatGPT/Work/Organization projects should reference the same canonical GitHub and Drive sources rather than maintaining independent KOVA copies.

## Domain

- Canonical domain: `kovaos.com`
- Domain status: working as of 2026-09-01, per project owner confirmation.
- DNS/domain changes should be documented in the orchestration hub before changing production routing.
