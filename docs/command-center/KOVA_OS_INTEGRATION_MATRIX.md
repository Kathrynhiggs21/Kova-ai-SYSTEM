# KOVA OS Integration Matrix

## Evidence states

- **Runtime verified** - a current KOVA production read or write/readback succeeded.
- **Assistant access** - the connected assistant can reach the service, but KOVA runtime integration is not proven.
- **Designed** - a specification or adapter boundary exists.
- **Blocked** - access, deployment, security, or an owner decision is required.
- **Disabled** - intentionally excluded from the active runtime.

Configuration alone is never proof of health. A successful read, Git push, or staged provider mutation proves only that operation at that time; it does **not** enumerate granted OAuth/API scopes or authorize future operations. `UNKNOWN` means evidence is unavailable; `INCOMPLETE` means required identity or permission evidence is still missing.

Reviewed 2026-10-21. Provider observations attributed to the coordinator below were supplied in this task; this session did not independently read provider accounts. Other inherited status claims are not fresh access checks.

| Integration | Current evidence | KOVA role | Next proof |
|---|---|---|---|
| GitHub | Git fetch and PR-branch push verified in this task; API reads returned Forbidden | Code, PRs, CI, release evidence | Protect and validate both active default branches |
| `Kova-ai-SYSTEM` | Active Core; CI exists | Backend, orchestration, MCP, contracts | Deploy the backend and verify authenticated health/MCP calls |
| `kovaos-site` | Canonical app; current PR and production acceptance UNKNOWN | Authenticated interface for `kovaos.com` | Merge CI and verify protected production login/routes |
| Google Drive | Historical assistant-access claim; current access UNKNOWN; KOVA runtime unverified | Canonical user files and private registry | Run metadata inventory with readback and no source mutation |
| Gmail | Historical assistant-access claim; current access UNKNOWN; KOVA runtime unverified | Triage and approved drafts/actions | Prove least-privilege read, then approved send flow |
| Google Calendar | Historical assistant-access claim; current access UNKNOWN; KOVA runtime unverified | Agenda, conflicts, reminders | Prove read and approved event creation/readback |
| Notion | Historical assistant-access claim; current access UNKNOWN; KOVA runtime unverified | Human-readable view only | Verify one canonical view without duplicate masters |
| OpenAI/model providers | Designed | AI Assistant behind provider-neutral interface | Prove one authenticated provider route with logging |
| MCP | Implemented in Core; production call unverified | Standard owner-authenticated tool interface | Merge hardening and test initialize/tool call in production |
| Zapier/Make/n8n | Optional fallback | Cross-app bridge only where direct routes are insufficient | Enable only a named workflow with evidence and bounded scope |
| Legacy hosting provider | Retired from active KOVA runtime; clearly KOVA-specific projects paused 2026-10-19 | Historical provider evidence only; not a fallback | Delete legacy projects / cancel paid plan after confirming no unrelated workload depends on the Kova OS team |
| Cloudflare | October 19 source baseline records authoritative DNS for kovaos.com; current account/zone access UNKNOWN | Public edge, DNS, Access, static delivery | Verify canonical Cloudflare frontend release and authenticated production acceptance |
| Railway | Coordinator-authenticated read, 2026-10-21: kovaos-app-backend SLEEPING; MySQL OFFLINE. Application/database health is not established | Persistent application backend/services | Verify current app/database health and authenticated acceptance under separately authorized work; do not treat SLEEPING or OFFLINE as healthy |
| Google Cloud backend | Optional | Optional backend/container deployment | Use only if a named workload needs it; do not duplicate Railway by default |

## Provider identity and granted permissions

These are **actual-grant evidence fields**, not desired permissions. No provider's granted OAuth/API scope list was available for this review. Every scope field remains `UNKNOWN`; observed access/staging must not be substituted for a grant list. Do not copy tokens or credential values into this matrix.

| Integration | Stable provider identity / account boundary | Actual granted OAuth/API scopes | Permission evidence status |
|---|---|---|---|
| GitHub | Repositories `github.com/Kathrynhiggs21/Kova-ai-SYSTEM` and `github.com/Kathrynhiggs21/kovaos-site`; authenticated principal ID UNKNOWN | UNKNOWN | INCOMPLETE: Git operations succeeded, but API reads were forbidden; neither reveals the full grant list. |
| `Kova-ai-SYSTEM` | Canonical GitHub repository above; deployed service/account ID UNKNOWN | UNKNOWN | INCOMPLETE: source owner-key enforcement is not evidence of a live principal's grants. |
| `kovaos-site` | Canonical GitHub repository above; Railway app service ID UNKNOWN | UNKNOWN | INCOMPLETE: deployment observation does not establish owner-session permissions. |
| Google Drive | Google account/tenant, OAuth client and canonical folder IDs UNKNOWN in this review | UNKNOWN | INCOMPLETE: historical assistant access does not identify the current grant. |
| Gmail | Google account/tenant and OAuth client IDs UNKNOWN | UNKNOWN | INCOMPLETE: no current scope metadata read. |
| Google Calendar | Google account/tenant and OAuth client IDs UNKNOWN | UNKNOWN | INCOMPLETE: no current scope metadata read. |
| Notion | Workspace, integration and authenticated principal IDs UNKNOWN | UNKNOWN | INCOMPLETE: no current capability/grant metadata read. |
| OpenAI/model providers | Selected provider account/project and principal IDs UNKNOWN | UNKNOWN | INCOMPLETE: designed interface does not establish provider grants. |
| MCP | Core source owns transport; live server identity and authenticated principal ID UNKNOWN | UNKNOWN | INCOMPLETE: implemented owner-key checks do not enumerate live tool authorization. |
| Zapier/Make/n8n | Selected provider/workspace, workflow and principal IDs UNKNOWN | UNKNOWN | INCOMPLETE: optional bridge; no current grant metadata read. |
| Legacy hosting provider | Legacy team/project IDs UNKNOWN; retired from active runtime | UNKNOWN | INCOMPLETE historical inventory; do not reconnect or restore as fallback. |
| Cloudflare | Account ID, zone ID, Worker service identity and principal ID UNKNOWN; `kovaos.com` is a domain label, not an account ID | UNKNOWN | INCOMPLETE: DNS/source observations do not enumerate token permissions or resource scope. |
| Railway | Workspace `1e645067-cebc-47ae-af2e-31b373a4806e`; project `kovaos-runtime` / `350381be-1681-49f2-b91e-a75dbfb8eb8d`; app/MySQL service IDs and authenticated principal ID UNKNOWN | UNKNOWN | INCOMPLETE: coordinator supplied authenticated resource/status read on 2026-10-21; granted scopes were not available. |
| Google Cloud backend | Project, service account and deployed workload IDs UNKNOWN | UNKNOWN | INCOMPLETE: optional workload; no current IAM/grant metadata read. |

The Railway IDs are nonsecret resource identifiers supplied by the coordinator, not credentials. The same read reported the app **SLEEPING** and MySQL **OFFLINE**; it establishes neither end-to-end health nor granted permissions. Older staging observations remain dated history. Complete missing identity and grant evidence only through separately authorized metadata reads; record the evidence date, authenticated principal, resource boundary and actual scope/capability names. Until then, keep these records `INCOMPLETE`.

## Build rule

Every runtime integration records owner/account, purpose, data read, data written, OAuth/API scope, secret location, trigger, failure behavior, privacy boundary, and current verification evidence.

## Priority order

1. Cloudflare + Railway canonical deployment
2. Core-to-app `/api/v1` contract
3. one AI provider
4. Drive metadata registry
5. Calendar and Gmail
6. optional bridges only where a direct connector cannot do the job
