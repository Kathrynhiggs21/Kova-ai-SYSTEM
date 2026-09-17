# Infrastructure: Vercel Project Alignment

Status: Owner-executed cleanup checklist · 2026-09-17
Scope: Aligns Vercel projects with the canonical KOVA OS architecture defined in
`docs/architecture/ADR-002-CANONICAL-WEB-APP.md`, `docs/architecture/KOVA_REPOSITORY_MAP.md`,
and `kova_repos_config.json`.

Related issue: Kathrynhiggs21/Kova-ai-SYSTEM#110.

## Canonical runtime targets

The runtime registry currently enables only two repositories:

- `Kathrynhiggs21/Kova-ai-SYSTEM` — canonical orchestration hub / FastAPI backend.
- `Kathrynhiggs21/kovaos-site` — canonical authenticated KOVA OS web application for
  `kovaos.com`.

`kova-ai`, `Kova-os-docengine`, `kova-ai-site`, `kova-ai-mem0`, and other older KOVA
repositories are migration sources, experimental adapters, or legacy/reference components.
They are not canonical Vercel deployment sources unless explicitly promoted in
`kova_repos_config.json`.

Retaining a Vercel project during cleanup does not promote its GitHub source repository
to canonical status. Clean project names are preserved only long enough to verify
domains and environment variables before removal.

## Current Vercel project inventory

| Current project        | GitHub source        | Classification                                                  |
| ---------------------- | -------------------- | --------------------------------------------------------------- |
| `kova-ai-system`       | `Kova-ai-SYSTEM`     | KEEP — canonical backend/orchestration deployment               |
| `kova-ai-system-sl9b`  | `Kova-ai-SYSTEM`     | DUPLICATE — remove only after env/domain verification           |
| `kova-ai`              | `kova-ai`            | LEGACY/MIGRATION — not the canonical frontend                   |
| `v0-kova-ai`           | `kova-ai`            | DUPLICATE LEGACY                                                |
| `kova-ai-z3fs`         | `kova-ai`            | DUPLICATE LEGACY (see NEXT_NO_VERSION note below)               |
| `kova-os-docengine`    | `Kova-os-docengine`  | EXPERIMENTAL / DISABLED — not production KOVA runtime           |
| `kova-os-docengine-kpsl` | `Kova-os-docengine`| DUPLICATE EXPERIMENTAL                                          |

Missing: a Vercel project linked to the canonical `Kathrynhiggs21/kovaos-site` repository.

### `kova-ai-z3fs` failure classification

The failed `kova-ai-z3fs` preview is duplicate-project configuration noise, not a
source-code failure. Vercel reports `NEXT_NO_VERSION` because the duplicate project is
configured as a Next.js app even though the linked `kova-ai` repository is not a Next.js
app. Do not modify repository code to satisfy this deployment. Remove/unlink
`kova-ai-z3fs` with the other duplicate projects after checking for unique environment
variables or aliases.

## Required order of operations

Perform these steps in order in the Vercel console. Do not reorder; several later steps
depend on the canonical frontend being verified first.

1. Create/connect a Vercel project for `Kathrynhiggs21/kovaos-site`.
2. Verify its build, authentication, environment variables, and production routes.
3. Point `kovaos.com` and any intended production aliases at the canonical frontend
   only.
4. Confirm `kova-ai-system` remains the intended backend deployment for
   `Kova-ai-SYSTEM`.
5. For every legacy/duplicate project, compare environment variables, custom domains,
   aliases, and any unique settings against the canonical projects. Record any unique
   configuration before removal so it can be re-created on the canonical project if it
   is still required.
6. Remove the Git integration from redundant legacy copies so they stop producing
   parallel builds while ownership review continues.
7. Delete duplicate/legacy Vercel projects only after owner approval and after
   verifying that no unique configuration or production traffic remains.
8. Verify the following routes on the canonical `kovaos-site` deployment after
   cutover: `/`, `/dashboard`, `/ai`, `/files`, `/settings`, and owner/admin routes.

### Projects targeted for owner-approved removal

After step 5 verification confirms no unique domains, aliases, or environment variables
remain, these projects should be removed via the Vercel console:

- `kova-ai-system-sl9b`
- `v0-kova-ai`
- `kova-ai-z3fs`
- `kova-os-docengine-kpsl`

The connected Vercel API surface does not currently expose project unlink or delete
operations, so these four actions remain owner-only console tasks.

## Storage / sync rule

Do not use Vercel, GitHub, Google Drive, Notion, or Dropbox as mirrored copies of the
same KOVA files. Keep one canonical home per artifact and sync metadata, links, and
status where needed rather than duplicating content. This applies equally to Vercel
projects: one deployment per canonical repository, not one deployment per historical
name.

## Safety boundary

No project deletion, domain reassignment, environment-variable overwrite, or
irreversible unlinking is performed automatically by this repository or its automation.
Every destructive action in the checklist above requires a final owner confirmation in
the Vercel console. Automation in this repository is limited to documenting the
required state; the Vercel console is the execution surface.

## Owner checklist

- [ ] Canonical `kovaos-site` Vercel project created and connected to
      `Kathrynhiggs21/kovaos-site`.
- [ ] `kovaos-site` build, auth, environment variables, and production routes
      verified.
- [ ] `kovaos.com` and production aliases pointed at the canonical `kovaos-site`
      project only.
- [ ] `kova-ai-system` confirmed as the backend deployment for `Kova-ai-SYSTEM`.
- [ ] Environment variables, domains, aliases, and unique settings compared on every
      legacy/duplicate project.
- [ ] Git integration removed from redundant legacy projects.
- [ ] `kova-ai-system-sl9b`, `v0-kova-ai`, `kova-ai-z3fs`, and
      `kova-os-docengine-kpsl` deleted after owner approval and verification.
- [ ] Post-cutover verification of `/`, `/dashboard`, `/ai`, `/files`, `/settings`,
      and owner/admin routes on the canonical frontend.
