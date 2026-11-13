---
name: prune
description: Cut a codebase down. Find unused code, dependencies, comments and docs, and stale or conflicting agent context, then delete or shorten them in small PRs. Run it before improve-codebase-architecture.
disable-model-invocation: true
---

# Prune

Pruning makes a codebase smaller without changing what it does. The measure is lines removed from code and words removed from docs, while every check stays green. A **cut** is one finding that is deleted or rewritten shorter. A cut that drops an exported name or corrects a stale claim counts even when it removes no lines. **Sediment** is anything still in the repo that no longer bears on what the code does: dead code, unused dependencies, comments that repeat the code, docs and agent context that went stale or contradict each other, and tests that check nothing.

If the user named a directory or a kind of cut, prune only that. "Every kind" and "every directory" below then mean the ones in scope.

## 1. Baseline

Find the project's checks (typecheck, lint, tests, build) from its `CLAUDE.md`, `package.json` scripts or CI workflow, and run them. A test that skips because a build artifact or a native module is missing has not run. Build what it needs and run the suite again. If it can't be built here, name the skipped test files in the plan, because no check guards a cut in the code they cover.

Count lines with `scc` or `tokei` if installed, otherwise `git ls-files -z | xargs -0 wc -l`. Count the words in the docs as well, because a doc with long lines hides its size from a line count. Leave only lockfiles, generated files, migrations and vendored code out of the count. A path that a project rule protects, such as a read-only or archived folder, stays in the count and in the search. Write down the exact count commands so step 6 runs the same ones.

List the largest directories by line count with the command in [references/finders.md](references/finders.md). Step 2 searches them in that order. If the project has a coverage tool, record line coverage of the app code (tests excluded) for step 5.

Done when you have the line count, the doc word count, the commands that produced them, the largest directories, coverage or a note that there is no coverage tool, and the checks passing with every skipped test either run or named. A check that already fails is noted as failing before pruning and doesn't block the run.

## 2. Find

Look for sediment of every kind below, in every directory listed in step 1, tests included. Read [references/finders.md](references/finders.md) for the tools per ecosystem, how to find duplicates and how to check docs against code.

- **Dead code:** unused files, exports, functions, types, props, routes and CSS. Feature flags with the same value in every environment, and the branches they switch off.
- **Dependencies:** unused packages, two packages that do the same job, and a package the platform or the language already covers.
- **Comments:** commented-out code, comments that restate the next line, and TODOs that are done or obsolete.
- **Docs and agent context:** `CLAUDE.md`, `AGENTS.md`, `README`, `docs/`, project skills and code comments that name a command, path, flag or behaviour that no longer exists, two documents that state the same rule, and two that contradict each other or the code.
- **Tests:** skipped or disabled tests, snapshots, fixtures, mocks and test helpers that no test uses, tests that repeat another test's case, and tests that only assert a mock was called.
- **Long code:** helpers and constants defined in more than one file, one definition written out twice by hand (a schema and its DDL, a type and its validator), hand-written versions of a function the standard library or an installed package already has, and wrappers that only pass their arguments through.

Every candidate needs evidence that it is unused or stale, such as `rg` finding no other reference or the doc's command missing from `package.json`. Tools miss references by string and by convention, so search for each name before calling it unused: dynamic imports, framework file routes, config files, scripts, CI workflows and docs.

Done when every kind above has its candidates with their evidence, or the command that found none, and a finder has run over every directory listed in step 1.

## 3. Sort

Give each candidate one verdict:

- **delete:** nothing uses it. This holds at any size. An export that nothing outside its file uses loses its `export` keyword, though no line goes.
- **rewrite:** it is still needed but can be shorter. Merge duplicates into one source, replace the hand-written helper with the library call, or turn a long comment into a better name. Shorten a doc that repeats another to its outcome and a link.
- **keep:** with a one-line reason. Keep the public API of a published library, migrations that have run anywhere, and code that a test or an import outside the repo uses.
- **ask:** the owner has to decide. This is for a conflict where neither the doc nor the code is clearly right, code that looks unused but might serve a user or a job you can't see, a definition written out twice by hand, and any cut in a path that a project rule protects.

When two documents conflict, the code decides which one is true. Fix the wrong one, keep the rule in one place, and point to it from the other.

Done when every candidate has a verdict.

## 4. Plan

Show three things:

1. The search, as a table with one row per kind from step 2. Each row gives what the search found, or the command that found none.
2. The cuts grouped into PRs, with the estimated lines and doc words removed per PR.
3. The **ask** items as numbered questions, each with its size and a recommended answer.

Under the cuts, name the test files from step 1 that could not run and the cuts in the code they cover.

Group the cuts by kind, one kind per PR, so each PR has one reason to revert. Order them from least to most risky: comments and docs, dependencies, dead code, rewrites, and tests last. Keep a PR to about 400 changed lines, not counting deletions, generated files and lockfiles.

Wait for the owner. Done when they approve the plan and answer the questions.

## 5. Cut

Cut code before tests, so the full test suite checks every code cut.

**Code.** Build one PR at a time and run the checks after each. When a test fails, find out what it covers:

- Behaviour the app still has: the cut was wrong. Put the code back and mark that cut **keep** with the reason.
- Only the code you deleted: delete the test in the same PR.

Fix a failing test by one of those two moves only. Editing its assertions to make it pass hides a wrong cut.

**Tests.** Start once every code PR is green. Deleting a test never makes a check fail, so coverage is the guard here. Measure line coverage of the app code again after each test PR. A cut that lowers it goes back and is marked **keep**. Without a coverage tool, cut only skipped tests and unused snapshots, fixtures, mocks and helpers.

File each PR the project's usual way, with its net change in lines and doc words in the body.

Done when every approved cut is in a PR with green checks and coverage no lower than the baseline, or is marked keep with the reason it failed.

## 6. Report

Run the count commands from step 1 again. Report the lines and doc words before and after, the PR links, and every **keep** with its reason. Then point the owner to `/improve-codebase-architecture` as the next step, now that the sediment is out of its way.
