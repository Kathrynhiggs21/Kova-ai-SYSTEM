# KOVA OS Integration Matrix

## Evidence states

- **Runtime verified** - a current KOVA production read or write/readback succeeded.
- **Assistant access** - the connected assistant can reach the service, but KOVA runtime integration is not proven.
- **Designed** - a specification or adapter boundary exists.
- **Blocked** - access, deployment, security, or an owner decision is required.
- **Disabled** - intentionally excluded from the active runtime.

Configuration alone is never proof of health.

| Integration | Current evidence | KOVA role | Next proof |
|---|---|---|---|
| GitHub | Assistant access; active repo reads/writes verified | Code, PRs, CI, release evidence | Protect and validate both active default branches |
| `Kova-ai-SYSTEM` | Active Core; CI exists | Backend, orchestration, MCP, contracts | Deploy the backend and verify authenticated health/MCP calls |
| `kovaos-site` | Canonical app; CI PR open | Authenticated interface for `kovaos.com` | Merge CI and verify protected production login/routes |
| Google Drive | Assistant access; KOVA runtime unverified | Canonical user files and private registry | Run metadata inventory with readback and no source mutation |
| Gmail | Assistant access; KOVA runtime unverified | Triage and approved drafts/actions | Prove least-privilege read, then approved send flow |
| Google Calendar | Assistant access; KOVA runtime unverified | Agenda, conflicts, reminders | Prove read and approved event creation/readback |
| Notion | Assistant access; KOVA runtime unverified | Human-readable view only | Verify one canonical view without duplicate masters |
| OpenAI/model providers | Designed | AI Assistant behind provider-neutral interface | Prove one authenticated provider route with logging |
| MCP | Implemented in Core; production call unverified | Standard owner-authenticated tool interface | Merge hardening and test initialize/tool call in production |
| Zapier/Make/n8n | Optional fallback | Cross-app bridge only where direct routes are insufficient | Enable only a named workflow with evidence and bounded scope |
| Vercel | Retired from active KOVA runtime; clearly KOVA-specific projects paused 2026-10-19 | Historical provider evidence only; not a fallback | Delete legacy projects / cancel Pro plan after confirming no unrelated workload depends on the Kova OS team |
| Cloudflare | Connected account/zone evidence; authoritative DNS for kovaos.com | Public edge, DNS, Access, static delivery | Verify canonical Cloudflare frontend release and authenticated production acceptance |
| Railway | Current kovaos-app-backend deployment observed healthy/sleeping with no recent failures | Persistent application backend/services | Keep exact-source deployments healthy and connect Cloudflare edge to the verified Railway origin |
| Google Cloud backend | Optional | Optional backend/container deployment | Use only if a named workload needs it; do not duplicate Railway by default |

## Build rule

Every runtime integration records owner/account, purpose, data read, data written, OAuth/API scope, secret location, trigger, failure behavior, privacy boundary, and current verification evidence.

## Priority order

1. Cloudflare + Railway canonical deployment
2. Core-to-app `/api/v1` contract
3. one AI provider
4. Drive metadata registry
5. Calendar and Gmail
6. optional bridges only where a direct connector cannot do the job
