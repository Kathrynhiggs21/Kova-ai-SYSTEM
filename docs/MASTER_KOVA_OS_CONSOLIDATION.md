# Master KOVA OS Consolidation

## Canonical product
KOVA OS at `kovaos.com` is the single personal operating system, AI assistant, command center, and connector layer. It is not a Manus-owned system and it is not a collection of competing dashboards.

## Canonical sources
- Technical control plane: `Kathrynhiggs21/Kova-ai-SYSTEM`
- Primary web/dashboard implementation: `Kathrynhiggs21/kovaos-site`
- Document/data index: Google Drive `KOVA AI Sync Hub` and its `00_MASTER_KOVA_OS` folder
- Human-readable workspace/index: Notion, as a view/reference layer rather than the source of truth
- DNS/edge: Cloudflare for `kovaos.com`

## Master Drive states
`00_MASTER_KOVA_OS` contains five lifecycle buckets:
1. `01_ACTIVE_CANONICAL` — current authoritative artifacts
2. `02_REFERENCE` — useful supporting material that is not authoritative
3. `03_PURGATORY_REVIEW_MERGE` — duplicates, conflicts, unclear ownership, or material awaiting merge
4. `04_ARCHIVE_SUPERSEDED` — confirmed obsolete/superseded material retained for history
5. `05_SECURITY_QUARANTINE` — credentials, tokens, API-key references, private access records, and other sensitive material

Nothing is deleted merely because it is old or duplicated. Ambiguous items go to Purgatory first.

## Connector policy
KOVA owns the orchestration. Every external service is an interchangeable connector/adaptor.

Preferred connection order:
1. Native connector/app
2. MCP
3. Official API/OAuth
4. Automation bridge (Zapier, Make, n8n, Pipedream, etc.)
5. Webhook/export/import fallback

Examples include OpenAI/ChatGPT/Codex, Google Drive/Gmail/Calendar/Contacts, NotebookLM/Gemini/Google Labs, GitHub, Notion, Dropbox, OneDrive, Box, Cloudflare, Vercel, Supabase, Canva, Adobe, Gamma, Manus, Zapier, Make, and Android companion services.

Manus is optional and must never be required for KOVA to operate.

## Identity policy
KOVA is one system with multiple authorized identities. `katy@kovaos.com` and `spear.cpt@gmail.com` should point to the same KOVA profile and canonical data, with provenance retained per connected account. They must not create parallel KOVA instances or duplicate master records.

## Repository target state
Keep active repositories only when they have a distinct deployable/runtime responsibility. Unique code from duplicate or legacy KOVA repositories should be migrated before those repositories are archived.

Target responsibilities:
- `Kova-ai-SYSTEM`: orchestration/backend/control plane, connector registry, shared schemas, operating rules
- `kovaos-site`: primary KOVA web app/dashboard at `kovaos.com`
- Optional specialized repos only when technically justified (e.g. document engine or memory service)
- Scribbles/Reagan projects remain separate products/modules and integrate with KOVA rather than being merged blindly into the OS codebase

## Deduplication rules
- Exact duplicates: retain one canonical file plus references/shortcuts.
- Converted copies (DOCX/PDF/Google Doc of same source): keep the best editable source canonical; use rendered copies only when needed.
- Contradictory masters: merge unique facts into the current master, then move old versions to archive.
- Legacy vendor instructions: preserve as reference/archive but remove authority labels.
- Credential/API-key documents: security quarantine; never publish or place secrets in dashboards.
- Gmail/Chrome/bookmark/history evidence: evidence that an account/service may exist, not proof of current connection.
- Connector status is only `Verified` after a current live test.

## Current known cleanup findings
- Multiple Notion `Kova OS — Master Dashboard` pages exist.
- Multiple Notion `Integration Status`, `Kova OS World`, and integration setup pages exist.
- Old Notion Android/DroidMind instructions assume Manus as the MCP host; these are legacy.
- Multiple Drive copies/conversions of `Kova_OS_Master_Connector_Record` exist.
- Multiple Drive copies/conversions of Gmail MCP connector reports exist.
- Dropbox contains duplicate KOVA files in root and `Mobile Uploads`.
- Google Drive contains a June 2026 Takeout ZIP that should be inventoried, not duplicated into active folders.
- OneDrive is an active cloud source and Box has current Google-account authorization evidence; both belong in the connector inventory.

## No-code operating rule
The owner should not be required to code for normal KOVA use. Codex/agents may maintain code, integrations, schemas, and deployments, while the dashboard and connector tray expose understandable no-code controls.

## Next consolidation sequence
1. Inventory every reachable KOVA artifact and connected storage source.
2. Build the live connector/account registry.
3. Merge current product requirements into one Master KOVA specification.
4. Move exact/near duplicates into Purgatory or Archive only after canonical selection.
5. Quarantine security-sensitive references.
6. Consolidate repo code into the smallest sensible active repository set.
7. Make `kovaos.com` the primary user interface: orb + waves, command bar, dashboard, modules, accounts, projects, connections, status, tasks, family, work, Scribbles, finance, pets, travel and Android companion access.
