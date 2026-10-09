# KOVA Decisions

Updated: 2026-10-09

## D-001 — Canonical repository authority
The active repository set is derived only from `kova_repos_config.json` entries where `enabled` is `true`, as required by ADR-003. Do not maintain a second manual active-repository list in continuity files.

Repository roles, donors, experiments, and history must follow that machine-readable registry until an accepted architecture change updates it.

## D-002 — Web hosting target
Approved migration target:
- Cloudflare for public edge/static delivery.
- Railway for the persistent Node/Express backend contained in `kovaos-site`.

Existing Vercel/Netlify/GitHub Pages/Manus paths are rollback or migration surfaces during transition, not sources of truth.

## D-003 — Core remains separate
The FastAPI Core in `Kova-ai-SYSTEM` is a separate control-plane runtime. Do not collapse it into the web app's Railway Node service.

## D-004 — Same-origin public API
The browser should continue using `/api/*`. Cloudflare proxies API requests to Railway so the browser does not need a second public API hostname.

## D-005 — Evidence before “live”
Configured resources, aliases, environment-variable names, placeholder Workers, or successful builds do not prove end-to-end runtime health.

## D-006 — No deprecated Railway config
Do not introduce new `railway.toml` / `railway.json` Config-as-Code. Railway has deprecated that system for new services. Prefer current Railway Infrastructure-as-Code or explicit provider configuration with reviewed state.

## D-007 — Production changes stay owner-gated
Production DNS, domain reassignment, destructive provider retirement, deployment deletion, secret replacement, and live private-data cutover require explicit owner approval.

## D-008 — One home per artifact
GitHub owns source. Drive owns user documents. AI World owns provider/provenance material. Registries and dashboards point to canonical homes instead of making copies.

## D-009 — Durable build continuity
The Continuous Builder state files in this repository are the handoff between build sessions. Chat history is supporting context, not the only build state.
