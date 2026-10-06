# ADR-002: Canonical KOVA Web Application

- Status: Accepted
- Date: 2026-09-15
- Amended: 2026-10-06
- Domain: `https://kovaos.com`

## Decision

KOVA OS has two active platform repositories:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` owns architecture, the control plane, connector contracts, automation policy, shared schemas, deployment coordination, and audits.
2. `Kathrynhiggs21/kovaos-site` owns the authenticated browser/PWA experience at `kovaos.com`.

`kova-ai-dash` is a feature donor. Its unique dashboard, integration, command, and provenance features must move through reviewed pull requests into `kovaos-site`; it is disabled in the runtime registry and will be archived only after migration verification.

The proposed names `kova-core-system`, `kovaos-pwa`, `kova-memory-mem0`, and `kova-legacy-archive` are logical target labels, not authorization to create duplicate repositories or combine Git histories destructively. Existing repositories keep their names until redirects, deployment links, package imports, and history preservation are verified.

Scribbles, Reagan learning, and TAC for Hope are independent product/World boundaries. They may integrate with KOVA through contracts, but they are not folders inside the KOVA Core repository.

## Source evidence

- [Approved KOVA final architecture](https://drive.google.com/file/d/19B30gtiOE9F9IzYaKixQNrz3wUu6IROq/view)
- [KOVA target-state registry](https://drive.google.com/file/d/1vDdBFTgVxj1djLsSKI6Id5zGZpduq3mM/view)
- [KOVA remediation roadmap](https://drive.google.com/file/d/17NmHIlWPDeHnFQDg-27GQA4eWmH2_W63/view)
- [KOVA architecture package folder](https://drive.google.com/drive/folders/180rt6J7TuEtsErBvG_rt8ZPnEAICpako)
- [Structured KOVA/AI Drive](https://drive.google.com/drive/folders/1ASnxBdkrBtEhw7s5OlM27JF6dTuQ5WWl)

The general personal Drive folder is not a KOVA source of truth. The mixed KOVA working folder contains useful artifacts but also duplicates and converted copies; it is an intake/reference source, not executable truth.

## Consequences

- Runtime registry enables only Core and `kovaos-site`.
- Feature donors, experiments, and archives cannot be deployed by registry automation.
- GitHub owns executable truth; Drive owns user files and archival evidence.
- New KOVA repositories require a distinct deployable boundary and an update to this ADR and the runtime registry.
- Cloudflare is the target public edge, TLS termination, static web delivery, and request-routing layer for `kovaos.com`.
- The web application's persistent Node/Express/tRPC backend may run on Railway behind Cloudflare after the Railway account/service is connected and the preview smoke-test gate passes.
- KOVA Core is a separate Python/FastAPI control-plane service. It must not be silently routed to the web Node backend. The October 6 audit found `/health = 200` only on the FastAPI-configured `kova-ai-system-okaz` Vercel project, but that project had no Vercel environment-variable inventory, so it is evidence of a viable runtime shape rather than authorization to promote it.
- Until a dedicated Core destination is connected, configured, and proven with an authenticated Core-to-web contract, existing Core deployments remain in place and none may be retired solely because the Cloudflare web migration is ready.
- Vercel, GitHub Pages, Netlify, and Manus-hosted KOVA surfaces are migration/rollback surfaces only until the replacement path is independently verified; retaining a provider deployment does not promote its source repository to canonical status.
