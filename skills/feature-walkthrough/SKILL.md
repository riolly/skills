---
name: feature-walkthrough
description: Pick and make the proof for a user-visible change. That is a marked screenshot, a marked before-and-after pair, or a captioned or narrated video, with browser-tab comparisons, pointer gestures and terminal output. Use while planning or finishing a user-visible change, to pick the proof (most changes need a screenshot or nothing), and when the user asks for screenshots, a before-and-after comparison, a video demo or a walkthrough.
---

# Feature walkthrough

Show a user-visible change with the cheapest proof that lets the reader check it. Most changes need a marked screenshot or nothing; few need a video.

## Choose the proof

Choose during planning, because a before-and-after pair needs its "before" shot taken before you edit. Change the choice if the work turns up a flow worth showing. When the user asks for a specific format, make that one. Honor the user's current and earlier preferences, including applicable `AGENTS.md` and `CLAUDE.md` instructions.

| What changed | Proof | Ask first? |
| --- | --- | --- |
| Nothing visible, such as a backend change, a refactor or config | A test or command output, as text. This skill adds nothing. | No |
| Output of a CLI or terminal command | The output, pasted as text. Record the terminal only when timing or interaction is the point. | No |
| New UI with no earlier version, such as a screen, a dialog or a control | One marked screenshot per screen | No |
| Changed UI that a still image shows, such as layout, style, copy, or an added or moved element | A marked before-and-after pair | No |
| A behavior across several steps or states, or a result easier to see than to describe | A short silent clip with captions | Ask once |
| A long flow, an animation or timing, or several tabs or apps | A video. Make it a comparison video when the old behavior matters. | Ask once |

- Take screenshots without asking; they cost seconds. A responsive change gets a shot for each width that changes, such as 390 and 1280 pixels. A theme change gets a shot for each theme. Otherwise take one shot per screen.
- Ask about a video once, with the other planning questions. Name what it would show, and offer written steps with screenshots as the alternative. Use a question tool permitted in the current mode. With an asynchronous question tool, continue implementation and verification while waiting. When nobody can answer, as in a non-interactive run, skip the video unless one was already requested.
- The answer holds for the whole task. After a decline, do not ask again or record anyway; the user can still request a video later.
- Narrate a video meant for a client, a release note, or anyone outside development. Keep a video that proves a PR silent, with captions. The user's choice overrides both.

Every proof ends with the written steps to try and the expected result. Continue with the section for the chosen format.

## Screenshots

1. For a pair, get the baseline first. Take the "before" shot before editing, or from a deployment or clean checkout at the base revision running on its own port, as in [advanced walkthroughs](references/advanced.md). Note the revision and URL of each shot. If no baseline is available, say so and take the "after" shot alone.
2. Use the same viewport, route, sample data and scroll position for both shots of a pair. Scroll the change into view.
3. In T3, evaluate the trimmed text of `scripts/annotate.js` in the page with `preview_evaluate`, as described in [advanced walkthroughs](references/advanced.md). Call `__walkthrough.still([{ selector, label }, ...])` with one item per change, up to 12. A short label such as "New: follow-up tiles" helps when the change is small. On a "before" shot, mark the element the change replaces, or the spot where it will appear. Take the screenshot with `preview_snapshot({ save: true })`, then call `__walkthrough.destroy()`.
4. Without T3, add `screenshot` steps to a `scripts/record_browser.py` scenario and leave out the video output, as described in [portable recording](references/portable.md). Find the script as in [Locate the installed helpers](#locate-the-installed-helpers).
5. Open each saved image. Every rectangle surrounds its change, and no label covers a change or another label.

Save the images under the project's ignored `artifacts/walkthrough/` directory, named by version and screen, such as `before-meetings.png` and `after-meetings.png`. In a client that renders local images, show them with `![After: meetings](/absolute/path/after-meetings.png)`; otherwise give the absolute paths. GitHub accepts PR images only through a browser upload, so in a PR body add a `Before merge` step that names the files to drag into the description. Keep the images out of source control unless the project asks for them.

Stop reading here unless a video was also chosen.

## Make the video

Create a short video of the actual workflow, with a small set of steps the viewer can try. Deliver an MP4 with readable app text, a visible title and compact captions, plus spoken narration when the choice above calls for it. Aim for 30–90 seconds per workflow; use shorter clips for simple changes. Explain what changed, why it helps, what to click, and what the viewer should see. Support claims with the demonstrated behavior.

For every narrated recording, read [spoken walkthroughs](references/narration.md) before planning scene lengths. A local Piper voice reads the same timed text used for captions without an API key. Captions remain useful with sound muted. If voice setup fails, report the failure explicitly with the available captioned clip.

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

3. For narrated output, run `scripts/narrate_video.py` with `--captions cues.json` and `--title "A concise walkthrough title"` on the edited clip, as shown in the narration guide. For a composition that already has source titles, preserve those headers and omit `--title`. This adds the caption footer once. For silent output, pass `--captions` and `--title` to `finish_video.py` instead.
4. Require the final export report to confirm portable MP4 and complete decoding, plus audible audio for narrated output. Inspect extracted frames at every key result and cue boundary. Titles must remain visible and captions must fit below the app. Check that app text stays readable at normal playback size.
5. Open the final MP4 in the available browser/player and verify playback advances, seeking works, and sound is present. Serve that same file with a download link, save a copy, and verify the copy plays. Report any unavailable playback or listening check. Deliver only after these checks pass or the remaining limitation is stated.

The helpers produce 8-bit H.264 video, AAC audio when present, and a finalized fast-start MP4. They preserve the input and require `--force` for an existing output. Deliver the final exported `.mp4`, using its actual path.

## When T3 preview tools are absent

Use an available browser integration with native video recording if it supports one. Otherwise, use `scripts/record_browser.py` as described in [portable recording](references/portable.md). It uses Playwright to record a real workflow, including the annotation helper, without an agent-specific MCP server. This is the normal path for Claude Code or Codex CLI without T3 preview tools. A navigation failure in an available T3 preview alone is not a reason to switch browser systems.

## Deliver the walkthrough

Save the final clip under the project's ignored `artifacts/walkthrough/` directory or another durable local artifact directory. In a client that supports local video embeds, use `![Feature walkthrough](/absolute/path/feature.mp4)`. In a terminal client such as Claude Code CLI, give the absolute path and a link supported by that client; do not claim an inline player exists. Keep the text to what changed, the version or URL demonstrated, and a few concrete actions with expected results. Mention any important unverified behavior. Keep binary recordings out of source control unless the project asks for them.

For comparison videos, several tabs, different web apps, terminal segments, or side-by-side playback, read [advanced walkthroughs](references/advanced.md). A composed browser/terminal video is assembled from separate recordings. Full desktop capture and native app switching require a separate desktop recorder and display access.

Sources: live T3 Code recording tool descriptions; [Playwright video recording](https://playwright.dev/python/docs/videos); [Claude Code skills](https://code.claude.com/docs/en/skills); [FFmpeg filters](https://www.ffmpeg.org/ffmpeg-filters.html); [asciinema recording](https://docs.asciinema.org/manual/cli/quick-start/).
