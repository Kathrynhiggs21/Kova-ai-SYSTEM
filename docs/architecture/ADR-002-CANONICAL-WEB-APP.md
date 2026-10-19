# ADR-002: Canonical KOVA Web Application

- Status: Accepted
- Date: 2026-09-15
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
- Vercel cleanup retains clean project names only long enough to verify domains and environment variables; retaining a Vercel project does not promote its source repository to canonical status.

## Hosting migration priority — October 19, 2026

The owner has directed urgent replacement of Vercel across KOVA. The target already recorded by the canonical web repository is **Cloudflare edge/static delivery plus Railway persistent services**. Keep the existing FastAPI control plane and Node/Express web backend behind their current contracts; do not rewrite either into a Worker merely to change hosts.

- Vercel is legacy migration/rollback infrastructure, not the target for new KOVA deployment or service configuration.
- `kovaos.com` and `www.kovaos.com` currently belong to private ChatGPT Sites according to the October 19 registry decision and web PR #38. Keep that entry intact until the replacement is verified. A target architecture is not evidence of cutover.
- Follow the [canonical web deployment guide](https://github.com/Kathrynhiggs21/kovaos-site/blob/main/docs/deployment/cloudflare-railway.md) and reconcile [domain isolation PR #38](https://github.com/Kathrynhiggs21/kovaos-site/pull/38). Never attach wildcard KOVA routes or mix Scribbles identity/routing into KOVA.
- Inventory Vercel project/domain links, Git integrations, checks, environment **names**, callbacks, scheduled jobs, storage and analytics dependencies. Preserve source history and a tested rollback; never publish secret values.
- Stage Cloudflare-to-Railway routing and require real application health JSON, intended-account login, anonymous denial, secure callback/cookies, protected routes, logout and persistence. An Access login page returning HTTP 200 is not backend health.
- After replacement acceptance, disable Vercel automatic Git deployments and mandatory legacy checks, remove active setup instructions and retire projects/billing dependencies through the verified provider workflow. Historical references remain explicitly historical; package-lock mentions alone do not establish a hosting dependency.

Current Core integration and frontend-auth work remain staged: [Core PR #147](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/147) and [web PR #33](https://github.com/Kathrynhiggs21/kovaos-site/pull/33) are draft/unmerged as read October 19. No production cutover, project deletion, credential transfer or billing change is performed by this documentation update.
