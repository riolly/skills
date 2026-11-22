# skills

Agent skills, published as a plugin marketplace with one plugin, `riolly-skills`, that holds every skill. README.md lists them.

Phase: v0.x since 2026-11-16. A skill runs in every project that installs it, and a wrong instruction fails without an error.

## Commands

- `uv run --python 3.12 tests/test_feature_walkthrough.py` checks the `feature-walkthrough` scripts. No other skill has tests.
- `./install.sh` in `riolly/dotfiles` brings a merge here to a machine.

## Rules that are expensive to break

- **A changed checklist item shows its status at both pinned commits.** When a `phase-up` item or eval expectation changes, read YoungPro at the two commits in `skills/phase-up/references/youngpro.md` and put the result and the command in the PR body. One PR counted the test runner as a flow script because nobody read the commit.
- **A skill starts from a plain phrase.** Keep a trigger description, and set `disable-model-invocation` only when the owner asks for a slash-only skill. `prune` shipped manual-only, and "prune this project" did nothing.
- **This repo is public and YoungPro is private.** Name its files and decisions. Never copy its data, secrets or anything about its users.
- **Every skill lives in the one `riolly-skills` plugin.** A plugin per skill with `source: "./"` puts the whole `skills/` folder in each install, and T3 Code then lists every skill once per plugin.
- **A new skill stays on a branch until it passes an eval on a real project.** Merging it to `main` ships it to every machine and every plugin user at once.
