# Core handoff

Reviewed 2026-10-21. The continuity work on that date used existing PR [#145](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/145), branch `chore/continuous-builder-oct9`. This is dated provenance, not a permanent continuation-branch instruction. Read [AGENTS.md](../AGENTS.md), [build state](../KOVA_BUILD_STATE.md), [backlog](../KOVA_BACKLOG.md), [repository map](architecture/KOVA_REPOSITORY_MAP.md), [module boundaries](architecture/ADR-003-MODULAR-CORE-BOUNDARIES.md) and [run log](../KOVA_RUN_LOG.md). These own the details; this file is navigation and audit evidence.

## Before selecting a continuation branch

1. Preserve local changes and inspect the current checkout (`git status --short`, `git branch --show-current`, `git log -1`). Stay in the existing environment; do not create a worktree or reset local work to replay this handoff.
2. Read the remote's **current default branch** with `git ls-remote --symref origin HEAD`, then fetch that branch and record its current full commit SHA. Do not assume the default branch is still `main` or that an old SHA remains current.
3. Read the candidate PR's **current open/closed/merged state, base branch, head repository/branch and full head SHA**, plus current checks. Use the GitHub API when available, or readable current PR/checks pages together with Git refs. A surviving branch/ref alone does not establish an open PR. If status cannot be read, report the missing evidence before selecting a continuation branch.
4. Select an existing authorized PR branch only if the PR is still open, its current base matches the intended default branch, and its head still owns the unfinished scope. Check for intervening commits before updating it; preserve others' changes and never force-push to recover a historical head. If the PR was merged, start the next task from the current default-branch state and locate the current authorized work; if closed unmerged, inspect its disposition/superseding PR. Do not automatically reuse #145 or `chore/continuous-builder-oct9` in either case.

For this dated follow-up only, remote discovery returned default `main` at `c7188318a6e2b17b28dfc5311d365f2d0ed6e0de`; the current PR page showed #145 **Open**, targeting `main`, with the same-repository head `chore/continuous-builder-oct9` at `bbc5f4fd83692dd111fd583e1000204e69546986` before this correction. The coordinator reported hosted container-smoke, verify-platform, CodeQL and CircleCI success on that exact head. Recheck all of this at the next continuation; it does not select a branch for future sessions.

## PR audit against main

Main: [`c718831`](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/commit/c7188318a6e2b17b28dfc5311d365f2d0ed6e0de). Heads below were fetched before this pass's changes. Behind counts describe those original heads, not the updated #145 branch.

| PR / original head | Main commits missing | Visible CI and disposition |
|---|---:|---|
| [#145](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/145) / `d2064bc` | 16 | [verify-platform passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/37895249595). Best continuity home; update with main and factual hosting guidance. |
| [#146](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/146) / `7eadbc0` | 16 | [verify-platform passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/37894445159). Overlapping two-file continuity draft; unique auth, CORE audit, temporal-memory and connector tasks are retained in the consolidated backlog. Recommend superseding after #145 review. |
| [#147](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/147) / `95137fe` | 2 | [verify-platform passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/38787132989). Distinct CORE adapter/tests and [dated runtime gate](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/blob/95137fef723ead918f3a1c0ab9db8458b7100cc0/docs/operations/KOVA_RUNTIME_GATE_2026-10-10.md); retain separately. |
| [#148](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/148) / `dbe7f41` | 2 | [verify-platform passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/38973596695). Distinct synthetic Temporal pilot; existing CI does not exercise its package. Retain pending integration checks. |
| [#151](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/151) / `248baf0` | 2 | [verify-platform passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/39301658348). Hosting intent overlaps main/#145; do not import stale private-Sites ownership or Vercel-rollback claims. Unique references preserved below; recommend superseding after review. |
| [#153](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/pull/153) / `7309275` | 0 | [verify-platform and container-smoke passed](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/actions/runs/39688989796). Distinct proposed architecture/schemas; resolve ADR-004 numbering and evidence-state vocabulary before adoption. |

All six original heads' checks pages showed successful CodeQL jobs and CircleCI checks; Mergify protection/queue checks were neutral. PR conversation pages also showed legacy Vercel deployment errors. Those do not establish a failing Core build or justify reviving Vercel. The older five heads did not show the newer `container-smoke` job; old green CI is not proof of compatibility with current main.

GitHub API reads return `Forbidden`; audit evidence comes from Git refs and public PR/checks HTML. Check updated-head CI again after push. No PR closure, merge or production write is authorized by this handoff.

## Preserved source links

- [Original #145 provider metadata and migration record](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/blob/d2064bce72f6a61a8afc2c0d85e65f3d9cd3ee22/docs/command-center/KOVA_OS_INTEGRATION_MATRIX.md): dated evidence, superseded where current main disagrees.
- [Canonical web deployment guide](https://github.com/Kathrynhiggs21/kovaos-site/blob/main/docs/deployment/cloudflare-railway.md), [web #28 PORT gate](https://github.com/Kathrynhiggs21/kovaos-site/pull/28), [web #33 auth work](https://github.com/Kathrynhiggs21/kovaos-site/pull/33), and [web #38 domain isolation](https://github.com/Kathrynhiggs21/kovaos-site/pull/38). Retained as review sources; their current PR/production states were not verified here.
- [#151 source proposal](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/commit/248baf03a771270022685d1106117da8b12133fd), [#146 continuity source](https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/commit/7eadbc0fc4ab06a3a52978d789c3668b2b7d9427). Preserve provenance without treating historical hosting claims as live facts.
