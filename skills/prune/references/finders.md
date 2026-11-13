# Finders

Tools that list prune candidates, by ecosystem. Each one gives candidates, not verdicts. Check every hit with `rg` before cutting it.

## JavaScript and TypeScript

- `npx knip` lists unused files, exports, types, dependencies and devDependencies, and packages used but not listed. It has plugins for most frameworks. When it reports framework entry files (TanStack Start routes, Astro pages, config files) as unused, add them to `entry` in a `knip.json` instead of deleting them.
- `npx tsc --noEmit --noUnusedLocals --noUnusedParameters` lists unused locals and parameters without changing `tsconfig.json`.
- For CSS, search each class name in a stylesheet across the templates.

## Python

- `ruff check --select F401,F841,ERA001` finds unused imports, unused variables and commented-out code.
- `vulture .` finds unused functions, classes and variables, each with a confidence score. Unused functions and classes report 60%, so check each with `rg`. Unreachable code reports 100%.
- `deptry .` finds unused and missing dependencies.

## Go

- `go run golang.org/x/tools/cmd/deadcode@latest ./...` lists functions that no entry point reaches.
- `staticcheck -checks U1000 ./...` lists unused code.
- `go mod tidy` drops unused modules. Commit its diff as its own cut.

## Rust

- The compiler's `dead_code` and `unused_*` warnings from `cargo check`.
- `cargo machete` finds unused dependencies.

## Any repo

- Commented-out code: `rg -n '^\s*(//|#)\s*(import|const|let|var|function|def|return|if|for|await|export)\b'`.
- TODOs: `rg -n 'TODO|FIXME|XXX|HACK'`, then check each against the code and `git log`.
- Files nobody touches: `git log -1 --format=%cr -- <file>`. Age alone is no verdict, only a reason to look.

## Tests

- Skipped tests: `rg -n '\.(skip|todo)\(|\bx(it|describe|test)\(|@pytest\.mark\.skip|@unittest\.skip|t\.Skip\(|#\[ignore\]'`. Cut one only when its reason is gone or it has been skipped for months (`git log -1 --format=%cr -S '<skip line>'`).
- Unused fixtures, mocks and helpers: search each exported name and file name in the test files. For snapshots, the Vitest and Jest summaries list obsolete ones, and `npx vitest run -u` or `npx jest -u` deletes them. Run `-u` only on a green suite, because it also rewrites failing snapshots.
- Coverage of the app code: `npx vitest run --coverage`, `npx jest --coverage`, `pytest --cov=<package>`, `go test -cover ./...`, `cargo llvm-cov`. Compare the line percentage for the app files, not the total, because deleting tests changes the total's base.

## Docs and agent context

Check every claim a doc makes that the repo can confirm:

- Each command it names exists in `package.json` scripts, the `Makefile`, `justfile` or `bin/`.
- Each path it names exists: `git ls-files | rg <path>`.
- Each env var it names is still read somewhere in the code.
- Each rule appears in one document only. When two documents state it, keep it in the one the agent loads, usually `CLAUDE.md` or `AGENTS.md`, and point to it from the other.
- A doc that copies something one command can show, such as a script list, a directory tree or a dependency list, is a copy that goes stale. Replace it with the command, or delete it.
