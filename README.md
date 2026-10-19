# KOVA OS — Orchestration Hub

Canonical architecture, control plane, repository registry, deployment references, and validation tooling for KOVA OS.

This repository coordinates one KOVA system. It is not a second document library, a mirror of the frontend, or proof that every catalogued integration is live.

## Start here

1. Read [`AGENTS.md`](AGENTS.md) before changing code or configuration.
2. Use [`docs/architecture/KOVA_REPOSITORY_MAP.md`](docs/architecture/KOVA_REPOSITORY_MAP.md) for canonical repository roles.
3. Use [`kova_repos_config.json`](kova_repos_config.json) for machine-readable repository status and boundaries.
4. Use [`docs/command-center/KOVA_OS_FINAL_GUIDE.md`](docs/command-center/KOVA_OS_FINAL_GUIDE.md) for the product vision and phased roadmap.

Historical guides and generated exports may still exist in the repository. Verify current code, configuration, and runtime evidence before treating an older document as authoritative.

## Canonical runtime repositories

| Repository                                                                          | Role                                        | Boundary                                                            |
| ----------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------- |
| [`Kathrynhiggs21/Kova-ai-SYSTEM`](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM) | Orchestration hub and backend/control plane | Architecture, MCP, validation, shared services, repository registry |
| [`Kathrynhiggs21/kovaos-site`](https://github.com/Kathrynhiggs21/kovaos-site)       | Canonical KOVA web app for `kovaos.com`     | Frontend routes, accessibility, owner workflows, web deployment     |

Other KOVA repositories are migration sources, experiments, provider adapters, optional worlds, or archived references unless the canonical registry explicitly promotes them. Do not create a new repository to bypass unfinished work in either active runtime repository.

## System boundaries

- **GitHub** stores source code and review history.
- **Google Drive** is the canonical home for KOVA user documents. The KOVA root contains one `KOVA Core` folder.
- **KOVA AI World** is separate from KOVA Core and contains provider/agent material, provenance, and promotion workflows. Link by stable ID or URL; do not mirror its contents.
- **Hosting target:** Cloudflare edge/static delivery plus Railway persistent services. Vercel is legacy migration/rollback infrastructure; current production routing must be verified separately.
- **The frontend** never becomes an orchestration or document source of truth.

One artifact gets one canonical home. Indexes and dashboards should point to that home instead of copying it.

## Evidence-based status

Use these labels consistently:

| Label              | Meaning                                                                            |
| ------------------ | ---------------------------------------------------------------------------------- |
| `Configured`       | A setting or adapter exists; runtime has not been proven                           |
| `Connected`        | Authentication and a current end-to-end read through the intended source succeeded |
| `Runtime verified` | The intended production path passed a current check                                |
| `Needs connection` | Required authorization or configuration is missing                                 |
| `Broken`           | A current check failed with recorded evidence                                      |
| `Unknown`          | No current evidence exists                                                         |

Never infer a live connection from a document, environment-variable name, mock response, or provider logo.

## Security defaults

- Never commit credentials, tokens, recovery codes, private keys, private records, or production secrets.
- Keep real values in the approved deployment/provider secret store. Commit only safe templates.
- Fail closed when authentication, owner approval, runtime evidence, or a required scope is missing.
- Use least privilege and the minimum context needed for every agent, connector, and workflow.
- Keep destructive or production-critical changes reversible. DNS, domain ownership, authentication ownership, deployment deletion, and live private-data cutover require explicit owner approval.
- Static Git-tracked evidence cannot authorize live family data. The Vault remains in sample mode until independent server-side authorization and runtime gates exist.

## Local validation

Python 3.11 and Node.js 22 match CI. Install dependencies in an isolated environment, then run the same gates used by GitHub:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r kova-ai/requirements.txt

./verify_platform.sh
python3 scripts/validate_config.py
PYTHONPATH=kova-ai python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m compileall -q kova-ai/app
node --check site/app.js
node --test tests/test_site_exports.js
```

Do not put real secrets in command history or test fixtures. If a credentialed integration cannot be exercised safely, report it as unverified rather than substituting a mock success.

## Development workflow

1. Inspect the existing implementation and canonical docs.
2. Work on a branch and open a focused pull request.
3. Update behavior, tests, documentation, and registry records together.
4. Run relevant local checks and require CI before merge.
5. Record what was actually verified and what remains external or owner-only.

The owner should not need to write or debug code for ordinary maintenance. User-facing KOVA workflows should remain no-code, dyslexia-first, and plain-language.

## Historical production baseline — October 6, 2026

As re-audited on October 6, 2026:

- the core `main` branch includes the fail-closed Vault live-cutover controls;
- the canonical frontend repository is `kovaos-site`; Vercel currently has both `kova-app` and `kovaos-site` projects deploying the same current `main` commit (`593452d`), while root/www Vercel aliases are attached to `kovaos-site`;
- public routing is not cut over to that Vercel build: October 6 probes resolved `kovaos.com` through Cloudflare to GitHub Pages headers and the legacy `kova-ai-site` redirect to `kova.manus.space`, so Vercel alias metadata is not runtime proof;
- backend Vercel ownership is still under reconciliation: `kova-ai-system`, `kova-ai-system-sl9b`, and `kova-ai-system-okaz` all deploy the canonical Core repository;
- repeatable October 6 probes of deployments `dpl_AeGoU5MNzDoUkcQ8b3DBySXbYdJB` (`kova-ai-system`), `dpl_7pR5HEXnmMMaSuK1nHEHd7cCTDyP` (`kova-ai-system-sl9b`), and `dpl_6gQwD7nW54BJ9zdHHr6EBGQn6BJF` (`kova-ai-system-okaz`) found `/health` returning HTTP 200 only on the FastAPI-configured `okaz` project; the other two returned 404 on both `/health` and `/api/health`;
- the redacted env-name audit found `kova-ai-system` carrying development/preview-scoped configuration including `APP_NAME`, `DEBUG`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `GITHUB_WEBHOOK_SECRET`, `SECRET_KEY`, `JWT_ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`, while `kova-ai-system-okaz` returned no Vercel environment variables; no secret values were read into documentation;
- no backend project should be retired or promoted solely from build status until runtime configuration and the authenticated Core-to-web contract are reconciled;
- anonymous Google Drive editing has been removed from the KOVA and AI World roots; and
- duplicate/legacy Vercel projects and Manus-derived frontend runtime paths still require controlled review before retirement or replacement.

This is a dated baseline, not a permanent health guarantee. Re-run checks before reporting current status.

## Key references

- [`docs/architecture/KOVA_REPOSITORY_MAP.md`](docs/architecture/KOVA_REPOSITORY_MAP.md) — repository ownership and runtime boundary
- [`docs/architecture/PERSONAL_FAMILY_RECORDS_VAULT.md`](docs/architecture/PERSONAL_FAMILY_RECORDS_VAULT.md) — Vault security and cutover boundary
- [`CONNECTOR_TRAY.md`](CONNECTOR_TRAY.md) — connector design and status model
- [`SETUP_GUIDE.md`](SETUP_GUIDE.md) — historical setup reference only; use the validation section above for current checks
- [`archive/`](archive/) — historical material, not current operating instructions

When documents disagree, current code plus the repository map, machine-readable registry, tests, and runtime evidence take precedence.

## Metadata file lifecycle

`scripts/file_organizer.py` indexes source identities, versions, readable titles, lifecycle labels, sensitivity, and duplicate evidence without moving, renaming, deleting, or copying originals. Private registry and exception reports are stored outside this repository with user-only filesystem permissions.

Use `config/automation_policy.v1.json` and [KOVA_FILE_ORGANIZATION.md](KOVA_FILE_ORGANIZATION.md) for the current policy and commands. The implementation can process an explicit metadata inventory; it does not itself connect every provider or scan inaccessible accounts. Live provider scheduling and private-data cutover still require separately verified authorization.

## Hosting migration priority — October 19, 2026

The owner has directed urgent replacement of Vercel across KOVA. The target already recorded by the canonical web repository is **Cloudflare edge/static delivery plus Railway persistent services**. Keep the existing FastAPI control plane and Node/Express web backend behind their current contracts; do not rewrite either into a Worker merely to change hosts.

- Vercel is legacy migration/rollback infrastructure, not the target for new KOVA deployment or service configuration.
- `kovaos.com` and `www.kovaos.com` currently belong to private ChatGPT Sites according to the October 19 registry decision and web PR #38. Keep that entry intact until the replacement is verified. A target architecture is not evidence of cutover.
- Follow the [canonical web deployment guide](https://github.com/Kathrynhiggs21/kovaos-site/blob/main/docs/deployment/cloudflare-railway.md) and reconcile [domain isolation PR #38](https://github.com/Kathrynhiggs21/kovaos-site/pull/38). Never attach wildcard KOVA routes or mix Scribbles identity/routing into KOVA.
- Inventory Vercel project/domain links, Git integrations, checks, environment **names**, callbacks, scheduled jobs, storage and analytics dependencies. Preserve source history and a tested rollback; never publish secret values.
- Stage Cloudflare-to-Railway routing and require real application health JSON, intended-account login, anonymous denial, secure callback/cookies, protected routes, logout and persistence. An Access login page returning HTTP 200 is not backend health.
- After replacement acceptance, disable Vercel automatic Git deployments and mandatory legacy checks, remove active setup instructions and retire projects/billing dependencies through the verified provider workflow. Historical references remain explicitly historical; package-lock mentions alone do not establish a hosting dependency.

Current Core integration and frontend-auth work remain staged: [Core PR #147](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/147) and [web PR #33](https://github.com/Kathrynhiggs21/kovaos-site/pull/33) are draft/unmerged as read October 19. No production cutover, project deletion, credential transfer or billing change is performed by this documentation update.
