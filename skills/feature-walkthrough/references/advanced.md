# Advanced walkthroughs

## Before and after, several tabs, or different web apps

In T3, open the existing app and the changed version in separate preview tabs with `preview_open({reuseExistingTab:false})`. Preserve both returned IDs and use explicit `tabId` for every action. Each recorder exports only its own tab's content, without the browser's tab bar or OS app switching. Without T3, record each version using a separate scenario with `record_browser.py`, as described in [portable recording](portable.md), then compose the clips below. Two sequential recordings are sufficient; simultaneous recording is optional.

For an actual change comparison, record a known baseline before editing, use an existing deployment at the baseline revision, or build the baseline from a separate clean checkout. Run the new worktree on its own port. Record the revision and URL for each. Do not call arbitrary production and local versions "before" and "after" without checking their revisions. If the baseline cannot be obtained, say so and demonstrate the new behavior alone.

Use matching viewport sizes, sample data, routes, and actions. Different ports isolate local storage. Avoid clearing a user's stored data to align the comparison. Record each tab with its own start/stop calls. If recording several tabs, stop every started recorder even after an action fails. Preserve every returned recording path.

Use `scripts/compose_video.py` to make labelled chapters or a side-by-side comparison. Sequential chapters are easier to read on a phone. Each app has a 1920×1080 stage and a separate title header; side-by-side output is 3840 pixels wide. It supports exactly two clips and ends with the shorter trimmed clip; align the key action or result with each clip's `start`. Matching playback time does not prove the original actions happened simultaneously.

Write a JSON manifest. Paths may be absolute or relative to the manifest file:

```json
[
  {"path":"before.mp4","label":"Before: baseline revision abc123","start":0,"duration":20},
  {"path":"after.mp4","label":"After: current worktree","start":0,"duration":20}
]
```

```sh
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/compose_video.py \
  /absolute/path/clips.json /absolute/path/comparison.mp4 --layout side-by-side
```

Use `--layout sequence` for one clip after another, including more than two clips or different web apps. Add narration and matching captions after composition, preserving its existing title headers. For silent output, optional `--captions captions.json` uses the same start/end/text schema as `finish_video.py`, timed relative to the combined output. Caption text and its compact band scale with output width. Composition produces silent MP4, even when an input has audio; preserve source clips if narration matters. Existing output requires `--force`. Follow [export quality](quality.md) for GPU selection and final playback checks.

## Circles, rectangles and pointer gestures

Read `scripts/annotate.js` and evaluate its **trimmed text** in the selected tab with `preview_evaluate`, or the current browser integration's equivalent. T3 rejects leading/trailing whitespace. The portable recorder installs it automatically for a `mark` step. This installs `window.__walkthrough`, a temporary SVG overlay inside a shadow root. It does not click, type, send pointer events, or change the app's saved state. The overlay does not accept mouse events. Each mark places it in the browser's top layer, so it draws above an open modal dialog, popover, or fullscreen element. It is built without inline markup or style elements, so it also works on pages with Trusted Types or a strict style policy. Use observed CSS selectors with exactly one visible match, and scroll the target into the viewport before marking it.

```js
window.__walkthrough.mark({
  selector: 'input[aria-label="Search questions"]',
  shape: 'rectangle',
  gesture: 'wiggle',
  label: 'Search here',
  duration: 3500
})
```

- `shape` accepts `rectangle`, `circle`, or `none`. The circle fits the target bounds as an ellipse. Shapes draw themselves over the first half second.
- `gesture` accepts `wiggle`, `circle`, or `none`. Wiggle draws a moving pointer at the target; circle orbits the pointer around it. These are visual annotations, not actual OS cursor movement.
- `label` uses plain text. Optional `color` accepts a CSS color and `padding` adds 0–64 pixels around the target.
- `target` accepts an element in place of `selector`, for one that CSS cannot reach from the document, such as an element inside a shadow root.
- `duration` accepts 100–15000 milliseconds, then clears the mark. Only one active mark is shown. `status()` reports the current mark.

Marks follow the target's rendered position during scroll or resize. Reinspect and remark when a route change replaces the target. Full navigation requires installing the helper again. Background tabs can pause animation frames, so gesture clips should be checked in the exported video. Slow orbit gestures and a persistent shape survive low capture frame rates better than a fast wiggle.

For a clean demonstration, mark the target before clicking, wait for the gesture, use the real browser click tool, then mark the result. Avoid covering another necessary control with a label. Use `clear()` between steps and `destroy()` at the end. The helpers return confirmation objects so evaluation can verify cleanup. Do not include annotation styles in the application's source or portray them as shipped UI.

## Terminal segments

Terminal capture requires `asciinema` 3.x and `agg` on `PATH`; tested versions are 3.2.1 and 1.9.0. They capture a terminal's actual output and render it for replay. This is a recording of an isolated pseudo-terminal, not a screen capture of the user's terminal window. Installation links are in [portable recording](portable.md). Do not assume they are already installed.

Use `scripts/record_terminal.py` with a JSON list of explicitly intended commands, as argv arrays:

```json
[
  {"command":["node","--version"],"pause":2},
  {"command":["pnpm","test","--run"],"pause":3}
]
```

```sh
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/record_terminal.py \
  /absolute/path/steps.json /absolute/path/terminal.mp4
```

The helper prints the exact command, executes it, holds its result briefly, and stops on the first command failure. A command that cannot start, such as one missing from `PATH`, is recorded as a failed step with status 127. It records locally with asciinema's `--headless --return`, renders with `agg`, and exports through the MP4 helper. It prints one JSON report and exits with the failing command's status. Keep the `.cast` recording for replay with `asciinema play`. It also keeps an intermediate GIF. The cast, GIF, and MP4 appear together; a failed export leaves none of them. Nothing is uploaded. Run from the intended working directory. Only execute commands already within the user's task authorization; do not substitute success messages for failed output or silently rerun costly actions just for a video.

Optional `--captions` adds captions timed to the final rendered clip. Idle time is preserved up to 30 seconds, and the last frame holds for two seconds. `--force` replaces existing output files. Avoid credentials in recorded commands or output. Combine the terminal MP4 with browser clips using the same composition manifest.

Arbitrary native apps and one uninterrupted video of OS app switching still need a desktop recorder and access to the relevant display. Those are not provided by these helpers.

Sources: [FFmpeg stacking and concatenation](https://www.ffmpeg.org/ffmpeg-filters.html), [shadow roots](https://developer.mozilla.org/en-US/docs/Web/API/Element/attachShadow), [animation frame behavior](https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame), [asciinema](https://docs.asciinema.org/manual/cli/quick-start/), and [agg](https://github.com/asciinema/agg).
