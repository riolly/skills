---
name: feedback-round
description: Turn a batch of user feedback into small PRs. It triages each item, asks about unclear ones, slices the work into PRs of about 400 lines and drafts the reply to users. Use when the user says "feedback round" or pastes a batch of feedback (several items) from users or a client.
---

# Feedback round

One round takes a batch of feedback from users to merged PRs and a reply they can read. Two roles: the **owner** runs the round with you and approves; the **users** sent the feedback and only get the reply. The unit of work is a **slice**: one PR, about 400 changed lines at most (not counting generated files such as migration snapshots and lockfiles), with one reason to revert. YoungPro's second round shipped as one PR of +1460 −499 lines across 21 files, which nobody could review or revert in parts. Slicing at the start prevents that.

## 1. Capture

Number every item. Keep the sender's own words, and add a translation beside them if they wrote in another language. Note who asked and any screenshot. Split a message that asks for two things into two items.

Done when every sentence in the batch that reports a problem or asks for something maps to an item number.

## 2. Triage

Users often report from an old version, or ask for something that already exists. For each item, check the current code and recent history first, then record:

- **Kind:** done (already shipped: say since when and where to find it), bug, change, new, question, or decline.
- **Area:** the screen or module, named the way the codebase names it.
- **Size:** S (under 50 lines), M (under 200) or L (more), with a note when it needs a schema change.
- **Next:** a decision, a question for the owner, or a question only the users can answer.

Check each item against the product principle in the project's `CLAUDE.md`. An item that works against it gets **decline** with the reason, or a smaller change that gives the users what they actually need. Two items that contradict each other become one question.

Done when every item has all four fields.

## 3. Ask

Send the owner every open question and every decline in one message, numbered by item. Give each question a recommended answer, so the owner can reply "yes to all" or correct only some. Wait for the answers.

A question only the users can answer is marked **open**, goes into the reply in step 6, and doesn't block the round.

Done when no item is waiting on the owner.

## 4. Slice

Group items into slices:

- Items that touch the same files go in the same slice, so slices don't conflict when built in parallel.
- A schema change gets a slice of its own, because it needs its own migration and rehearsal steps.
- Bugs come first, in a small slice that can ship the same day.
- Split any slice estimated over 400 lines.

Order slices by what users meet first, and by any date they named (a meeting, an event). Show the plan as a table: slice name (it becomes the branch name), item numbers, estimated lines, migration yes or no, order. Wait for the owner to approve it.

Done when the owner approves the plan.

## 5. Build

Build one slice per PR, each in a fresh context: a new thread or worktree per slice when the owner wants them in parallel, or one after another here. Each slice follows the project's workflow and its PR body lists the item numbers it closes, in the users' words. If a slice grows past about 600 lines while building, split it before filing.

Done when every slice is a PR, or the owner has dropped it.

## 6. Close the round

Show a table of every item with its final status: the PR that closes it, declined (with the reason), or still open.

Then draft the reply to the users, in the language they wrote in, short enough for a chat message:
- what's fixed and what changed, in their words, not code names
- what already existed, and how to reach it (refresh the app, where to tap)
- what won't happen, and why
- the open questions only they can answer

The owner sends it. Never send it yourself.

Done when every item has a final status and the owner has the draft.
