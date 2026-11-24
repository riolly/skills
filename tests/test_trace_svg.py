# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["pillow"]
# ///
"""Checks for trace-svg: uv run tests/test_trace_svg.py."""

import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from PIL import Image, ImageDraw

TRACE = Path(__file__).resolve().parents[1] / "skills/trace-svg/scripts/trace.py"
GROUND, LINE, GOLD, BLUE = "#e2d5b7", "#5a4420", "#d9a93f", "#2f4f77"


class TraceSvg(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="trace-svg-test-")
        self.folder = Path(self.temporary.name)
        picture = Image.new("RGB", (240, 160), GROUND)
        draw = ImageDraw.Draw(picture)
        draw.ellipse([20, 30, 110, 130], fill="#e0b048", outline=LINE, width=3)
        draw.rectangle([140, 40, 220, 120], fill="#35557c", outline=LINE, width=3)
        picture.save(self.folder / "picture.png")
        (self.folder / "groups.json").write_text(
            json.dumps({"left": [[0, 0], [125, 0], [125, 160], [0, 160]], "right": [[125, 0], [240, 0], [240, 160], [125, 160]]})
        )

    def tearDown(self):
        self.temporary.cleanup()

    def trace(self, *options):
        out = self.folder / "out.svg"
        run = subprocess.run(
            [str(TRACE), str(self.folder / "picture.png"), str(out), "--paint", f"{GOLD},{BLUE}", "--ground", GROUND, "--line", LINE, "--colours", "4", *options],
            capture_output=True,
            text=True,
        )
        return run, out

    def test_paints_each_group_in_the_palette_and_leaves_the_ground_empty(self):
        run, out = self.trace("--groups", str(self.folder / "groups.json"), "--group-attr", "data-seal")
        self.assertEqual(run.returncode, 0, run.stderr)
        svg = out.read_text()
        left, right = re.findall(r'<g data-seal="(?:left|right)">.*?</g></g>', svg)
        self.assertIn(GOLD.upper(), left.upper())
        self.assertNotIn(BLUE.upper(), left.upper())
        self.assertIn(BLUE.upper(), right.upper())
        self.assertNotIn(GROUND.upper(), svg.upper())
        self.assertRegex(left, rf'data-layer="line" fill="{LINE}"><path')
        self.assertTrue(Path(f"{out}.palette.png").exists())

    def test_refuses_a_correction_for_a_colour_the_run_did_not_find(self):
        run, _ = self.trace("--map", f"#00ff00={GOLD}")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("found no colour #00ff00", run.stderr)


if __name__ == "__main__":
    unittest.main()
