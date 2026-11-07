# YoungPro, the benchmark

YoungPro (`riolly/youngpro-platform`, private) went from prototype to v0.x between 24 Oct and 2 Nov 2026. It uses TanStack Start, Drizzle, Neon, Better Auth, bun and Vercel, so on that stack its files are close to drop-in. On another stack, take the decisions and leave the code.

Read a file at the pinned commit, which never changes:

```bash
gh api "repos/riolly/youngpro-platform/contents/<path>?ref=44927c89a03ce6e7459b156b0563061e0602249a" -H "Accept: application/vnd.github.raw"
```

Item numbers match [checklist.md](checklist.md).

| Item | Files | Decisions worth keeping |
|---|---|---|
| D1 | `package.json` (`db:prod:migrate`) | The production URL comes from `neon connection-string main` inside the one command that needs it. The T3 worktree hook copies every ignored `.env*` file into new worktrees, so no `.env*` file may ever hold production. |
| D2 | `scripts/dev.ts`, `scripts/lib.ts` | PGlite in `./.pglite`, one per worktree. Each Vite port is paired with a database port, so worktrees run side by side. `.env.local` is rewritten on every start. Mock data is seeded once, while data that goes stale (today's meeting, kiosk code) refreshes on every start. Corrupt data moves to `.pglite.broken` and rebuilds; any other failure leaves the data alone. `dev:fresh` deletes the database. |
| D3 | `drizzle.config.ts`, `src/server/test-database.ts`, `scripts/mock-seed.ts`, `scripts/dev-seed.ts`, `scripts/share.ts` | Two allow-lists, not one: `isTestDatabase` (local and staging: test logins and mock data) and `isSafeToMigrate` (those plus `prerelease`, which holds real data). Neon endpoints are hard-coded, so a recreated branch is refused until the file is updated. `ALLOW_PROD_DB` is the only override, and only `db:prod:migrate` sets it. |
| D4 | `CLAUDE.md` | Its rules each name a silent breakage: server-only imports leaking into the client, kiosk writes on fixed URLs so queued requests replay after a redeploy, idempotent writes with device-made ids, middleware on every server function. Plus the product principle ("avoid extra work for leaders"). |
| D5 | `docs/workflow.md` ("To undo a release") | Rollback is "promote the previous deployment in Vercel", and the note says the schema stays where it is. |
| D6 | `scripts/e2e.ts`, `scripts/kiosk-e2e.ts`, `scripts/join-e2e.ts`, `scripts/leader-e2e.ts` | System Chrome, one script per flow. It reuses a running stack or starts one and stops it afterwards. Screenshots go to `/tmp/yp-e2e*`. The suite runs in CI only, after the laptop hard-powered-off three times under load. |
| P1 | `.github/workflows/ci.yml` | `checks` and `e2e` are separate jobs. The checks job fetches `origin/main` because `db:check` compares against it. Screenshots upload only when e2e fails. |
| P2 | `scripts/check-migrations.ts`, `scripts/migrations.ts`, `scripts/migrations.test.ts`, `scripts/db-status.ts` | `db:check` compares the branch's Drizzle journal with `main`'s and fails on a migration that would be skipped. It prints a `::warning::` in CI when a PR adds a migration. `db:status` is read-only and covers every Neon branch. |
| P3 | `package.json` (`db:staging:migrate`, `seed:mock:staging`, `dev:staging`) | One Neon `staging` branch shared by every preview. Previews don't migrate themselves, so a branch with a migration runs `db:staging:migrate` first, and staging can be ahead of production. |
| P4 | `scripts/prerelease-check.ts` | Resets Neon `prerelease` from production, applies the branch's migrations and force-pushes to a `prerelease` Git branch that Vercel deploys. It was first called `release`, which read like production, so it was renamed. |
| P5 | `package.json` (`db:prod:migrate`), `docs/workflow.md` step 6 | The human migrates production before merging. Migrations stay additive, because the old code runs on the new schema between those two steps. |
| P6 | `docs/workflow.md` | Environments table, seven steps that each end in "Done when", migration rules, a production-safety table and troubleshooting. |
| P7, P8 | None | Still missing at the pinned commit: no error alerts, no restore drill. |

## Using it as an eval

To test this skill, audit YoungPro at two commits and compare with the expected statuses:

- **Before** `ab76c45b1749a462444ef1e23c1f5e2d141913b2` (after PR #9, before the workflow PRs #11 and #12). Expected: D1 missing (the `dev` script reads `.env.local`, a production copy), D2 partial (`db:local` and `dev:local` are two commands and the env file isn't rewritten), D3 partial (no guard in `drizzle.config.ts`), D4 present, D5 partial (rollback not written down), D6 present, P3 present, and every other P item missing.
- **After** `44927c89a03ce6e7459b156b0563061e0602249a`. Expected: D1 to D6 and P1 to P6 present, P7 and P8 missing, and P9 missing (the `CLAUDE.md` has no `Phase:` line).

A good run gets every status right, finds P7 and P8 as the remaining gaps, and puts D1 first in the "before" plan.
