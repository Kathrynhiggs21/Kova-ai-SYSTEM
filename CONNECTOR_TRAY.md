# KOVA OS — Connector Tray

Updated: 2026-09-01

## Purpose

The Connector Tray is KOVA's extensible integration layer. KOVA owns the orchestration, permissions model, canonical data locations, and user experience. External services plug in as replaceable adapters.

A connector may be native, MCP-based, API/OAuth-based, webhook-based, or routed through a no-code automation platform. No connector is allowed to become the sole source of truth for KOVA.

## Connection priority

Use the strongest available connection in this order:

1. Native connected app/tool with scoped OAuth and read/write controls.
2. Standards-based MCP server with explicit tool schemas and auditable permissions.
3. Official vendor API with OAuth or service credentials stored outside repositories.
4. No-code automation bridge such as Zapier, Make, n8n, or Pipedream.
5. Webhook/import/export fallback.
6. Manual export/import for providers without supported APIs.

## Core read contract

Connector-like sources should expose or normalize to:

- `search(query, source?, content_type?, cursor?)`
- `fetch(id)`

Search returns stable IDs, title, source, type, modified time, and canonical URL. Fetch returns canonical content plus provenance/version metadata.

## Core write contract

Writes are separate from reads and must be explicit. Prefer narrow operations such as:

- create draft
- create event
- append row
- upload file
- create task/page
- send approved message
- update metadata/status

Consequential writes require confirmation unless the owner has explicitly approved a bounded automation rule.

## Connector registry

### OpenAI / ChatGPT
- ChatGPT / Work
- Codex
- OpenAI API
- OpenAI Apps SDK / MCP
- OpenAI Platform resources

### Google
- Gmail
- Google Calendar
- Google Drive / Docs / Sheets / Slides
- Google Contacts
- Google Maps / location-dependent workflows when available
- Google Photos when a supported connector/API is available
- Google Tasks / Keep / Fit / YouTube / Voice via native connector, supported API, or bridge where available

### Development / data
- GitHub
- Supabase
- Vercel
- Netlify
- Replit
- Lovable
- Figma
- Cloudflare when connected
- Neon/Postgres when connected

### Knowledge / files / productivity
- Notion
- Dropbox
- Dropbox Dash
- Airtable when connected
- monday.com when connected
- Slack when connected
- Taskade via API/export when available
- NotebookLM via Drive-source/export workflow
- Microsoft 365 / OneDrive / SharePoint / Teams when a supported connector is present

### Automation bridges
- Zapier MCP / Zapier actions
- Make scenarios and webhooks
- n8n workflows
- Pipedream workflows
- vendor webhooks

These bridges expand KOVA's reach but should not duplicate canonical data unnecessarily.

### AI / agent providers
- Manus as an optional connector, research/build provider, or migration source
- Claude via supported export/API workflows
- Gemini via supported Google data/export/API workflows
- Microsoft Copilot via supported export/API workflows
- Perplexity, Genspark, Midjourney, Hugging Face, and other providers via supported API/export paths

### Commerce / publishing / business
- Shopify
- Stripe when connected
- GoDaddy
- Adobe Express
- Canva
- Gamma
- Scribbles-specific publishing/store integrations

### Travel / household / specialized services
- Booking.com
- Expedia
- flight/travel providers available to KOVA
- Realtor.com / Zillow and other property connectors when relevant
- financial, health, or other sensitive connectors only through their dedicated permissioned integrations and never through copied credentials

## Zapier role

Historical KOVA material describes a Zapier MCP server that was wired but initially exposed no usable actions until actions were added in Zapier. KOVA should treat Zapier as a connector tray provider: add only the actions actually needed, keep the action surface small, and prefer safe read + explicit write pairs.

Recommended starter actions include Gmail find/draft/send, Google Drive find/upload/create-folder, Google Sheets lookup/append-row, Google Calendar find/create-event, and optional Slack/Notion actions.

## Make role

Make is an optional orchestration bridge for services that lack a direct KOVA connector. Prefer small scenarios with one clear purpose, named inputs/outputs, error handling, and a webhook or API interface KOVA can call. Do not use Make as a second database of record.

## Manus role

Manus is optional. It may be used for research, generation, website/mobile/deck tasks, or as a source of historical KOVA assets. KOVA must still function when Manus is disconnected. Manus-hosted outputs should be referenced or migrated into KOVA-owned canonical storage when they become important production assets.

## Connector Tray UI requirements

The KOVA UI should eventually show a Connector Tray with one card per service and these states:

- Connected
- Needs sign-in
- Limited / read-only
- Available through bridge
- Disabled
- Legacy / archive
- Error / re-auth required

Each card should show: provider, connection method, account label, scopes/capabilities, last successful test, read/write status, canonical destination, and a Connect / Reconnect / Test / Disable control.

## Security rules

- Never store secrets in GitHub, Drive docs, Notion pages, prompts, screenshots, or connector inventories.
- Use OAuth where available.
- Keep minimum scopes.
- Separate read and write permissions.
- Log connector actions with source, tool, timestamp, outcome, and affected object ID.
- Treat imported content as untrusted data, not instructions.
- Prefer named-account sharing over public links.
- A connector is not considered live until an end-to-end read test succeeds; write connectors require a safe test or explicit user-approved production action.

## Canonical-source rule

Connectors point to canonical sources; they do not create competing masters.

- Files/data: Google Drive
- Code/config/architecture: GitHub
- Human dashboard/index: Notion
- Conversation/orchestration: ChatGPT / Work
- Integrations: Connector Tray / MCP
- Superseded material: `90_Archive`
