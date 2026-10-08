#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["playwright==1.63.0"]
# ///
"""Record a real browser workflow when the agent has no native recorder."""

import argparse
import json
import math
from pathlib import Path
import tempfile
import time

from playwright.sync_api import sync_playwright, expect, Error as PlaywrightError

TIMEOUT = 15000  # milliseconds, for actions and assertions alike


def validate(scenario):
    if not isinstance(scenario, dict) or not isinstance(scenario.get("url"), str):
        raise ValueError("scenario needs a url and steps")
    if not scenario["url"].startswith(("http://", "https://", "file://")):
        raise ValueError("url must use http, https, or file")
    viewport = scenario.get("viewport", {"width": 1920, "height": 1080})
    if (not isinstance(viewport, dict) or set(viewport) != {"width", "height"}
            or not all(isinstance(n, int) and not isinstance(n, bool) and 320 <= n <= 3840
                       for n in viewport.values())):
        raise ValueError("viewport needs integer width and height between 320 and 3840")
    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps: raise ValueError("steps must be a nonempty array")
    actions = {"click", "fill", "press", "mark", "wait", "assert-text", "scroll"}
    for step in steps:
        if not isinstance(step, dict) or step.get("action") not in actions:
            raise ValueError(f"unknown step action; choose from {sorted(actions)}")
        action = step["action"]
        if action != "wait" and (not isinstance(step.get("selector"), str) or not step["selector"].strip()):
            raise ValueError(f"{action} needs a selector")
        if action in {"fill", "press", "assert-text"} and not isinstance(step.get("text"), str):
            raise ValueError(f"{action} needs text")
        hold = float(step.get("hold", 3 if action == "mark" else 1))
        if not math.isfinite(hold) or not 0 <= hold <= 30: raise ValueError("hold must be 0–30 seconds")


def record(scenario, output, headed=False, storage_state=None):
    validate(scenario)
    report = []
    viewport = scenario.get("viewport", {"width": 1920, "height": 1080})
    annotate = Path(__file__).with_name("annotate.js").read_text(encoding="utf-8").strip()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-recording-", dir=output.parent) as temporary:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed)
            context = browser.new_context(viewport=viewport,
                                          record_video_size=viewport,
                                          record_video_dir=temporary,
                                          storage_state=str(storage_state) if storage_state else None)
            context.set_default_timeout(TIMEOUT)
            # Assertions have their own, shorter default, and they gate every step.
            expect.set_options(timeout=TIMEOUT)
            page = context.new_page()
            video = page.video
            started = time.monotonic()
            completed = False
            try:
                response = page.goto(scenario["url"], wait_until="domcontentloaded")
                if response and response.status >= 400:
                    raise ValueError(f"app returned HTTP {response.status}")
                if scenario.get("ready_selector"):
                    page.locator(scenario["ready_selector"]).wait_for(state="visible")
                for i, step in enumerate(scenario["steps"]):
                    action = step["action"]
                    locator = page.locator(step["selector"]) if action != "wait" else None
                    if locator is not None:
                        expect(locator).to_have_count(1)
                        expect(locator).to_be_visible()
                    report.append({"step": i + 1, "action": action,
                                   "elapsed_seconds": round(time.monotonic() - started, 2)})
                    if action == "click": locator.click()
                    elif action == "fill": locator.fill(step["text"])
                    elif action == "press": locator.press(step["text"])
                    elif action == "scroll": locator.scroll_into_view_if_needed()
                    elif action == "assert-text": expect(locator).to_contain_text(step["text"])
                    elif action == "mark":
                        hold = float(step.get("hold", 3))
                        page.evaluate(annotate)
                        options = {key: step[key] for key in ("selector", "shape", "gesture", "label", "color", "padding") if key in step}
                        options["duration"] = min(15000, max(100, round(hold * 1000)))
                        # Mark the element Playwright resolved, which may be below the fold or in a shadow root.
                        locator.scroll_into_view_if_needed()
                        locator.evaluate("(target, options) => window.__walkthrough.mark({...options, target})", options)
                    page.wait_for_timeout(float(step.get("hold", 3 if action == "mark" else 1)) * 1000)
                page.evaluate("() => window.__walkthrough?.destroy()")
                completed = True
            finally:
                # Both contexts and browser close on failure; a failed workflow is not exported as success.
                try:
                    context.close()
                    if completed: video.save_as(str(output))
                finally: browser.close()
    return {"path": str(output), "url": scenario["url"], "viewport": [viewport["width"], viewport["height"]],
            "steps": report, "timing": "wall clock estimates; verify against exported frames",
            "audio": "silent; add narration after editing"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="JSON url/ready_selector/steps object")
    parser.add_argument("output", type=Path, help="raw .webm recording")
    parser.add_argument("--headed", action="store_true", help="show browser; requires a desktop display")
    parser.add_argument("--storage-state", type=Path, help="optional existing Playwright auth state; never committed")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.suffix.lower() != ".webm": parser.error("output must have a .webm extension")
    if output.exists() and not args.force: parser.error("output exists; choose another path or pass --force")
    if args.scenario.resolve() == output: parser.error("output must not replace the scenario")
    if args.storage_state and args.storage_state.resolve() == output:
        parser.error("output must not replace authentication state")
    try:
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        validate(scenario)
        # Publish only a complete recording. Do not leave a partial success artifact on error.
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="workflow-", dir=output.parent) as temporary:
            result = Path(temporary) / "recording.webm"
            report = record(scenario, result, args.headed, args.storage_state)
            if output.exists() and not args.force: raise ValueError("output appeared while recording")
            result.replace(output)
        report["path"] = str(output)
        print(json.dumps(report, indent=2))
    except (ValueError, TypeError, KeyError, OSError, PlaywrightError, AssertionError) as error:
        parser.exit(1, f"Browser recording failed: {error}\n")


if __name__ == "__main__": main()
