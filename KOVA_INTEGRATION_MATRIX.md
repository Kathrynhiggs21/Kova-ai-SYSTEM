# KOVA Integration Matrix

Verified: 2026-10-09

| System | Role | Current evidence | Status | Next proof |
|---|---|---|---|---|
| GitHub Core | Canonical control-plane source | `Kova-ai-SYSTEM/main` accessible; latest baseline merged | Connected | CI on this continuity PR |
| GitHub Web | Canonical authenticated web source | `kovaos-site/main` includes Cloudflare + Railway migration foundation | Connected | Cloudflare preview built from current main |
| Cloudflare | Public edge/static target | Account connected; `kovaos-web` Worker exists but is placeholder 503 with no assets/bindings/routes | Configured, not runtime verified | Deploy non-production Worker/static preview from canonical web repo |
| Railway | Web application-backend target | Private `kovaos-runtime` project created; `kovaos-app-backend` source/config staged; environment reports zero live services and one pending patch | Staged, not deployed | Explicit deployment approval, then health verification and HTTPS origin |
| KOVA Core runtime | FastAPI control plane | Source is canonical; long-term host still under reconciliation | Needs runtime decision | Verified health + authenticated Core-to-web contract |
| Vercel | Migration/rollback surface | Historical/current deployments exist | Rollback/review | Retain until replacement path passes smoke tests |
| Netlify / GitHub Pages / Manus | Legacy public surfaces | Historical routing evidence exists | Migration debt | Retire only after verified replacement and rollback |
| Google Drive | Canonical user document home | Connected in KOVA environment | Connected, permission state must be checked per task | Current ACL evidence before sensitive workflows |
| AI World | AI-provider/provenance system | Separate Drive root and registry | Separate canonical system | Link by stable ID/URL; never mirror into Core |
| ChatGPT shared handoff URL | Supporting context | Supplied 2026-10-09; page fetch failed | Unverified | Use exported/captured copy if it becomes accessible |
