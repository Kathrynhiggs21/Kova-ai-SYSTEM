# KOVA OS — Canonical Repository Map

Updated: 2026-09-15

## One-system rule

KOVA OS is one product spread across a small number of deliberately scoped repositories. `Kathrynhiggs21/Kova-ai-SYSTEM` is the canonical coordination and architecture hub. `kovaos.com` is the canonical product domain. A repository is not a separate KOVA system merely because its name contains KOVA.

The runtime registry is `kova_repos_config.json`. An entry with `enabled: false` is catalogued but is not automatically synchronized, analyzed, or deployed.

## Repository portfolio

| Repository | Clear role | Portfolio status | Runtime |
| --- | --- | --- | --- |
| `Kathrynhiggs21/Kova-ai-SYSTEM` | Architecture, FastAPI control plane, MCP endpoint, deployment coordination, repository registry | Canonical hub | Enabled |
| `Kathrynhiggs21/kovaos-site` | Primary web implementation for `kovaos.com` | Active web candidate; private and requires a dedicated build/deployment audit | Catalogued |
| `Kathrynhiggs21/kova-ai-dash` | React dashboard and integration hub | Active dashboard candidate; authentication hardened in PR #5 | Enabled |
| `Kathrynhiggs21/kova-ai` | Mixed assistant/application code plus historical generated assets | Migration source; audit directories before promoting any code | Catalogued |
| `Kathrynhiggs21/kova-ai-mem0` | Memory-provider adapter placeholder | Experimental component; no production data authority | Catalogued |
| `Kathrynhiggs21/Kova-os-docengine` | Document ingestion/transformation placeholder | Experimental component | Catalogued |
| `Kathrynhiggs21/Kova-AI-Scribbles` | Optional Scribbles integration | Specialized placeholder; Scribbles itself remains an independent world | Catalogued |
| `Kathrynhiggs21/kova-ai-site` | Older public site, redirect, and documentation material | Legacy migration source | Catalogued |
| `Kathrynhiggs21/mem0` | Generic private placeholder | Not a KOVA product repo; inspect before archive | Excluded |
| `Kovaos-com/vite-react` | Unmodified Vite starter under the KOVA organization | Empty experiment; do not deploy as KOVA | Excluded |
| `Kathrynhiggs21/platforms-starter-kit` | Generic private platform starter | Reference/experiment; not KOVA production | Excluded |

## Canonical product paths

These are URL paths, not Git branches and not instructions to create duplicate repositories:

| URL | Owner |
| --- | --- |
| `https://kovaos.com/` | Primary web implementation |
| `https://kovaos.com/dashboard` | Dashboard user interface |
| `https://kovaos.com/ai` | KOVA assistant experience |
| `https://kovaos.com/mcp` | Authenticated MCP endpoint and connector status |
| `https://kovaos.com/files` | User-controlled file index |
| `https://kovaos.com/settings` | Connections, privacy, and account settings |
| `https://kovaos.com/admin` | Owner-only administration |

## Naming standard

- Product name: **KOVA OS**
- Assistant name: **KOVA AI Assistant**
- Domain: **kovaos.com**
- Repository slugs: lowercase kebab-case for any future repository
- Branches: `main`, `feature/<topic>`, `fix/<topic>`, or `codex/<topic>`
- Do not use `k9va`, `kiva`, `kovoas`, numbered copies, or vendor-generated random suffixes as canonical names.

Existing repository names are retained until GitHub redirects, deployments, imports, and documentation can be verified. Renaming is a migration, not a cosmetic edit.

## Source-of-truth boundaries

- GitHub: code, configuration, architecture, issues, PRs, CI/CD.
- Google Drive: user-owned files and immutable export archives.
- Notion: human-readable indexes and operational views, never the only copy of code or files.
- ChatGPT/Work: conversational interface over canonical sources.
- KOVA MCP/Connector Tray: narrow, auditable retrieval and action bridge.

No optional vendor—including Manus, Zapier, Make, n8n, Mem0, or a model provider—owns KOVA's source of truth.

## Change rules

1. Search this map before creating another repository.
2. Migrate useful code through reviewed PRs; never copy whole repositories together blindly.
3. Never store passwords, access tokens, OAuth secrets, private keys, or recovery codes in Git.
4. Keep catalogued repositories disabled until their build, tests, secrets, ownership, and deployment path are verified.
5. Archive only after unique code and history have been assessed. Do not delete repositories as an organization shortcut.
6. Record any canonical-role change here and in `kova_repos_config.json` in the same PR.
