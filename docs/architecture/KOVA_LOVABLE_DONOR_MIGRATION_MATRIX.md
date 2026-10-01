# KOVA Lovable Donor Migration Matrix

Status: Active migration plan for issue #116.

## Scope

This matrix governs migration from the Lovable KOVA OS prototype into `Kathrynhiggs21/kovaos-site`.

- The Lovable build is a design/feature donor only.
- `kovaos-site` remains the sole canonical authenticated KOVA application.
- `Kova-ai-SYSTEM` remains Core/backend/orchestration authority.

## Migration Guardrails

1. Preserve existing auth and security hardening in `kovaos-site` and Core APIs.
2. Preserve existing working Drive Manager, AI assistance routes, and dashboard/project capabilities.
3. Migrate reusable UI/design components and interaction patterns only; do not replace working backend/data flows with donor demo implementations.
4. Do not migrate donor demo data into production databases.
5. Do not introduce a second storage system.
6. Do not introduce Manus as a required runtime, auth provider, or model provider.
7. Keep demo/unverified connector states explicitly labeled as unverified.
8. Validate each migration slice with `pnpm check`, tests, and production build in `kovaos-site` before merge.
9. Use preview deployment for each slice before production cutover.

## Feature Matrix

| Feature Area | Existing in `kovaos-site` | Donor Better | Net-New | Do Not Migrate |
|---|---|---|---|---|
| Liquid-glass / pearlescent 3D visual polish | Partial: current dark/orb glassmorphism and 3D orb exist | Yes: adopt only polish deltas that improve clarity/performance/accessibility | Tokens, shader/CSS treatment, and animation presets that are absent today | Donor-only theme engine rewrites, duplicate app shells, any backend coupling |
| Central stateful KOVA orb | Orb visuals already exist | If donor adds richer state semantics, evaluate and port | Stateful orb interaction model only if it can bind to existing app state/events | Parallel orb state store disconnected from canonical app state |
| Themes (Pearl, Midnight, Aurora, Sunset, Ocean, Prism, Minimal, High Contrast) | Existing theme support present but verify exact parity | Yes where donor themes provide clearer contrast/a11y | Missing theme palettes/tokens and switcher UX not already in canonical app | Separate donor config/runtime or duplicated theming frameworks |
| Dyslexia-first controls, focus mode, reduced motion, text/spacing adjustments | Accessibility controls may be partial | Yes if donor implementation is more complete and standards-aligned | New a11y toggles and persisted preferences not already implemented | Cosmetic-only controls without functional behavior |
| Full OS navigation and no-code interaction model | Navigation exists in canonical app | Donor interaction refinements may be useful | Missing navigation affordances, command surfaces, and no-code actions compatible with existing architecture | Donor navigation that bypasses existing auth/data constraints |
| Connections, System Health, Updates, Storage, Automations, Agents, Skills, Advanced views | Several surfaces already exist in canonical stack | Port only UX improvements and truly missing view capabilities | Any missing view module that can sit on current APIs/contracts | Creating a second backend or duplicate data endpoints for these views |
| Plain-language error/status UX | Existing status/error paths exist | Donor copy and UX patterns may improve clarity | New error-state components and status language standards | Hiding errors or representing unverified states as healthy/connected |
| Responsive desktop/tablet/mobile patterns | Responsive patterns already exist | Donor breakpoints/layout polish may be better in places | Net-new responsive components/layout behaviors not currently present | Device-specific forks that duplicate feature logic |

## Migration Sequence (Per Slice)

1. Select one feature area from the matrix.
2. Mark concrete donor deltas as one of: `existing`, `donor better`, `net-new`, `do not migrate`.
3. Implement only `donor better` and `net-new` items in small PR slices.
4. Run in `kovaos-site`: `pnpm check`, test command(s), production build command.
5. Validate in preview deployment before any production cutover.
6. Record evidence links/screenshots in the PR and update this matrix row status.

## Definition of Done

Migration is complete when:

- all rows have explicit `existing`/`donor better`/`net-new`/`do not migrate` decisions with evidence;
- no canonical auth/security regressions are introduced;
- Drive/AI/dashboard capabilities remain functional;
- no second storage/runtime path is introduced;
- preview validation has passed before production promotion.
