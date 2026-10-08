# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["playwright==1.63.0", "imageio-ffmpeg==0.6.0"]
# ///
"""Integration checks: uv run --python 3.12 tests/test_feature_walkthrough.py."""

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import imageio_ffmpeg

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/feature-walkthrough/scripts"
spec = importlib.util.spec_from_file_location("record_browser", SCRIPTS / "record_browser.py")
recorder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recorder)


class WalkthroughIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="walkthrough-test-")
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        page = self.work / "app.html"
        page.write_text('''<!doctype html><meta charset="utf-8"><title>Walkthrough test fixture</title>
<style>body{font:28px sans-serif;padding:80px;background:#f5f7fa}button{font:inherit;padding:20px}</style>
<h1>Portable recorder test fixture</h1>
<button id="apply" onclick="document.querySelector('#result').textContent='Saved successfully'">Apply change</button>
<p id="result">Waiting for your action</p>''')
        self.scenario = {"url": page.as_uri(), "ready_selector": "#apply", "steps": [
            {"action": "mark", "selector": "#apply", "shape": "circle", "gesture": "circle", "hold": 0.8},
            {"action": "click", "selector": "#apply", "hold": 0.1},
            {"action": "assert-text", "selector": "#result", "text": "Saved successfully", "hold": 0.1},
            {"action": "mark", "selector": "#result", "shape": "rectangle", "gesture": "wiggle", "hold": 0.8},
        ]}

    def cli(self, script, *arguments, env=None):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, arguments)],
                              capture_output=True, text=True, env=env)

    def page(self, body):
        page = self.work / "page.html"
        page.write_text('<!doctype html><meta charset="utf-8">' + body, encoding="utf-8")
        return page.as_uri()

    def clip(self, name, *options, streamed=False):
        # Generated footage is plain gray, so white or orange pixels come from the helpers.
        # Writing through a pipe leaves the container without a duration header.
        result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                                 "-f", "lavfi", "-i", "color=c=0x808080:s=640x400:d=1", *options,
                                 "-" if streamed else str(self.work / name)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        if streamed: (self.work / name).write_bytes(result.stdout)
        return self.work / name

    def shows(self, path, matches, rows=None):
        """Decode the video and report whether a frame has enough sampled pixels of a colour."""
        frames = imageio_ffmpeg.read_frames(str(path), pix_fmt="rgb24")
        width = next(frames)["size"][0]
        try:
            for frame in frames:
                pixels = memoryview(frame)[:rows * width * 3 if rows else None]
                if sum(matches(*pixels[i:i+3]) for i in range(0, len(pixels), 30)) > 30: return True
            return False
        finally: frames.close()

    orange = staticmethod(lambda r, g, b: r > 220 and 60 < g < 180 and b < 80)
    navy = staticmethod(lambda r, g, b: r < 45 and 15 < g < 55 and 30 < b < 75)
    white = staticmethod(lambda r, g, b: min(r, g, b) > 200)

    def metadata(self, path):
        frames = imageio_ffmpeg.read_frames(str(path))
        try: return next(frames)
        finally: frames.close()

    def test_real_actions_annotations_and_mp4_conversion(self):
        raw = self.work / "raw.webm"
        report = recorder.record(self.scenario, raw)
        self.assertEqual(len(report["steps"]), 4)
        self.assertEqual(self.metadata(raw)["size"], (1280, 800))
        output = self.work / "final.mp4"
        result = self.cli("finish_video.py", raw, output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["decode_verified"])
        self.assertEqual(self.metadata(output)["codec"], "h264")
        self.assertTrue(self.shows(output, self.orange), "the recorded video did not contain an annotation")

    def test_failed_result_does_not_export_success_video(self):
        self.scenario["steps"] = [{"action": "assert-text", "selector": "#result",
                                    "text": "Saved successfully", "hold": 0}]
        output = self.work / "failure.webm"
        with mock.patch.object(recorder, "TIMEOUT", 1000), self.assertRaises(AssertionError):
            recorder.record(self.scenario, output)
        self.assertFalse(output.exists())

    def test_invalid_scenario_is_rejected_before_recording(self):
        self.scenario["steps"] = [{"action": "invent-success", "hold": 0}]
        with self.assertRaises(ValueError): recorder.record(self.scenario, self.work / "invalid.webm")
        self.assertFalse((self.work / "invalid.webm").exists())

    def test_existing_output_is_not_replaced(self):
        output = self.work / "keep.webm"
        output.write_bytes(b"existing recording")
        scenario = self.work / "scenario.json"
        scenario.write_text(json.dumps(self.scenario))
        result = self.cli("record_browser.py", scenario, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), b"existing recording")

    def test_authentication_state_is_never_replaced_even_with_force(self):
        auth = self.work / "auth.webm"
        auth.write_text('{"cookies":[],"origins":[]}')
        scenario = self.work / "scenario.json"
        scenario.write_text(json.dumps(self.scenario))
        result = self.cli("record_browser.py", scenario, auth, "--storage-state", auth, "--force")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(auth.read_text(), '{"cookies":[],"origins":[]}')

    def test_marks_are_drawn_above_a_modal_dialog(self):
        url = self.page('<button id="open" onclick="document.querySelector(\'dialog\').showModal()">Open</button>'
                        '<dialog><button id="confirm">Confirm</button></dialog>')
        raw = self.work / "dialog.webm"
        recorder.record({"url": url, "steps": [
            {"action": "click", "selector": "#open", "hold": 0.1},
            {"action": "mark", "selector": "#confirm", "label": "Confirm here", "hold": 0.8}]}, raw)
        self.assertTrue(self.shows(raw, self.orange), "the outline was hidden behind the dialog")
        self.assertTrue(self.shows(raw, self.navy), "the label was hidden behind the dialog")

    def test_marks_work_under_a_strict_content_security_policy(self):
        url = self.page('<meta http-equiv="Content-Security-Policy" content="'
                        "require-trusted-types-for 'script'; style-src 'self'\">"
                        '<button id="apply">Apply change</button>')
        raw = self.work / "strict.webm"
        recorder.record({"url": url, "steps": [
            {"action": "mark", "selector": "#apply", "label": "Apply here", "hold": 0.8}]}, raw)
        self.assertTrue(self.shows(raw, self.orange), "the outline was not drawn")
        self.assertTrue(self.shows(raw, self.navy), "the label lost its styles")

    def test_marks_accept_any_target_the_recorder_can_act_on(self):
        url = self.page('<h1>Top</h1><div><template shadowrootmode="open"><button id="inner">Inside</button>'
                        '</template></div><p id="low" style="margin-top:2000px">Below the fold</p>')
        report = recorder.record({"url": url, "steps": [
            {"action": "mark", "selector": selector, "hold": 0.1}
            for selector in ("text=Top", "#inner", "#low")]}, self.work / "targets.webm")
        self.assertEqual(len(report["steps"]), 3)

    def test_results_slower_than_five_seconds_are_awaited(self):
        url = self.page('<button id="apply" onclick="setTimeout(() => result.textContent = \'Saved\', 6000)">'
                        'Apply</button><p id="result">Waiting</p>')
        report = recorder.record({"url": url, "steps": [
            {"action": "click", "selector": "#apply", "hold": 0},
            {"action": "assert-text", "selector": "#result", "text": "Saved", "hold": 0}]}, self.work / "slow.webm")
        self.assertEqual(len(report["steps"]), 2)

    def test_streamed_recording_without_a_duration_header_is_exported(self):
        # H.264 reorders frames, so the measured duration must come from decoding, not packet times.
        for name, options in (("stream.webm", ("-c:v", "libvpx", "-f", "webm")), ("stream.mkv", ("-f", "matroska"))):
            source = self.clip(name, *options, streamed=True)
            self.assertEqual(self.metadata(source)["duration"], 0)
            result = self.cli("finish_video.py", source, self.work / f"{name}.mp4")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertAlmostEqual(json.loads(result.stdout)["duration_seconds"], 1, delta=0.02)

    def compose(self, label, *arguments, env=None):
        manifest = self.work / "clips.json"
        manifest.write_text(json.dumps([{"path": str(self.clip(f"{name}.mp4")), "label": label}
                                        for name in ("before", "after")], ensure_ascii=False), encoding="utf-8")
        output = self.work / "comparison.mp4"
        result = self.cli("compose_video.py", manifest, output, *arguments, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return output, json.loads(result.stdout)

    def test_wide_composition_scales_captions_and_keeps_titles_in_the_header(self):
        captions = self.work / "captions.json"
        captions.write_text(json.dumps([{"start": 0, "end": 1, "text": "Both versions"}]))
        output, report = self.compose("Baseline", "--layout", "side-by-side", "--captions", captions)
        # A 2560-pixel frame needs twice the caption band of a 1280-pixel one.
        self.assertEqual((report["width"], report["height"]), (2560, 852 + 224))
        self.assertTrue(self.shows(output, self.white, rows=52), "clip titles are missing from the header")

    def test_labels_are_read_as_utf8_in_any_locale(self):
        env = {**os.environ, "LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}
        self.compose("Before: “old” Ánimo", env=env)

    terminal = unittest.skipUnless(shutil.which("asciinema") and shutil.which("agg"),
                                   "terminal capture needs asciinema and agg")

    @terminal
    def test_terminal_recording_shows_a_missing_command_as_a_failure(self):
        steps = self.work / "steps.json"
        steps.write_text(json.dumps([{"command": ["echo", "ready"], "pause": 0.2},
                                     {"command": ["definitely-not-a-command"], "pause": 0.2}]))
        output = self.work / "terminal.mp4"
        result = self.cli("record_terminal.py", steps, output)
        self.assertEqual(result.returncode, 127, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["decode_verified"])
        self.assertEqual(report["command_exit_code"], 127)
        cast = Path(report["terminal_cast"]).read_text(encoding="utf-8")
        self.assertIn("Command exited with status 127", cast)
        self.assertNotIn("Traceback", cast)

    @terminal
    def test_failed_terminal_export_reports_once_and_leaves_no_outputs(self):
        steps, captions = self.work / "steps.json", self.work / "captions.json"
        steps.write_text(json.dumps([{"command": ["echo", "ready"], "pause": 0.2}]))
        captions.write_text("[]")
        output = self.work / "terminal.mp4"
        result = self.cli("record_terminal.py", steps, output, "--captions", captions)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Terminal recording failed", result.stderr)
        self.assertEqual([p.name for p in self.work.glob("terminal.*")], [])


if __name__ == "__main__": unittest.main(verbosity=2)
