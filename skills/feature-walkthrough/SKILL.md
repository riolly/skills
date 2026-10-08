---
name: feature-walkthrough
description: Record narrated, captioned feature walkthroughs, compare app versions across browser tabs, add circles, rectangles and animated pointer gestures, and include terminal output. Use when the user asks for a video demo, before-and-after comparison, or walkthrough. Also use while planning a user-visible web change, to decide whether a recording is worth offering; most changes need none.
---

# Feature walkthrough

Create a short video of the actual workflow, with a small set of steps the viewer can try. Deliver an MP4 with readable app text, a visible title, compact captions, and spoken narration by default. Use silent output when the user requests it. Aim for 30–90 seconds per workflow; use shorter clips for simple changes. Explain what changed, why it helps, what to click, and what the viewer should see. Support claims with the demonstrated behavior.

For every narrated recording, read [spoken walkthroughs](references/narration.md) before planning scene lengths. A local Piper voice reads the same timed text used for captions without an API key. Captions remain useful with sound muted. If voice setup fails, report the failure explicitly with the available captioned clip.

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

Prefer a recording subagent when delegation is available and allowed by the runtime and user instructions. The user's yes to a recording also approves a recording subagent, unless they have said otherwise. Otherwise, record in the main agent. Choose the recording backend independently: use T3's shared preview when available, and use the portable recorder only through the fallback described below. Portable recording and finishing commands may run in the background, but retain their session or job handles and collect their results before final delivery.

Only in a client that explicitly supports keeping the job alive and automatically resuming the main thread after completion may the video follow an ended turn. In that case, start the recording job before ending the turn, include the written result and a line saying the video will follow, and verify the finished video before posting the follow-up. Do not infer this capability from the presence of subagent tools alone. Claude Code qualifies when its tool descriptions state that background work re-invokes the main thread on completion.

Subagents may inherit the conversation or start with limited context. Give the recording agent a self-contained brief either way:

- this skill's directory, and the instruction to follow its recording and finishing sections
- the app URL or port, the revision it should be serving, and any sample data to use
- each action in order, with the result the viewer should see after it
- the title and caption text, the narration choice, and any required encoder or GPU
- the absolute path for the final MP4
- what to return: the final path, export report, frame review, playback checks, and any failed or unavailable check

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
3. Set an explicit stable viewport with `preview_resize`. Start with 1280×900 in T3 and inspect actual raw frames before selecting a larger capture. Its recorder can soften text at larger viewports despite reporting those larger dimensions. Use native 1920×1080 with recorders that retain that detail. Rehearse the actions with `preview_snapshot`. For dense screens, increase browser zoom or frame fewer controls while keeping titles and results visible. Use sample data and preserve the user's saved data.
4. Call `preview_recording_start({tabId})`. Record its `startedAt` and each action's time for caption timing. Operate the app with the normal preview click, type, scroll, and press tools, using locators observed in the snapshot. Leave about 3–5 seconds after each result so the viewer can follow. For circles, rectangles, pointer wiggles, or orbit gestures, use the temporary annotation helper described in [advanced walkthroughs](references/advanced.md). T3 has no mouse-move tool; these gestures use a drawn pointer and do not move the OS mouse.
5. Call `preview_recording_stop({tabId})`, including when an action fails. It returns a local video `path` after transferring the file. Preserve that path immediately; stopping again is not a recovery method. Respect the transfer limit documented by the current tool and split long workflows into separate clips. Do not assume audio or native-app windows are included.
6. Inspect the raw video's measured dimensions and a frame of the smallest relevant app text. The requested viewport alone does not prove capture resolution. If text is unreadable, adjust zoom or framing and record again. Match captions to the actual video, trim long idle time, and label mock data or staging behavior when they affect expectations.

## Export and verify

Read [export quality](references/quality.md) for GPU setup and playback checks before exporting. The helpers preserve input resolution and use NVIDIA NVENC when a real encoding probe succeeds, with a reported CPU fallback. Their packaged FFmpeg works without sudo but lacks NVENC; the quality guide covers selecting a capable build.

1. Finish trimming or composition before adding narration. Inputs may be native MP4 or WebM. For example:

```sh
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/finish_video.py \
  /absolute/path/raw.mp4 /absolute/path/artifacts/walkthrough/feature.mp4 \
  --start 3 --duration 40
```

2. Write cues timed in seconds relative to the final trimmed clip, allowing each sentence to finish:

```json
[
  {"start": 0, "end": 7, "text": "Open Practise, then choose Programming."},
  {"start": 7, "end": 14, "text": "Search for React. The list shows matching questions."}
]
```

3. Run `scripts/narrate_video.py` with `--captions cues.json` and `--title "A concise walkthrough title"` on the edited clip, as shown in the narration guide. For a composition that already has source titles, preserve those headers and omit `--title`. This adds the caption footer once. For explicitly silent output, pass `--captions` and `--title` to `finish_video.py` instead.
4. Require the final export report to confirm portable MP4 and complete decoding, plus audible audio for narrated output. Inspect extracted frames at every key result and cue boundary. Titles must remain visible and captions must fit below the app. Check that app text stays readable at normal playback size.
5. Open the final MP4 in the available browser/player and verify playback advances, seeking works, and sound is present. Serve that same file with a download link, save a copy, and verify the copy plays. Report any unavailable playback or listening check. Deliver only after these checks pass or the remaining limitation is stated.

The helpers produce 8-bit H.264 video, AAC audio when present, and a finalized fast-start MP4. They preserve the input and require `--force` for an existing output. Deliver the final exported `.mp4`, using its actual path.

## When T3 preview tools are absent

Use an available browser integration with native video recording if it supports one. Otherwise, use `scripts/record_browser.py` as described in [portable recording](references/portable.md). It uses Playwright to record a real workflow, including the annotation helper, without an agent-specific MCP server. This is the normal path for Claude Code or Codex CLI without T3 preview tools. A navigation failure in an available T3 preview alone is not a reason to switch browser systems.

## Deliver the walkthrough

Save the final clip under the project's ignored `artifacts/walkthrough/` directory or another durable local artifact directory. In a client that supports local video embeds, use `![Feature walkthrough](/absolute/path/feature.mp4)`. In a terminal client such as Claude Code CLI, give the absolute path and a link supported by that client; do not claim an inline player exists. Keep the text to what changed, the version or URL demonstrated, and a few concrete actions with expected results. Mention any important unverified behavior. Keep binary recordings out of source control unless the project asks for them.

For before-and-after comparisons, several tabs, different web apps, terminal segments, or side-by-side playback, read [advanced walkthroughs](references/advanced.md). A composed browser/terminal video is assembled from separate recordings. Full desktop capture and native app switching require a separate desktop recorder and display access.

Sources: live T3 Code recording tool descriptions; [Playwright video recording](https://playwright.dev/python/docs/videos); [Claude Code skills](https://code.claude.com/docs/en/skills); [FFmpeg filters](https://www.ffmpeg.org/ffmpeg-filters.html); [asciinema recording](https://docs.asciinema.org/manual/cli/quick-start/).
