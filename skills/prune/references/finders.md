# Finders

Tools that list prune candidates, by ecosystem. Each one gives candidates, not verdicts. Check every hit with `rg` before cutting it.

## Size

Give both commands the count's exclusions as pathspecs after the `--`, such as `':!bun.lock' ':!vendor/**'`.

- The largest directories, two levels deep: `git ls-files -z -- . | xargs -0 wc -l | awk '$2!="total"{n=split($2,p,"/"); d=(n==1?".":(n==2?p[1]:p[1]"/"p[2])); s[d]+=$1} END{for(k in s) print s[k], k}' | sort -rn | head -20`. The list exists so that no large area is skipped. A directory on it that no finder below has run over has not been searched yet.
- Words in the docs: `git ls-files -z -- '*.md' '*.mdx' '*.rst' '*.txt' | xargs -0 cat | wc -w`.

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

## Duplicates

Run these over the test files as well as the app code. Helpers copied between test files are the common case.

- Copied blocks: `npx jscpd <dir> --min-lines 5 --min-tokens 50 --reporters console` works for most languages. Pass `--ignore` for fixtures and generated files.
- One name defined in several files: `rg -o --no-filename '^\s*(export )?(async )?function (\w+)|^\s*(export )?const (\w+)\s*[:=]' -r '$3$5' <dir> | sort | uniq -c | awk '$1>1' | sort -rn`. Change the pattern to the language's definition syntax. Read each hit, because two files can use one name for different things.
- One definition written out twice by hand: `rg -n -i 'parity|mirrors?\b|in sync|by hand'` in tests and comments. A test that compares two files, such as a schema and its DDL, marks the pair. Raise the pair as an **ask** item with the size of the second copy. Generating one from the other removes that copy, in its own PR, once the generated output matches the hand-written one. The comparing test goes only when the build generates the copy and nobody commits it.
- Compare two copies before merging them. A different regex, default or edge case is a difference in behaviour, and those two stay separate.
- Merging helpers copied between test files is a rewrite. The tests that use the helper check the merge, so it goes in the rewrite PR.

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
