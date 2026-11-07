---
name: phase-up
description: Audit a project against Day 0 or its next phase gate and set up what's missing, in small PRs. Use when the user says "phase up" or "Day 0", starts a project that will have real users, or a phase trigger appears (the first data that can't be regenerated, a second developer, money, users beyond the first group).
---

# Phase up

A project's phase is set by what a mistake costs. This skill moves a project through one **gate** at a time: it audits what the next phase needs, then adds what's missing, smallest risk first.

| Gate | Opens when | Checklist section |
|---|---|---|
| **Day 0** | Before the first real user | Day 0 |
| **v0.0.x → v0.x** | The project holds data that can't be regenerated | v0.x |
| **v0.x → v1** | The owner can no longer be the safety net: a second developer, use while they're away, money, users beyond the first group | v1 |

Day 0 is part of the v0.x gate: a project that skipped it gets those items first.

The phases: **v0.0.x**, a prototype that asks "does anyone want this?"; **v0.x**, a product people rely on, with cheap checks and cheap undo; **v1**, a platform that runs without its owner. A project moves up at an event, never a feeling.

The kinds: an **app** has accounts, saved data or writes; a **content site** is mostly read (marketing, docs, blog); a **toy** is for fun or an experiment. Anything else, such as a CLI, library, native app or browser extension, is **other**.

## 1. Place the project

Read the project's `CLAUDE.md` (its `Phase:` line and stack), the scripts in `package.json`, `.github/workflows/`, the deploy setup and how the app reaches its database.

Done when you can state, with evidence, three things:
- **Kind:** app, content site, toy or other. A toy has no gates; say so and stop. A content site's Day 0 is only the deploy item. For other, apply only D1, D3, D4, P1 and P2, and only where the project has credentials or data.
- **Current phase:** from the `Phase:` line, or judged from real users, real data and CI if there is none.
- **Target gate:** the next one up. Tell the user which gate you're auditing.

## 2. Audit

Read [references/checklist.md](references/checklist.md) and apply every item in the sections up to and including the target gate. Give each item a status:

- **present:** with evidence, a `file:line` or the output of a command you ran.
- **partial:** what exists and what's missing.
- **missing**
- **not needed:** with the reason, such as a project with no database.

Probe instead of trusting names. A script called `dev` may still read a production URL from `.env.local`, so trace where the URL comes from. Guards that refuse production are proven by running them against a fake production URL and seeing them refuse.

Done when every item in scope has a status and evidence.

## 3. Plan

Show the audit as a table, then a plan of PRs in this order:

1. **Protect real data:** credentials off disk, guards and isolation. An agent with a production URL on disk is the largest risk.
2. **Undo:** a known rollback, backups and restore.
3. **Checks:** CI, migration checks, smoke tests.
4. **Docs:** `docs/workflow.md`, the `CLAUDE.md` rules and `Phase:` line.

Each PR has one reason to revert and stays around 400 changed lines, not counting generated files (migration snapshots, lockfiles). Steps only the user can do (dashboards, billing, GitHub settings, secrets) go to the `wizard` skill as a list, not into a PR.

Wait for the user to confirm the plan. Done when they approve it or change it.

## 4. Build

Build one PR at a time, using [references/youngpro.md](references/youngpro.md) for how a working project solved each item. Adapt it to this project's stack, never copy it blind. Prove each PR the cheap way: a guard refusing a fake production URL, the dev command starting in a fresh worktree with no copied files, CI going green.

Ask before creating or changing cloud resources (databases, branches, projects, domains) or anything that touches production. Production data is read-only for this skill.

The last PR sets the `Phase:` line in the project's `CLAUDE.md` and adds any rule an agent must follow from now on. After the Day 0 gate the project is still a prototype: `Phase: v0.0.x, Day 0 done 2026-11-01`. After the v0.x gate: `Phase: v0.x since 2026-11-01`.

Done when every item in scope is present or the user has deferred it by name, and the `Phase:` line is set.
