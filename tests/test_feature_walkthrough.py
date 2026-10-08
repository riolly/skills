# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["playwright==1.63.0", "imageio-ffmpeg==0.6.0"]
# ///
"""Integration checks: uv run --python 3.12 tests/test_feature_walkthrough.py."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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

    def cli(self, script, *arguments):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, arguments)],
                              capture_output=True, text=True)

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
        # Decode pixels from the video and verify the orange annotation was captured.
        frames = imageio_ffmpeg.read_frames(str(output), pix_fmt="rgb24")
        next(frames)
        found = False
        for frame in frames:
            pixels = memoryview(frame)
            orange = sum(pixels[i] > 220 and 60 < pixels[i+1] < 180 and pixels[i+2] < 80
                         for i in range(0, len(pixels), 30))
            if orange > 30:
                found = True
                break
        frames.close()
        self.assertTrue(found, "the recorded video did not contain an annotation")

    def test_failed_result_does_not_export_success_video(self):
        self.scenario["steps"] = [{"action": "assert-text", "selector": "#result",
                                    "text": "Saved successfully", "hold": 0}]
        output = self.work / "failure.webm"
        with self.assertRaises(AssertionError): recorder.record(self.scenario, output)
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


if __name__ == "__main__": unittest.main(verbosity=2)
