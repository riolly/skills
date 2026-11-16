---
name: brief
description: Status report on every active project, or one, and what waits on the user. Use when the user says "brief" or "brief <project>", asks where a project stands or what waits on them, or answers a printed Decide list by number such as "1a 2b".
---

# Brief

A brief is a status report read fresh from GitHub. The **registry** is `riolly/dotfiles`: `projects.yaml` on `main` lists the active projects, and each open issue labelled `needs-you` is one thing that waits on the user, titled `<project>: Decide ...` or `<project>: Do ...`. Everything else (PRs, checks, release branches, `Phase:` lines, local commits) is read from the repos and this machine on every run. The skill keeps no file of its own.

The brief is read-only. Its only writes are a comment and a close on a `needs-you` issue, in step 3 and step 4. Merging, pushing, editing a project and filing new issues belong to other skills; a brief stops at a **ready** PR: not draft, mergeable, no check failing or pending (a repo with no checks counts). Unchecked `Before merge` boxes are the user's steps, so a PR with them can still be ready.

## 1. Collect

Run the collector once, from any folder:

```bash
bash <this skill's folder>/scripts/collect.sh            # every project
bash <this skill's folder>/scripts/collect.sh <project>  # one project, by name or alias
```

It prints the machine's name, the registry, one block per project, then the open `needs-you` issues, then the state of every PR an issue links to. With a project named it adds the last five merged PRs and keeps only that project's issues. Exit code 2 means the name matched no project or two; show the list it printed and ask which one. If it fails to read `projects.yaml`, report the error and stop.

The collector is the whole data source. Base the brief on its output alone, and run a further `gh` call only to prove a close in step 3.

Done when the collector exited 0 and printed a block for every project.

## 2. Report

Print the report in this order, and leave out a heading with nothing under it.

**State.** One sentence: how many projects, how many ready PRs, how many `Decide` issues, and how many `Do` items (each `Do` issue plus each PR with unchecked boxes and no issue).

**Table.** One row per project, in `projects.yaml` order:

| Project | Phase | In flight | Waits on you |
| --- | --- | --- | --- |
| YoungPro | v0.x | #31 ready; `feat/3-follow-up` 163 ahead, 5 days | #11, 4 PR steps |

Phase is the version from the `Phase:` line, or `none`. In flight names each open PR as ready, checks pending, checks failing (with the check's name), conflicting, or draft, plus the `target` gap when there is one. Waits on you lists the issue numbers and the count of unchecked PR steps. Write `none` in an empty cell.

**Decide.** Every open `Decide` issue, numbered from 1 in table order, then by issue number. Under each, the options as lettered lines with the recommendation as `a`, relabelled if the issue lists it later, a link to the issue, and what it blocks. The user answers with `1a 2b`.

**Do.** Every open `Do` issue, then each open PR with unchecked `Before merge` or `After merge` boxes and no issue, each step with its command or link. When a `Do` issue links a PR, list the PR's unchecked boxes under the issue, drop the issue's lines that repeat them, and keep its other steps, such as the merge itself. When the collector shows that part of an issue is out of date, such as a PR it waits on that has since merged, say so under the item.

**Flags.** Each of these, with the evidence line from the collector:

- `STALE` on a `target` line: the release branch holds commits more than three days old.
- `target: MISSING`: the branch is gone, so `projects.yaml` is out of date.
- `unpushed` or `uncommitted` lines: work that exists on this machine only. Name the machine from the `machine:` line. Work on another machine shows only when the brief runs there.
- `behind` lines: pull before working in that checkout.
- `phase: MISSING`: suggest `phase-up` for that project.
- A `needs-you` issue whose project prefix matches no entry in `projects.yaml`.

**Proof and links.** The deploy links of every project that has them, and the issues closed in step 3, each with its proof.

For `brief <project>`, print the same sections for that project, and add the merged PRs and every PR's full state line in place of the table row.

Done when every issue, every unchecked PR box and every flag in the collector output appears once in the report.

## 3. Close what GitHub shows is done

A `Do` issue is done when GitHub proves every step it lists: the linked PR shows `merged`, the PR's `After merge` boxes are checked, the release PR it asks for exists. Close it with a comment that quotes the proof:

```bash
gh issue close <n> -R <registry> --comment "Done: #31 merged on 2026-11-17 and its After merge boxes are checked. Closed by brief."
```

When the proof covers only some steps, leave the issue open and say in the report which steps remain. A step that happens off GitHub, such as sending a letter, leaves its issue open for the user to close. A `Decide` issue closes only through step 4.

## 4. Record answers

When the user answers by number after a brief in this thread, map each number and letter to the issue and option in the printed Decide list. Without a printed list in this thread, run steps 1 and 2 first and ask the user to answer that list. For each answer:

```bash
gh issue close <n> -R <registry> --comment "Decided: <the option's full text>. Answered in a brief on <date>."
```

Record the option's text, because the letters were relabelled for the report. An answer that matches no option is recorded in the user's words. Reply with one line per closed issue and its link.
