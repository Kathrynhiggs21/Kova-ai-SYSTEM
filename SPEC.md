# KOVA MCP v0.1

## Outcome and users

The private owner can ask ChatGPT to open a compact KOVA command center, summarize a day, inspect enabled GitHub projects and check integrations without opening several consoles. The assistant supplies intent and summaries; Core supplies authorized source data and evidence. This is a focused conversational surface, not a port of the whole website.

## Existing product and architecture

Extend Core's existing owner-authenticated FastAPI `/mcp` endpoint and repository registry in place. Keep Cloudflare + Railway, `kovaos-site` as the canonical website, and Drive as the home for user documents. Do not scaffold a competing Skybridge server, repository, identity store or dashboard database. No Firebase/Descope/Auth0 cutover, Vercel reactivation or live-domain change is included.

## Experience

- Open: show today, calendar, enabled projects, integration evidence, blockers and next steps in a compact MCP HTML resource and structured tool output.
- Digest: request an ISO date or use today in the configured timezone; return bounded calendar data and GitHub repository metadata. No claim of GitHub activity, task completion or AI synthesis without that source.
- Inspect: list enabled projects, inspect one enabled project, check integrations or explicitly refresh a read probe.
- Missing credentials, inaccessible providers and incomplete pagination remain visible. Empty results are successful reads only after provider evidence.

## Tools and view

`open_kova_dashboard`, `get_kova_status`, `get_daily_digest`, `get_calendar_events`, `get_integration_status`, `refresh_integration`, `list_kova_projects`, `get_project_status`.

Preserve existing `kova_*` tools. The owner-protected `ui://kova/dashboard.html` resource uses `text/html;profile=mcp-app`, semantic HTML, escaped data, responsive layout and no scripts, external assets or network requests. Browsing state remains in the host; tools perform real reads. The resource is a current snapshot; refresh by calling the tool again.

## Security and sources

Require the existing server-only `X-Kova-API-Key` boundary for discovery, tools and resources. This header-based owner transport is not OAuth and must not be advertised as direct ChatGPT OAuth support. Client compatibility and any authenticated gateway/tunnel must be verified before connection. Do not expose keys through a browser or resource.

GitHub reads only enabled registry coordinates with server credentials. Calendar reads only one server-configured calendar using a dedicated approved read-only Google grant. Never accept a URL, token, tenant, calendar ID or arbitrary repository from tool callers. Token refresh is allowed; content writes are not. Do not create tasks, share files, delete integrations or start automations.

Read-only providers use bounded timeouts, bounded pagination and a short private process cache scoped to provider configuration. Calendar deduplication uses stable iCalUID plus occurrence start, never title similarity alone. Preserve distinct recurring occurrences. No durable private-data mirror.

## Acceptance

Test owner rejection before external access, discovery and old-tool compatibility, typed/closed input validation, provider failure redaction, missing credentials, authorized GitHub reads, pagination, timezone/DST day windows, recurring deduplication, cache/refresh, resource escaping and source restrictions. Run the existing source gates and container smoke when supported. Report synthetic tests separately from live credentials, deployment and ChatGPT tool discovery.

## Release

Develop on `feat/mcp-v01`, open a draft PR, require existing CI gates. Deploy only after approved Core credentials and client transport compatibility are verified. Roll back by reverting the focused PR or selecting the previous Core image; do not modify the separate Node web backend. Host rendering and authenticated live provider acceptance remain required before declaring launch complete.
