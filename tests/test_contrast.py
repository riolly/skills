"""Contrast checks: python3 tests/test_contrast.py."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/designing-ui/scripts/contrast.py"
spec = importlib.util.spec_from_file_location("contrast", SCRIPT)
contrast = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contrast)

WHITE = "oklch(1 0 0)"
DESTRUCTIVE = "oklch(0.577 0.245 27.325)"


class Ratios(unittest.TestCase):
    def test_extremes(self):
        self.assertAlmostEqual(contrast.ratio("#000", "#fff"), 21, places=2)
        self.assertAlmostEqual(contrast.ratio("#fff", "#fff"), 1, places=2)

    def test_every_format_reads_the_same_red(self):
        for text in ("#ff0000", "#f00", "rgb(255 0 0)", "rgb(255, 0, 0)", "rgba(100%, 0%, 0%, 1)", "hsl(0 100% 50%)", "hsl(0deg, 100%, 50%)"):
            self.assertAlmostEqual(contrast.ratio(text, "#fff"), 4.0, places=2, msg=text)

    def test_shadcn_neutral_theme(self):
        cases = [
            ("input border", 1.26, ("oklch(0.922 0 0)", WHITE)),
            ("focus ring", 2.59, ("oklch(0.708 0 0)", WHITE)),
            ("muted text on muted", 4.34, ("oklch(0.556 0 0)", "oklch(0.97 0 0)")),
            ("dark input border", 1.47, ("oklch(1 0 0 / 15%)", "oklch(0.145 0 0)")),
            ("destructive tint", 3.99, (DESTRUCTIVE, "oklch(0.577 0.245 27.325 / 10%)", WHITE)),
        ]
        for name, expected, colours in cases:
            self.assertAlmostEqual(contrast.ratio(*colours), expected, places=2, msg=name)

    def test_chroma_percent_scales_to_point_four(self):
        self.assertAlmostEqual(
            contrast.ratio("oklch(50% 50% 30)", WHITE),
            contrast.ratio("oklch(0.5 0.2 30)", WHITE),
            places=6,
        )

    def test_translucent_foreground_blends_before_measuring(self):
        self.assertAlmostEqual(contrast.ratio("rgb(0 0 0 / 50%)", "#fff"), contrast.ratio("#808080", "#fff"), places=1)

    def test_rejects_a_translucent_final_layer(self):
        with self.assertRaises(ValueError):
            contrast.ratio("#000", "rgb(255 255 255 / 50%)")


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_min_sets_the_exit_code(self):
        self.assertEqual(self.run_script("#000", "#fff", "--min", "4.5").returncode, 0)
        self.assertEqual(self.run_script("#eee", "#fff", "--min", "3").returncode, 1)

    def test_token_name_is_an_error(self):
        result = self.run_script("var(--primary)", "#fff")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported colour", result.stderr)


if __name__ == "__main__":
    unittest.main()
