#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["playwright==1.63.0"]
# ///
"""Record a real browser workflow, or take marked screenshots, when the agent has no native browser tools."""

import argparse
import json
import math
import shutil
from pathlib import Path
import tempfile
import time

from playwright.sync_api import sync_playwright, expect, Error as PlaywrightError

TIMEOUT = 15000  # milliseconds, for actions and assertions alike
MARK_KEYS = {"selector", "shape", "label", "color", "padding"}


def default_hold(action):
    return 3 if action == "mark" else 0 if action == "screenshot" else 1


def screenshot_paths(scenario):
    return [Path(step["path"]).resolve() for step in scenario["steps"] if step["action"] == "screenshot"]


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
    actions = {"click", "fill", "press", "mark", "wait", "assert-text", "scroll", "screenshot"}
    for step in steps:
        if not isinstance(step, dict) or step.get("action") not in actions:
            raise ValueError(f"unknown step action; choose from {sorted(actions)}")
        action = step["action"]
        if action not in {"wait", "screenshot"} and (not isinstance(step.get("selector"), str) or not step["selector"].strip()):
            raise ValueError(f"{action} needs a selector")
        if action in {"fill", "press", "assert-text"} and not isinstance(step.get("text"), str):
            raise ValueError(f"{action} needs text")
        if action == "screenshot":
            if not isinstance(step.get("path"), str) or not step["path"].lower().endswith(".png"):
                raise ValueError("screenshot needs a .png path")
            marks = step.get("marks", [])
            if (not isinstance(marks, list) or len(marks) > 12
                    or not all(isinstance(m, dict) and isinstance(m.get("selector"), str) and m["selector"].strip()
                               and set(m) <= MARK_KEYS for m in marks)):
                raise ValueError(f"screenshot marks must be 0–12 objects with a selector and only {sorted(MARK_KEYS)}")
        hold = float(step.get("hold", default_hold(action)))
        if not math.isfinite(hold) or not 0 <= hold <= 30: raise ValueError("hold must be 0–30 seconds")
    shots = screenshot_paths(scenario)
    if len(set(shots)) != len(shots): raise ValueError("each screenshot needs its own path")


def record(scenario, output=None, headed=False, storage_state=None):
    """Run the steps. Without an output path, record no video and only take the screenshots."""
    validate(scenario)
    shots = screenshot_paths(scenario)
    if output is None and not shots: raise ValueError("nothing to save; pass a video output or add a screenshot step")
    report, taken = [], []
    viewport = scenario.get("viewport", {"width": 1920, "height": 1080})
    annotate = Path(__file__).with_name("annotate.js").read_text(encoding="utf-8").strip()
    for path in [output, *shots]:
        if path is not None: path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="browser-recording-", dir=(output or shots[0]).parent) as temporary:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed)
            video_options = {"record_video_size": viewport, "record_video_dir": temporary} if output else {}
            context = browser.new_context(viewport=viewport, **video_options,
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
                    locator = page.locator(step["selector"]) if "selector" in step else None
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
                    elif action == "screenshot":
                        page.evaluate(annotate)
                        marks, targets = step.get("marks", []), []
                        for mark in marks:
                            target = page.locator(mark["selector"])
                            expect(target).to_have_count(1)
                            expect(target).to_be_visible()
                            targets.append(target.element_handle())
                        if marks:
                            # Pass the elements Playwright resolved, so shadow-root selectors work here too.
                            page.evaluate("([marks, targets]) => window.__walkthrough.still("
                                          "marks.map(({selector, ...rest}, i) => ({...rest, target: targets[i]})))",
                                          [marks, targets])
                        shot = Path(temporary) / f"screenshot-{len(taken)}.png"
                        page.screenshot(path=str(shot))
                        page.evaluate("() => window.__walkthrough.clear()")
                        taken.append(shot)
                    page.wait_for_timeout(float(step.get("hold", default_hold(action))) * 1000)
                page.evaluate("() => window.__walkthrough?.destroy()")
                completed = True
            finally:
                # Both contexts and browser close on failure; a failed workflow is not exported as success.
                try:
                    context.close()
                    if completed and output: video.save_as(str(output))
                finally: browser.close()
        # Screenshots appear only after every step passed, like the video.
        for shot, path in zip(taken, shots): shutil.move(shot, path)
    result = {"path": str(output) if output else None, "screenshots": [str(path) for path in shots],
              "url": scenario["url"], "viewport": [viewport["width"], viewport["height"]], "steps": report}
    if output:
        result.update(timing="wall clock estimates; verify against exported frames",
                      audio="silent; add narration after editing")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="JSON url/ready_selector/steps object")
    parser.add_argument("output", type=Path, nargs="?", help="raw .webm recording; omit to take only screenshots")
    parser.add_argument("--headed", action="store_true", help="show browser; requires a desktop display")
    parser.add_argument("--storage-state", type=Path, help="optional existing Playwright auth state; never committed")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve() if args.output else None
    if output and output.suffix.lower() != ".webm": parser.error("output must have a .webm extension")
    try:
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        validate(scenario)
        protected = [args.scenario.resolve(), *([args.storage_state.resolve()] if args.storage_state else [])]
        for path in [output, *screenshot_paths(scenario)]:
            if path is None: continue
            if path in protected: parser.error("an output must not replace the scenario or authentication state")
            if path.exists() and not args.force: parser.error(f"{path} exists; choose another path or pass --force")
        if output is None:
            print(json.dumps(record(scenario, None, args.headed, args.storage_state), indent=2))
            return
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
