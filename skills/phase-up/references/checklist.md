# Phase checklist

Items are stack-agnostic. Each has a **check** (how to prove it) and the **cost** of skipping it, mostly taken from what happened on YoungPro. How YoungPro built each item is in [youngpro.md](youngpro.md), under the same number.

## Day 0

Before the first real user. A content site needs only D5.

**D1. Production credentials never on disk.** Production is reached through one deliberate command that fetches credentials when it runs (for example from the database provider's CLI), never from an `.env*` file.
- Check: `git ls-files | rg '\.env'` lists only an example file. No `.env*` file in the main checkout or any worktree holds a production host: compare their database hosts with production's, without printing secrets. A dev command that rewrites the env file fixes only the checkouts where it ran. Any hook that copies ignored files into new worktrees is accounted for.
- Cost: a production `.env.local` left in the main checkout gets copied into new worktrees, where a plain `dev` or migrate reaches real data.

**D2. One command, one isolated local stack.** In a fresh worktree, one command installs dependencies and starts the app with its own database, migrations, mock data and test accounts, and writes its env file with local values every time.
- Check: run it in a fresh worktree with nothing copied in. It ends with a URL you can sign in to.
- Cost: without it, each new worktree borrows someone else's database, which is how D1 breaks.

**D3. Guards on writes.** Every script that migrates, seeds or turns on test logins checks the target database against an allow-list of local and test hosts, and refuses anything else. One explicit override exists for production, and only the production command sets it.
- Check: point each one at a fake production URL and watch it refuse.
- Cost: a seed script that "resets all data" is one wrong env var away from wiping production.

**D4. A project CLAUDE.md that earns its load.** Commands, the product principle, and the rules that are expensive to break (id generation, idempotent writes, auth on every server entry point). The `Phase:` line is P9.
- Check: each rule names something an agent could break without noticing. Lookups the repo already answers (scripts, directory layout) stay out.

**D5. Preview, deploy, roll back.** Every push gets a preview deploy, a merge deploys production, and the rollback is written down (on Vercel: promote the previous deployment). The rollback note says that it rolls back code, not the schema.
- Check: the latest push has a preview URL, and the rollback steps are in the repo.

**D6. One smoke test per core flow.** A script that drives a real browser through each flow users depend on. It is how the agent checks its own work, not a regression suite.
- Check: it runs with one command against the local stack.

## v0.x

The project holds data that can't be regenerated. Everything in Day 0, plus:

**P1. CI on every PR.** Typecheck, lint, unit tests, the migration check (P2), the build and the smoke tests. e2e runs in CI, not on the laptop.
- Check: the latest PR shows the checks, and they're green.

**P2. Migrations can't go wrong silently.** Migrations are additive: removing or renaming a column takes two releases. A check fails a branch whose migration the tool would skip. Drizzle, for example, skips a migration generated before one that reached `main` first. A read-only status command shows what's pending in each database.
- Check: generate a migration on a branch older than the newest one on `main`, and watch the check fail.
- Cost: a skipped migration gives no error. The app breaks on the first query against the missing column.

**P3. A shared preview database apart from production.** Previews use a staging database with mock data and test accounts, never production.
- Check: a preview's database host is the staging one.

**P4. Rehearsal on a copy of production.** For changes with a migration or that change how existing data is read: one command resets a copy of production, applies the branch's migrations and deploys the branch against it. It stays private: real data, no test accounts.
- Check: the command prints a URL that works with real data.

**P5. Production migrations by one deliberate command, before the merge.** CI warns on PRs that add a migration. The human runs the production migration, then merges.
- Check: the PR template, CI warning or workflow doc says so, and `db:status` shows nothing pending after a release.

**P6. The workflow is written down.** `docs/workflow.md` has an environments table and the steps of a change, each ending in "Done when". The production guards are listed in one table.
- Check: a fresh agent can ship a change by following it, with no other context.

**P7. Errors reach the owner.** Production errors arrive as an alert (email, push, chat) without anyone opening a dashboard. A weekly summary is not an alert.
- Check: throw a test error in production or a preview, and the alert arrives.
- Cost: YoungPro reached v0.x without this. Leaders report errors before the owner sees them.

**P8. Backups and restore are known.** The restore window is known (for example the provider's point-in-time restore), and one restore has been tried into a branch.
- Check: the workflow doc says how to restore, and the drill's date is recorded.

**P9. Phase line.** `CLAUDE.md` says `Phase: v0.x since <date>`.

## v1

The owner can no longer be the safety net. Everything above, plus only what the trigger calls for. Scale is a separate question: add load testing only when usage calls for it.

**R1. Required checks on `main`.** A red check blocks the merge, so an agent that merges on green (tstack's `full-send`) means something. Private repos need GitHub Pro or Team for this.

**R2. Migrations in the deploy pipeline.** Expand, then contract, so each release runs on both the old and the new schema.

**R3. Alerts with a runbook.** For each alert: what it means, what to check, how to roll back, who decides.

**R4. Security in the loop.** `/security-review` on every auth, role or payment change. Dependency updates arrive as grouped weekly PRs (Renovate or Dependabot).

**R5. Gradual rollout.** Risky changes ship behind a feature flag or a rolling release.

**R6. Ownership written down.** Who owns each account (hosting, database, domain, Google Cloud), where the secrets live (a password manager vault), and the restore drill on a schedule.
