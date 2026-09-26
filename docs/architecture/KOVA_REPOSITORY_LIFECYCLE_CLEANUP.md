# KOVA Repository Lifecycle Cleanup

Status: approved cleanup plan · 2026-09-26

## Canonical runtime

Only these repositories are active KOVA runtime sources:

1. `Kathrynhiggs21/Kova-ai-SYSTEM` — Core/control plane, orchestration, MCP, contracts, Agent Ledger and system services.
2. `Kathrynhiggs21/kovaos-site` — authenticated KOVA application for `kovaos.com`, including dashboard and modules.

## Disabled donors / historical sources

These repositories must not deploy or present themselves as canonical KOVA runtime:

- `kova-ai-dash` — feature donor only; migrate useful UI/auth patterns into `kovaos-site`, then archive.
- `kova-ai` — mixed historical assistant/application migration source; migrate useful code, then archive.
- `kova-ai-site` — legacy public site/redirect/docs source; migrate unique material, then archive.
- `kova-ai-mem0` — experimental memory adapter; disabled unless a future ADR promotes it.
- `mem0` — excluded generic/private placeholder; archive.
- `Kova-os-docengine` — experimental document engine; disabled unless a future ADR promotes it.
- `Kova-AI-Scribbles` — optional integration placeholder; not KOVA runtime.

Independent Scribbles/Zoo products remain outside the KOVA runtime.

## Naming direction

Do not create more `kova-ai-*` runtime repositories.

The current canonical names remain authoritative until an atomic rename/migration is approved. A future human-readable rename may map:

- `Kova-ai-SYSTEM` -> `kova-core`
- `kovaos-site` -> `kova-app`

Do not perform those renames piecemeal. Repository URLs, CI, Vercel, domain mappings, agents, docs and automation must move together.

## Ruleset cleanup

Core currently has an active ruleset misleadingly named `Mergify` whose rule is Copilot review, not Mergify queue policy. Repository-side Mergify behavior is now defined by `.mergify.yml`.

Owner/admin GitHub settings cleanup:
- rename or remove the misleading `Mergify` ruleset;
- retain one intentional protection policy for `main`;
- avoid duplicate Copilot review requirements;
- scope production protection to `main` unless another branch genuinely needs it;
- if Mergify queue is enabled, add the Mergify integration as the appropriate bypass actor required for queue mechanics;
- require canonical CI/security checks, not obsolete duplicate deployment checks.

The connected GitHub API can read but not mutate repository rulesets, so these settings remain an explicit admin action until a supported administrative connection is available.

## Mergify rollout

`.mergify.yml` is present in both canonical repositories. Validate one low-risk queue run before enabling automatic queueing broadly.

## Deployment cleanup

Only canonical runtime repositories should own production KOVA deployments. Suffixed/duplicate Vercel projects and legacy repository deployments are cleanup targets and must not become sources of truth.

## Archive gate

Before archiving a donor repository:
1. identify unique useful code/assets;
2. migrate through reviewed PRs;
3. verify canonical CI;
4. update references;
5. disable deployment/automation;
6. archive the donor.

Never delete historical repositories merely to make the list look cleaner.
