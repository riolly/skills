---
name: prune
description: Cut a codebase down by deleting or shortening unused code, dependencies, tests, comments, and stale or conflicting docs and agent context, in small PRs. Use when the user says "prune" or asks to remove dead code or reduce lines of code.
---

# Prune

Pruning makes a codebase smaller without changing what it does. The measure is net lines removed while every check stays green. A **cut** is one finding that is deleted or rewritten shorter. **Sediment** is anything still in the repo that no longer bears on what the code does: dead code, unused dependencies, comments that repeat the code, docs and agent context that went stale or contradict each other, and tests that check nothing.

If the user named a directory or a kind of cut, prune only that.

## 1. Baseline

Find the project's checks (typecheck, lint, tests, build) from its `CLAUDE.md`, `package.json` scripts or CI workflow, and run them. Count lines with `scc` or `tokei` if installed, otherwise `git ls-files -z | xargs -0 wc -l`. Leave lockfiles, generated files, migrations and vendored code out of the count. Write down the exact count command so step 6 runs the same one. If the project has a coverage tool, record line coverage of the app code (tests excluded) for step 5.

Done when you have a line count, the command that produced it, coverage or a note that there is no coverage tool, and the checks passing. A check that already fails is noted as failing before pruning and doesn't block the run.

## 2. Find

Look for sediment of every kind below. Read [references/finders.md](references/finders.md) for the tools per ecosystem and how to check docs against code.

- **Dead code:** unused files, exports, functions, types, props, routes and CSS. Feature flags with the same value in every environment, and the branches they switch off.
- **Dependencies:** unused packages, two packages that do the same job, and a package the platform or the language already covers.
- **Comments:** commented-out code, comments that restate the next line, and TODOs that are done or obsolete.
- **Docs and agent context:** `CLAUDE.md`, `AGENTS.md`, `README`, `docs/`, project skills and code comments that name a command, path, flag or behaviour that no longer exists, two documents that state the same rule, and two that contradict each other or the code.
- **Tests:** skipped or disabled tests, snapshots, fixtures, mocks and test helpers that no test uses, tests that repeat another test's case, and tests that only assert a mock was called.
- **Long code:** duplicated helpers, hand-written versions of a function the standard library or an installed package already has, and wrappers that only pass their arguments through.

Every candidate needs evidence that it is unused or stale, such as `rg` finding no other reference or the doc's command missing from `package.json`. Tools miss references by string and by convention, so search for each name before calling it unused: dynamic imports, framework file routes, config files, scripts, CI workflows and docs.

Done when every kind above has been searched and each candidate has its evidence, or the kind has none in this repo.

## 3. Sort

Give each candidate one verdict:

- **delete:** nothing uses it.
- **rewrite:** it is still needed but can be shorter. Merge duplicates into one source, replace the hand-written helper with the library call, or turn a long comment into a better name.
- **keep:** with a one-line reason. Keep the public API of a published library, migrations that have run anywhere, and code that a test or an import outside the repo uses.
- **ask:** the owner has to decide. This is for a conflict where neither the doc nor the code is clearly right, or code that looks unused but might serve a user or a job you can't see.

When two documents conflict, the code decides which one is true. Fix the wrong one, keep the rule in one place, and point to it from the other.

Done when every candidate has a verdict.

## 4. Plan

Show a table of the cuts grouped into PRs, with the estimated lines removed per PR, then the **ask** items as numbered questions with a recommended answer each. Group by kind, one kind per PR, so each PR has one reason to revert. Order them from least to most risky: comments and docs, dependencies, dead code, rewrites, and tests last. Keep a PR to about 400 changed lines, not counting deletions, generated files and lockfiles.

Wait for the owner. Done when they approve the plan and answer the questions.

## 5. Cut

Cut code before tests, so the full test suite checks every code cut.

**Code.** Build one PR at a time and run the checks after each. When a test fails, find out what it covers:

- Behaviour the app still has: the cut was wrong. Put the code back and mark that cut **keep** with the reason.
- Only the code you deleted: delete the test in the same PR.

Fix a failing test by one of those two moves only. Editing its assertions to make it pass hides a wrong cut.

**Tests.** Start once every code PR is green. Deleting a test never makes a check fail, so coverage is the guard here. Measure line coverage of the app code again after each test PR. A cut that lowers it goes back and is marked **keep**. Without a coverage tool, cut only skipped tests and unused snapshots, fixtures, mocks and helpers.

File each PR the project's usual way, with its net line change in the body.

Done when every approved cut is in a PR with green checks and coverage no lower than the baseline, or is marked keep with the reason it failed.

## 6. Report

Run the count command from step 1 again. Report the lines before and after, the PR links, and every **keep** with its reason. Then point the owner to `/improve-codebase-architecture` as the next step, now that the sediment is out of its way.
