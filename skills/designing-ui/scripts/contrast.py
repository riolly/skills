#!/usr/bin/env python3
"""Measure the WCAG contrast ratio between two colours, standard library only.

usage: contrast.py FOREGROUND BACKGROUND [BACKDROP ...] [--min RATIO]

Pass final values, not token names. Colours are hex, rgb(), hsl() or oklch(),
each with optional alpha: "oklch(1 0 0 / 15%)". A translucent colour needs what
sits behind it, so list the layers from top to bottom after FOREGROUND. Text in
a 10% tint on the page is: FOREGROUND "TINT" PAGE.

Exit code 1 means the ratio is below --min; 2 means a colour failed to parse.
"""

import argparse
import colorsys
import math
import re
import sys

Colour = tuple[float, float, float, float]  # gamma-encoded sRGB plus alpha, 0 to 1


def clamp(value: float) -> float:
    return min(1.0, max(0.0, value))


def encode(channel: float) -> float:
    channel = clamp(channel)
    if channel <= 0.0031308:
        return 12.92 * channel
    return 1.055 * channel ** (1 / 2.4) - 0.055


def decode(channel: float) -> float:
    if channel <= 0.04045:
        return channel / 12.92
    return ((channel + 0.055) / 1.055) ** 2.4


def oklch_to_srgb(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    long = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    medium = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    short = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (
        encode(4.0767416621 * long - 3.3077115913 * medium + 0.2309699292 * short),
        encode(-1.2684380046 * long + 2.6097574011 * medium - 0.3413193965 * short),
        encode(-0.0041960863 * long - 0.7034186147 * medium + 1.7076147010 * short),
    )


def number(text: str, percent_of: float = 1.0) -> float:
    if text == "none":
        return 0.0
    if text.endswith("%"):
        return float(text[:-1]) / 100 * percent_of
    return float(text)


def parse(text: str) -> Colour:
    value = text.strip().lower()
    hex_match = re.fullmatch(r"#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})", value)
    if hex_match:
        digits = hex_match[1]
        if len(digits) <= 4:
            digits = "".join(digit * 2 for digit in digits)
        parts = [int(digits[index : index + 2], 16) / 255 for index in range(0, len(digits), 2)]
        return (parts[0], parts[1], parts[2], parts[3] if len(parts) == 4 else 1.0)

    function = re.fullmatch(r"(oklch|rgba?|hsla?)\((.*)\)", value)
    if not function:
        raise ValueError(f"unsupported colour: {text}")
    name, body = function[1], function[2]
    parts = [part for part in re.split(r"[\s,/]+", body.strip()) if part]
    if len(parts) not in (3, 4):
        raise ValueError(f"unsupported colour: {text}")
    alpha = clamp(number(parts[3])) if len(parts) == 4 else 1.0

    if name == "oklch":
        rgb = oklch_to_srgb(number(parts[0]), number(parts[1], 0.4), number(parts[2].removesuffix("deg")))
    elif name.startswith("rgb"):
        rgb = tuple(clamp(number(part, 255) / 255) for part in parts[:3])
    else:
        hue = number(parts[0].removesuffix("deg")) / 360 % 1
        rgb = colorsys.hls_to_rgb(hue, clamp(number(parts[2])), clamp(number(parts[1])))
    return (*rgb, alpha)


def flatten(layers: list[Colour]) -> Colour:
    """Composite layers, top first, in gamma-encoded sRGB as browsers do."""
    result = layers[-1]
    for layer in reversed(layers[:-1]):
        alpha = layer[3]
        result = (
            alpha * layer[0] + (1 - alpha) * result[0],
            alpha * layer[1] + (1 - alpha) * result[1],
            alpha * layer[2] + (1 - alpha) * result[2],
            alpha + (1 - alpha) * result[3],
        )
    return result


def luminance(colour: Colour) -> float:
    return 0.2126 * decode(colour[0]) + 0.7152 * decode(colour[1]) + 0.0722 * decode(colour[2])


def ratio(foreground: str, *background: str) -> float:
    """Ratio of foreground over a stack of layers, top first."""
    back = flatten([parse(layer) for layer in background])
    if back[3] < 0.999:
        raise ValueError("the last background layer must be opaque; add what sits behind it")
    front = flatten([parse(foreground), back])
    lighter, darker = sorted((luminance(front), luminance(back)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure the WCAG contrast ratio between two colours.",
        epilog="List translucent backgrounds top first, ending on an opaque colour.",
    )
    parser.add_argument("foreground")
    parser.add_argument("background", nargs="+")
    parser.add_argument("--min", type=float, default=None, help="required ratio, such as 4.5 or 3")
    args = parser.parse_args()
    try:
        measured = ratio(args.foreground, *args.background)
    except ValueError as error:
        print(f"contrast: {error}", file=sys.stderr)
        return 2
    if args.min is None:
        verdict = f"normal text {'pass' if measured >= 4.5 else 'FAIL'}, large text and boundaries {'pass' if measured >= 3 else 'FAIL'}"
        print(f"{measured:.2f}:1  {verdict}")
        return 0
    print(f"{measured:.2f}:1  {'pass' if measured >= args.min else 'FAIL'} at {args.min:g}:1")
    return 0 if measured >= args.min else 1


if __name__ == "__main__":
    sys.exit(main())
