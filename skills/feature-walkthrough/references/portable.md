# Recording without T3

Use this path in Claude Code or Codex CLI when no native recording tool is available. Both agents can run the same Python helpers from their installed skill directory. A browser automation integration can help inspect controls; the recorder itself needs no MCP configuration or account.

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if absent. The helpers declare their Python dependencies inline. Python 3.12 is a suitable shared choice and `uv` can obtain it. For the browser recorder, download its pinned Chromium build:

```sh
PLAYWRIGHT_SKIP_BROWSER_GC=1 uv run --python 3.12 --with playwright==1.63.0 \
  python -m playwright install --only-shell chromium
```

The environment variable preserves browser builds used by other projects. This downloads the headless browser and its recording dependency, not system packages. If Playwright reports missing Linux libraries, use its [system dependency instructions](https://playwright.dev/python/docs/browsers#install-system-dependencies) according to the machine's permissions. Do not assume privileged package installation is available. `--headed` requires a desktop display and a full Chromium installation, obtained with `python -m playwright install chromium` using the same pinned package.

Narration has a separate one-time [voice download](narration.md). Terminal segments require [asciinema 3.x](https://docs.asciinema.org/manual/cli/installation/) and [agg](https://github.com/asciinema/agg#installation) on `PATH`. These are optional; a browser-only clip needs neither. Linux is tested; other supported platforms still need compatible browser, FFmpeg, and voice dependencies.

## Record actual actions

Start the correct app version on a reachable URL. Inspect the page with an available browser tool or Playwright, then choose unique observed CSS selectors. Save a scenario JSON such as:

```json
{
  "url": "http://localhost:3000/",
  "ready_selector": "#search",
  "steps": [
    {"action":"mark","selector":"#search","shape":"rectangle","gesture":"wiggle","label":"Search here","hold":3},
    {"action":"fill","selector":"#search","text":"React","hold":1},
    {"action":"assert-text","selector":"#results","text":"React","hold":1},
    {"action":"mark","selector":"#results","shape":"circle","gesture":"circle","label":"Check the result","hold":4}
  ]
}
```

These selectors are illustrative, not a claim about the target app. Assertions must express that app's actual expected result. The supported actions are `click`, `fill`, `press`, `scroll`, `assert-text`, `mark`, and `wait`. Every action except `wait` requires a `selector` with exactly one visible match; `fill`, `press`, and `assert-text` also require `text`. CSS is the usual choice, and any Playwright selector works for every action, including elements inside an open shadow root. For `press`, the text is a Playwright key such as `Enter`. `assert-text` waits for the locator to contain the text. Each step allows 15 seconds for its element to appear and for an asserted result. `scroll` brings the element into view, and `mark` does so before drawing. `wait` only holds the current scene. `hold` is seconds after an action, defaulting to 3 for marks and 1 otherwise, with a maximum of 30. Mark options match the [annotation helper](advanced.md).

```sh
uv run --python 3.12 "$WALKTHROUGH_SKILL_DIR"/scripts/record_browser.py \
  /absolute/path/scenario.json /absolute/path/artifacts/walkthrough/raw.webm
uv run "$WALKTHROUGH_SKILL_DIR"/scripts/finish_video.py \
  /absolute/path/artifacts/walkthrough/raw.webm \
  /absolute/path/artifacts/walkthrough/edited.mp4
```

The recorder creates a fresh 1920×1080 browser context with the same video dimensions, executes the real actions, and closes it to finalize the WebM. Set `"viewport":{"width":1600,"height":900}` in the scenario for different framing; capture size always matches it. It preserves saved data in the user's browser. It rejects ambiguous controls, HTTP errors, and failed assertions, and does not export a failed workflow as success. Existing output requires `--force`. Review the exported frames, trim initial loading or idle time with `finish_video.py`, and then add narration and captions. Reported action times are wall clock estimates, not authoritative video timestamps. Follow [export quality](quality.md) before delivery.

For login, pass `--storage-state /absolute/path/auth.json` only with an authorized existing Playwright storage-state file. Treat it as credentials and keep it out of recordings, source control, and installation archives. The recorder does not open the user's regular browser profile.

Record each app version to a separate clip, then use `compose_video.py` for labelled chapters or side-by-side playback. Add narration after composition. Refer to the [advanced guide](advanced.md) for manifests and terminal recordings. Browser capture omits the browser's tab bar, other apps, microphone, and native desktop; added narration supplies the audio track.

Sources: [Playwright recording](https://playwright.dev/python/docs/videos), [browser setup](https://playwright.dev/python/docs/browsers), and the linked uv, asciinema, and agg documentation.
