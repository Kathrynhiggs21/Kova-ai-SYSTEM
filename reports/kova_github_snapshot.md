# KOVA GitHub Snapshot

Captured: 2026-09-29 · Owner: `Kathrynhiggs21`

This is a point-in-time read of every KOVA-related GitHub repository. It records what GitHub showed on the capture date: default branch, latest commit, branch count, CI workflows, open pull requests and open issues.

It does **not** change repository roles. Roles and the active set still come only from [`kova_repos_config.json`](../kova_repos_config.json) and [`docs/architecture/KOVA_REPOSITORY_MAP.md`](../docs/architecture/KOVA_REPOSITORY_MAP.md). Replace this file with a new capture rather than keeping several copies.

## At a glance

| Repository | Registry role | Default branch | Latest commit on default | Branches | Open PRs | Open issues | GitHub Actions workflows |
|---|---|---|---|---|---|---|---|
| [`Kova-ai-SYSTEM`](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM) | Core · **ACTIVE** | `main` | `e249cae` 2026-09-29 — Replace stale setup README with the canonical KOVA operating guide (#136) | 116 | 47 | 18 | `ci.yml` |
| [`kovaos-site`](https://github.com/Kathrynhiggs21/kovaos-site) | Canonical web app · **ACTIVE** | `main` | `0a370df` 2026-09-29 — Secure runtime routes and restore health checks (#22) | 23 | 6 | 2 | `ci.yml` |
| [`kova-ai-dash`](https://github.com/Kathrynhiggs21/kova-ai-dash) | Feature donor · disabled | `main` | `a958353` 2026-09-15 — Clarify KOVA repository role (#6) | 9 | 5 | 1 | none |
| [`kova-ai`](https://github.com/Kathrynhiggs21/kova-ai) | Migration source · disabled | `main` | `a9dba45` 2026-09-15 — Clarify KOVA component role and add CI (#26) | 32 | 15 | 0 | `ci.yml`, `check-gemini-secret.yml`, `kova-auto-update.yml`, `zoo-v8-render.yml` |
| [`kova-ai-mem0`](https://github.com/Kathrynhiggs21/kova-ai-mem0) | Memory adapter · disabled | `main` | `f4016d1` 2026-09-15 — Clarify KOVA memory adapter role and repair CI (#3) | 6 | 2 | 1 | none |
| [`Kova-os-docengine`](https://github.com/Kathrynhiggs21/Kova-os-docengine) | Document component · disabled | `main` | `aac2e7e` 2026-09-15 — Clarify KOVA repository role (#5) | 5 | 1 | 1 | none |
| [`Kova-AI-Scribbles`](https://github.com/Kathrynhiggs21/Kova-AI-Scribbles) | Scribbles placeholder · disabled | `main` | `2cfd66f` 2026-09-15 — Clarify KOVA component role and add CI (#2) | 4 | 0 | 1 | none |
| [`kova-ai-site`](https://github.com/Kathrynhiggs21/kova-ai-site) | Legacy public site · disabled | `main` | `1ac9d4b` 2026-09-01 — docs: correct stale primary-repo architecture | 5 | 2 | 0 | none |
| [`scribbles-by-marcy`](https://github.com/Kathrynhiggs21/scribbles-by-marcy) | World · review | `master` | `b84bf21` 2026-08-01 — Add locked Card Number Plaque System | 12 | 2 | 0 | `zoo-v7-1-render.yml`, `zoo-v7-1-render-google.yml`, `google-cloudrun-source.yml`, `generator-generic-ossf-slsa3-publish.yml` |
| [`Scribblesbymarcy`](https://github.com/Kathrynhiggs21/Scribblesbymarcy) | World · unreviewed duplicate | `main` | `11ee30e` 2026-07-30 — Merge PR #1 (codex-zoo-cards) | 3 | 0 | 0 | none |
| [`Scribbles-Zoo-Project`](https://github.com/Kathrynhiggs21/Scribbles-Zoo-Project) | World · review | `main` | `8f4ec86` 2026-09-16 — Merge PR #4 (copilot/fix-comments-in-review-thread) | 4 | 1 | 1 | none |

Branch counts include the session branch `ccr-f9264153-4zolcl` in each repository. "none" under workflows means no `.github/workflows` directory; some of those repositories use CircleCI or Mergify instead.

Excluded repositories listed in the registry (not captured here): `Kathrynhiggs21/mem0`, `Kovaos-com/vite-react`, `Kathrynhiggs21/platforms-starter-kit`.

## Active repositories

### Kova-ai-SYSTEM

**Open issues (18)**

| # | Title | Last updated |
|---|---|---|
| 133 | Vault live-data enablement gates | 2026-09-27 |
| 131 | Vercel canonical deployment cleanup | 2026-09-26 |
| 130 | Donor migration and archive program | 2026-09-26 |
| 116 | Compare Lovable KOVA OS design donor with kovaos-site and migrate only net-new features | 2026-09-16 |
| 115 | Consolidate KOVA Drive/Notion master records without duplicate storage | 2026-09-15 |
| 114 | Remove hidden Manus runtime dependency from canonical kovaos-site | 2026-09-15 |
| 113 | Implement non-duplicating KOVA status sync across Drive, Notion, GitHub and deployments | 2026-09-15 |
| 112 | Deploy canonical kovaos-site and cut over kovaos.com | 2026-09-15 |
| 110 | Infrastructure: align Vercel projects with canonical KOVA architecture | 2026-09-17 |
| 107 | KOVA GitHub repair tracker — active components | 2026-09-14 |
| 92 | KOVA OS Remediation v1: make repository ownership and runtime architecture canonical | 2026-09-16 |
| 65 | ## Pull Request Overview | 2025-11-04 |
| 60, 56, 51, 48, 44, 36 | ✨ Set up Copilot instructions (six duplicates) | 2025-09-29 → 2025-10-20 |

**Open pull requests (47)** — ready for review first, then drafts.

Ready for review (24):

| # | Title | Branch | Last updated |
|---|---|---|---|
| 129 | Lock canonical KOVA repository lifecycle and cleanup plan | `chore/repo-role-cleanup` | 2026-09-26 |
| 109 | Automate KOVA file lifecycle management | `codex/automate-manual-file-workflows` | 2026-09-26 |
| 104 | Fix flake8 lint errors in export_endpoints.py | `chunk/fix-flake8-export-endpoints` | 2026-09-14 |
| 103 | Fix /ai/command repo allowlist ordering (build-and-test #1142) | `chunk/fix-ai-command-repo-check-order` | 2026-09-14 |
| 98 | Harden MCP JSON-RPC parameter handling | `copilot/f4802fa7…` | 2026-09-26 |
| 84 | Fix Python syntax validation step in CircleCI | `chunk/fix-python-syntax-validation-2` | 2026-08-01 |
| 83 | Fix Validate Python syntax step (build-and-test) | `chunk/fix-python-syntax-validation` | 2026-08-01 |
| 82 | ci: fix Validate Python syntax step using compileall | `chunk/fix-py-syntax-validation` | 2026-08-01 |
| 78 | Fix `.mergify.yml` validation errors | `mergify/fix-config-20260723063919-f1fc2fed` | 2026-09-26 |
| 77 | Fix `.mergify.yml` validation errors | `mergify/fix-config-20260723063912-eb4262ef` | 2026-09-26 |
| 66 | Claude/kova os update 011CUe1P4rsvrKbNfWQ7stA6 | `claude/kova-os-update-…` | 2026-07-31 |
| 57 | Fix Copilot instructions by removing incorrect tool_calling section | `copilot/setup-copilot-instructions-2` | 2025-12-09 |
| 47 | Test Mergify PR | `test-mergify` | 2025-09-29 |
| 43 | Fix Mergify configuration and add GitHub Actions CI for automated PR merging | `copilot/fix-c09e117d…` | 2025-11-06 |
| 42 | Comprehensive Kova AI System Refactor: Production-Ready Infrastructure, Security & Database Operations | `copilot/fix-690f5822…` | 2025-10-16 |
| 22 | Load .env for database session | `codex/add-dotenv-support-for-database_url-h85f86` | 2025-09-12 |
| 20 | Load .env for database session | `codex/add-dotenv-support-for-database_url` | 2025-09-12 |
| 18 | Add root env example and document configuration | `codex/add-.env.example-and-update-documentation` | 2025-09-12 |
| 15 | feat: add repository scan endpoint | `codex/add-api-for-kova-os-access-needs` | 2025-09-12 |
| 11 | Codespace-miniature-zebra-6r5q7gj7w7xhxqg4 | `codespace-miniature-zebra-…` | 2025-09-12 |
| 6 | Complete Kova AI System Implementation with FastAPI, Database Schema, Redis Cache, and One-Shot Deployment | `copilot/fix-2d4be906…` | 2025-09-12 |
| 5 | Extract Kova AI Platform from bundled structure to main folder | `copilot/fix-8a9a9bd2…` | 2025-09-12 |
| 4 | Implement comprehensive download code functionality for Kova AI System | `copilot/fix-f6f12c9d…` | 2025-10-16 |
| 2 | Copilot/fix 6a8ea77e 239f 48a0 acd0 e04a014ed126 | `copilot/fix-6a8ea77e…` | 2025-09-12 |

Drafts (23):

| # | Title | Last updated |
|---|---|---|
| 126 | Align Vercel project governance with canonical KOVA runtime and enforce it in config validation | 2026-09-17 |
| 125 | Document Vercel project alignment with canonical KOVA architecture | 2026-09-17 |
| 124 | Enforce canonical runtime repo boundaries for Vercel cleanup alignment | 2026-09-17 |
| 123 | Audit KOVA Core CI/merge automation and harden runtime config samples | 2026-09-17 |
| 122 | Document CI/PR automation baseline and correct stale Copilot testing guidance | 2026-09-17 |
| 121 | P0 audit remediation: harden API imports and align core setup docs | 2026-09-17 |
| 120 | Remediation v1: canonicalize KOVA ownership map, runtime registry, and frontend boundaries | 2026-09-16 |
| 119 | Define canonical Lovable donor migration matrix and align donor policy metadata | 2026-09-16 |
| 106 | Enforce repository/path validation precedence for AI GitHub routes | 2026-09-14 |
| 105 | Enforce repository-first validation for AI GitHub endpoints | 2026-09-17 |
| 99 | Updating AI endpoints for the application | 2026-09-14 |
| 96 | Install Vercel Web Analytics Integration | 2026-09-01 |
| 80 | Fix Google Drive integration build dependencies, workspace pathing, and OAuth scopes | 2026-07-25 |
| 58 | Add API endpoint to export all Kova repositories | 2025-12-09 |
| 55 | Fix Mergify configuration to use CircleCI legacy status and add review requirements | 2025-10-16 |
| 53 | Fix Mergify configuration to match CircleCI workflow name | 2026-07-23 |
| 52 | Configure Copilot instructions for repository | 2025-10-08 |
| 45 | Enhanced GitHub Copilot instructions with AI agent best practices | 2025-10-08 |
| 37 | Set up comprehensive Copilot instructions for development workflow | 2025-10-16 |
| 35 | Fix Docker build robustness and add environment validation for Kova AI System | 2025-09-29 |
| 28 | [WIP] Approve PR #27 | 2025-09-12 |
| 27 | [WIP] Add complete default Mergify configuration | 2025-12-09 |
| 16 | Add Kubernetes DB secret and reference in API deployment | 2025-09-10 |

### kovaos-site

**Open issues (2)**

| # | Title | Last updated |
|---|---|---|
| 10 | Migrate best dashboard donor features into canonical KOVA app | 2026-09-26 |
| 1 | Separate public KOVA site from private Command Center responsibilities | 2026-09-01 |

**Open pull requests (6)**

| # | Title | State | Last updated |
|---|---|---|---|
| 23 | Fix optional analytics build warnings | Ready | 2026-09-29 |
| 19 | Add fail-closed private Drive index search for Vault | Draft | 2026-09-29 |
| 12 | Install Vercel Web Analytics Integration | Draft | 2026-09-26 |
| 7 | Add canonical KOVA Copilot instructions and repo-specific CI automation audit | Draft | 2026-09-17 |
| 3 | ci: add deterministic validation for kovaos.com app | Ready | 2026-09-26 |
| 2 | CI hardening: verify public KOVA site on every PR | Ready | 2026-09-26 |

## Donor, experimental and legacy repositories

### kova-ai-dash

- Issue #3 — Formalize this repository as the KOVA Command Center (2026-09-01). *Note: superseded by the registry, which makes `kovaos-site` the canonical app.*
- PRs: #8 Clarify KOVA donor/legacy lifecycle (ready, 2026-09-26) · #7 Copilot instructions and CI audit (draft) · #4 CI hardening (ready) · #2 protect private command center data (ready) · #1 Dependabot npm bumps, 9 updates (ready)

### kova-ai

- No open issues.
- PRs (15): #29 Copilot instructions + remove stale Mergify (draft) · #28 Audit P0 (draft) · #27 Align ownership docs (draft) · #25 validate root app in CI (ready) · #23 Remove invalid `kova-ai` submodule gitlink (draft) · #21 Vercel Web Analytics (draft) · #15 card-rendering workflow (ready) · #14 Gemini API integration (draft) · #13 Dependabot js-yaml 3.14.1 → 3.14.2 (ready) · #12 Jest and runtime scripts (ready) · #11 minimal memory schema (ready) · #10 update gitignore (ready) · #9 netlify.toml newline (ready) · #4 docs trailing newline (ready) · #1 assistant memory schema (ready)

### kova-ai-mem0

- Issue #2 — Rebuild as provider-independent KOVA Memory service (2026-09-01)
- PRs: #4 Copilot instructions and CI audit (draft) · #1 Mergify configuration update (ready, 2025-10-14)

### Kova-os-docengine

- Issue #4 — Decide docengine disposition: rebuild with a narrow contract or archive (2026-09-01)
- PRs: #6 Copilot instructions and audit constraints (draft)
- Note: the repository holds a zip bundle `KOVA_OS_DocEngine_Complete_2025-10-23 (2).zip` rather than unpacked source.

### Kova-AI-Scribbles

- Issue #1 — Resolve duplicate Scribbles repository role (2026-09-01)
- No open PRs.

### kova-ai-site

- No open issues.
- PRs: #3 Copilot instructions + disable stale Mergify (draft) · #2 Mergify configuration update (ready, 2025-10-14)
- Latest README states `kovaos.com` redirects to `kova.manus.space`; see Core issue #114 on removing the Manus dependency.

## World repositories

### scribbles-by-marcy

- Default branch is `master` (all other KOVA repositories use `main`).
- No open issues.
- PRs: #6 Zoo V8 image production execution plan (ready, 2026-08-01) · #4 Update Zoo Cards Codex workspace to V7 (draft)

### Scribblesbymarcy

- No open issues or PRs. Same-name duplicate of `scribbles-by-marcy`; registry lifecycle is "unreviewed".

### Scribbles-Zoo-Project

- Issue #1 — Define Zoo / educational-card project without legacy renderer dependency (2026-09-01)
- PRs: #3 Align README boundary wording with KOVA World terminology (draft)

## Totals

| Measure | Count |
|---|---|
| Repositories captured | 11 |
| Open pull requests | 81 |
| Open issues | 26 |
| Remote branches (including session branches) | 219 |

## Observations for the owner

These are read-only observations. Nothing was closed, merged or deleted.

1. **Core PR backlog is large.** `Kova-ai-SYSTEM` has 47 open PRs; 22 were last touched in 2025. Many are superseded by later canonical work (for example the Mergify, Copilot-instructions and early FastAPI PRs). Issue #130 and PR #129 are the natural place to decide which to close.
2. **Duplicate PRs.** #20 and #22 share a title and purpose; #77 and #78 are two Mergify fixes from the same minute; #82, #83 and #84 all fix the same Python-syntax CI step; #105 and #106 overlap; #124, #125 and #126 are three takes on Vercel alignment.
3. **Duplicate issues.** Six open "Set up Copilot instructions" issues (#36, #44, #48, #51, #56, #60) plus #65, whose title is a pasted heading.
4. **Stale branches.** `Kova-ai-SYSTEM` carries 116 branches, including leftover `tmp-mergify/merge-queue/*` and `mergify/merge-queue/*` branches.
5. **Unmerged Dependabot updates** in `kova-ai` (#13) and `kova-ai-dash` (#1).
6. **Copilot-instructions draft PRs** are open in six repositories from the same 2026-09-17 sweep; decide once whether to land or close them all.
