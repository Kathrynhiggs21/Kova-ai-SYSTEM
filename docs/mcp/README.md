# KOVA MCP v0.1

Core already owns MCP at `POST /mcp`; this change extends that endpoint in place. It does not deploy over the Node web backend, introduce another repository, or switch identity providers. See root `SPEC.md` for the agreed scope.

## Features

- Eight read-only tools provide a today snapshot, digest, enabled project references, GitHub metadata, calendar events and integration checks.
- `open_kova_dashboard` selects the owner-protected `ui://kova/dashboard.html` resource. The HTML is a compact responsive, script-free snapshot using the standard MCP Apps MIME type. MCP Apps-capable hosts may render it; other hosts can use the same structured/text tool result. Rendering inside ChatGPT is not yet verified.
- Existing `kova_*` tools remain available. Tool results also include `structuredContent`.
- Daily digests are source summaries, not model-generated priorities or promises that work completed. No OpenAI credential is required for this first version.

## Authentication and client boundary

The existing server-side `KOVA_OWNER_API_KEY` protects discovery, calls and resources through `X-Kova-API-Key`. Missing configuration denies access. A ChatGPT-connected app is not proof that the Core runtime has provider permissions.

This is currently a trusted owner-header MCP transport, not a complete MCP OAuth authorization server. Do not paste an owner key into the dashboard, commit it, publish it, or disable authentication to make a client connect. Verify the chosen client's support for the existing header, or implement a separately reviewed OAuth/gateway integration before claiming direct ChatGPT connection. A tunnel client does not supply a missing server or authorization boundary.

## Approved configuration

Use Railway/Core's approved server secret store; templates contain names only.

| Name | Purpose |
| --- | --- |
| `KOVA_OWNER_API_KEY` | Existing Core owner authorization |
| `GITHUB_TOKEN` | Approved read access to enabled repository metadata; prefer a narrowly scoped installation credential |
| `KOVA_TIMEZONE` | Day boundary; defaults to `America/New_York` |
| `KOVA_GOOGLE_CLIENT_ID` | Dedicated approved Google client |
| `KOVA_GOOGLE_CLIENT_SECRET` | Matching secret |
| `KOVA_GOOGLE_CALENDAR_REFRESH_TOKEN` | Dedicated approved read-only Calendar grant |
| `KOVA_GOOGLE_CALENDAR_ID` | The one permitted calendar; never a caller argument |

The Calendar token response must prove `calendar.events.readonly` or `calendar.readonly`, with no content-write or unrelated data scopes. Missing/unverifiable scopes fail closed. No authorization redirect or new permission grant is performed by the adapter. Provider consent and account selection remain a prerequisite.

No Calendar request retrieves attendees, descriptions or location. Reads are bounded to one day, 100 events per page and 10 pages. Overflow is `partial`, never a successful empty result. Identical iCalUID/occurrence pairs deduplicate; equal titles alone do not. Distinct recurring occurrences remain distinct.

Provider snapshots have a 60-second private process cache bounded to 32 entries and scoped to configuration, owner key and enabled repository set. `refresh_integration` invalidates the selected provider's snapshots and performs a read probe. No content writes or persistent mirror is created. Changing credentials or registry identity cannot reuse the prior cache.

## Validate and release

Run the existing platform checks and the full test suite from the README. `scripts/smoke_mcp.py` verifies owner rejection, initialization, discovery, legacy tool compatibility, the dashboard and its resource against a running Core API. The existing container CI job runs it inside the built Core image. New tests use synthetic HTTP transport and account values; passing them does not verify live credentials.

Release through a reviewed Core PR and existing `verify-platform` / container checks. Before launch verify an owner-authenticated MCP initialize, discovery, resource read and real GitHub/Calendar reads through the intended Core deployment and host. Anonymous/wrong-owner requests must fail. No private data belongs on an unauthenticated health endpoint. Do not change kovaos.com, provider identities, database schemas or the separate Node service as part of this source release.

Status at implementation: source and synthetic tests implemented; live provider authorization, host rendering and production MCP deployment remain unverified. Contacts, Manus, Dropbox, Notion and OpenAI report `not_implemented` until their approved runtime adapters exist.
