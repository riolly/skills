---
name: feature-walkthrough
description: Record narrated, captioned feature walkthroughs, compare app versions across browser tabs, add circles, rectangles and animated pointer gestures, and include terminal output. Use when the user asks for a video demo, before-and-after comparison, or walkthrough. Also use while planning a user-visible web change, to decide whether a recording is worth offering; most changes need none.
---

# Feature walkthrough

Create a short video of the actual workflow, with a small set of steps the viewer can try. Deliver an MP4 with readable captions and, when useful, spoken narration. Aim for 30–90 seconds per workflow; use shorter clips for simple changes. Explain the result like the engineer who built it: what changed, why it helps, what to click, and what the viewer should see. Sound confident and interested without inventing benefits or overstating what was verified.

For narration, read [spoken walkthroughs](references/narration.md). A local Piper voice can read the same timed text used for captions without an API key. Keep captions useful with sound muted. Prefer a silent video when the user asks for one or narration adds little.

## Decide whether to record

A recording costs minutes, and most changes do not need one. Decide early when possible, and revise the choice if the work reveals a flow worth demonstrating.

Honor the user's current and earlier recording preferences, including applicable `AGENTS.md` instructions. Record without asking when a video is already requested, or the user invoked this skill to create one. When there is no existing preference, judge how hard the change is to check by hand:

| Checking the change | What to do |
| --- | --- |
| Obvious. A few written steps cover it, such as a new button, a text or style change, or one form field. | Do not record and do not ask. Finish with the written steps and the expected result. |
| Medium. Several steps or states, or a result that is easier to see than to describe. | Ask once, with the other planning questions. Offer written steps, the recommended choice, or a short recording. |
| Hard. A long flow, timing or animation, a before-and-after comparison, or several apps or tabs. | Ask once, with the other planning questions. Offer a recording, the recommended choice, or written steps. |

Name what the recording would show, and use a question tool permitted in the current mode when available. Ask during planning when possible; with an asynchronous question tool, continue implementation and verification while waiting. When nobody can answer, as in a non-interactive run, use written steps unless a recording was already requested.

The answer holds for the whole task. After a decline, do not ask again or record anyway; the user can still request a video later. Stop reading here when the answer is no.

## Keep the answer ahead of the video

Finish and verify the work, then send the written result as a progress update before recording: what changed, the steps to try, and the expected results.

In Codex, use a commentary message for this update and keep the turn active while recording. The final response must include the written result and the verified video or a concrete recording limitation. A background command or subagent alone does not guarantee an automatic follow-up after the turn ends.

Prefer a recording subagent when delegation is available and allowed by the runtime and user instructions. Otherwise, record in the main agent. Choose the recording backend independently: use T3's shared preview when available, and use the portable recorder only through the fallback described below. Portable recording and finishing commands may run in the background, but retain their session or job handles and collect their results before final delivery.

Only in a client that explicitly supports keeping the job alive and automatically resuming the main thread after completion may the video follow an ended turn. In that case, start the recording job before ending the turn, include the written result and a line saying the video will follow, and verify the finished video before posting the follow-up. Do not infer this capability from the presence of subagent tools, including in Claude Code.

Subagents may inherit the conversation or start with limited context. Give the recording agent a self-contained brief either way:

- this skill's directory, and the instruction to follow its recording and finishing sections
- the app URL or port, the revision it should be serving, and any sample data to use
- each action in order, with the result the viewer should see after it
- the caption text, and whether narration is wanted
- the absolute path for the final MP4
- what to return: the final path, what the frames showed, and any step that failed

When a subagent drives the shared preview, leave that tab alone until it reports back. Review the returned file and key frames according to the recording steps below before delivery.

If recording fails, report the limitation with the written steps in the final response or supported follow-up. Preserve the verified feature result without claiming that an unfinished recording is ready.

## Locate the installed helpers

This skill follows the Agent Skills format and works with Claude Code and Codex. Resolve paths from the directory containing this loaded `SKILL.md`, including when the installer uses symlinks. In Claude Code, `${CLAUDE_SKILL_DIR}` identifies that directory. In Codex, use the skill location supplied by the runtime. The examples below use a task-specific shell variable:

```sh
WALKTHROUGH_SKILL_DIR="/absolute/path/to/feature-walkthrough"
```

Replace that value with the resolved installed location. Run the helpers with `uv run`; Python dependencies are pinned inline and FFmpeg is supplied by a package. Installing the skill with `npx skills add` copies its instructions and helpers, not browser binaries, terminal tools, or voice models. Read [portable recording](references/portable.md) for prerequisites and recording without T3.

## Record the browser

In T3 Code, use its collaborative browser tools. They already support recording; no browser extension, API key, or separate recorder is required.

1. Call `preview_status`, then `preview_open` if no automation-capable tab is attached. Keep the returned `tabId` for all calls in the recording. Discover the exact schemas if these tools are lazy-loaded.
2. Open the relevant app version with `preview_navigate`. Prefer `{target: {kind: 'environment-port', port: PORT, path: '/'}}` for a local server, or provide the exact feature route. Verify the loaded revision; an existing localhost origin may serve an older installed PWA from its service worker. Prefer a fresh port to changing that origin's saved data or service worker. If navigation fails, inspect the error and page diagnostics, correct the address or binding, and retry. A deployed app is suitable for a recording test, but do not present an older deployment as evidence of an unshipped change. Report an unreachable worktree server as a limitation.
3. Use a readable, stable viewport, normally 1280×800. Inspect with `preview_snapshot` and rehearse the required actions before starting. Use sample data and avoid showing credentials. Do not clear an existing user's saved data to prepare a demo.
4. Call `preview_recording_start({tabId})`. Record its `startedAt` and each action's time for caption timing. Operate the app with the normal preview click, type, scroll, and press tools, using locators observed in the snapshot. Leave about 3–5 seconds after each result so the viewer can follow. For circles, rectangles, pointer wiggles, or orbit gestures, use the temporary annotation helper described in [advanced walkthroughs](references/advanced.md). T3 has no mouse-move tool; these gestures use a drawn pointer and do not move the OS mouse.
5. Call `preview_recording_stop({tabId})`, including when an action fails. It returns a local video `path` after transferring the file. Preserve that path immediately; stopping again is not a recovery method. Respect the transfer limit documented by the current tool and split long workflows into separate clips. Do not assume audio or native-app windows are included.
6. Verify that the returned file exists and decodes. Match captions to the actual video, not just the planned actions. Trim long idle time and keep loading failures out of a success walkthrough. Label mock data, simulations, or staging behavior when they affect what the viewer should expect.

Use `scripts/finish_video.py` for consistent MP4 conversion, trimming, and captions. Run it with `uv run`; its pinned dependency supplies FFmpeg without sudo. Inputs may be the native MP4 or a WebM recording. Example:

```sh
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/finish_video.py \
  /absolute/path/raw.mp4 /absolute/path/artifacts/walkthrough/feature.mp4 \
  --captions /absolute/path/captions.json --start 3 --duration 40
```

Caption times are seconds relative to the final trimmed clip. Write JSON as:

```json
[
  {"start": 0, "end": 5, "text": "Open Practise, then choose Programming."},
  {"start": 5, "end": 10, "text": "Search for React. The list shows matching questions."}
]
```

The helper scales to at most 1280 pixels wide, puts captions in a separate band below the app, produces H.264 MP4 with fast start, and checks the result by decoding it. It never replaces the input. Existing output requires `--force`. Read several extracted frames, including each key result, to check timing and readability before delivery.

## When T3 preview tools are absent

Use an available browser integration with native video recording if it supports one. Otherwise, use `scripts/record_browser.py` as described in [portable recording](references/portable.md). It uses Playwright to record a real workflow, including the annotation helper, without an agent-specific MCP server. This is the normal path for Claude Code or Codex CLI without T3 preview tools. A navigation failure in an available T3 preview alone is not a reason to switch browser systems.

## Deliver the walkthrough

Save the final clip under the project's ignored `artifacts/walkthrough/` directory or another durable local artifact directory. In a client that supports local video embeds, use `![Feature walkthrough](/absolute/path/feature.mp4)`. In a terminal client such as Claude Code CLI, give the absolute path and a link supported by that client; do not claim an inline player exists. Keep the text to what changed, the version or URL demonstrated, and a few concrete actions with expected results. Mention any important unverified behavior. Keep binary recordings out of source control unless the project asks for them.

For before-and-after comparisons, several tabs, different web apps, terminal segments, or side-by-side playback, read [advanced walkthroughs](references/advanced.md). A composed browser/terminal video is assembled from separate recordings. Full desktop capture and native app switching require a separate desktop recorder and display access.

Sources: live T3 Code recording tool descriptions; [Playwright video recording](https://playwright.dev/python/docs/videos); [Claude Code skills](https://code.claude.com/docs/en/skills); [FFmpeg filters](https://www.ffmpeg.org/ffmpeg-filters.html); [asciinema recording](https://docs.asciinema.org/manual/cli/quick-start/).
