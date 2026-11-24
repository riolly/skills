#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["numpy", "pillow", "scipy", "scikit-image", "vtracer"]
# ///
"""Trace a flat-colour picture into an SVG of flat fills and one line layer.

The picture's own colours are found by clustering. Each one is painted with the
nearest colour of --paint, or becomes bare ground. The line is found by how much
darker it is than what surrounds it, so it survives a soft or small picture.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi
from scipy.cluster.vq import kmeans2
from skimage import color, morphology


def rgb_of(hex_colour):
    h = hex_colour.lstrip("#")
    return [int(h[i : i + 2], 16) for i in (0, 2, 4)]


def hex_of(rgb):
    return "#%02x%02x%02x" % tuple(int(v) for v in rgb)


def lab_of(hex_colours):
    rgb = np.array([rgb_of(h) for h in hex_colours], dtype=np.float64).reshape(1, -1, 3) / 255
    return color.rgb2lab(rgb)[0]


def nearest(lab, palette):
    out = np.empty(lab.shape[:-1], dtype=np.int32)
    flat, res = lab.reshape(-1, 3), out.reshape(-1)
    for i in range(0, len(flat), 1 << 18):
        res[i : i + (1 << 18)] = ((flat[i : i + (1 << 18), None, :] - palette[None]) ** 2).sum(-1).argmin(-1)
    return out


def fill_from_neighbours(labels, hole):
    idx = ndi.distance_transform_edt(hole, return_distances=False, return_indices=True)
    return labels[idx[0], idx[1]]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("picture")
    p.add_argument("out", help="the SVG to write. A swatch sheet is written next to it as <out>.palette.png")
    p.add_argument("--paint", required=True, help="the flat colours to paint with, as hex, comma separated")
    p.add_argument("--ground", required=True, help="the picture's bare background, as hex. It is left empty in the SVG")
    p.add_argument("--line", required=True, help="the colour to draw the line in, as hex")
    p.add_argument("--map", default="", help="corrections, as from=to pairs: a colour from the swatch sheet = a paint colour, ground or line")
    p.add_argument("--colours", type=int, default=16, help="how many of the picture's own colours to look for")
    p.add_argument("--groups", help="JSON file: {name: [[x, y], ...]}, one polygon per group in picture pixels, drawn back to front")
    p.add_argument("--group-attr", default="data-group", help="the attribute that names a group")
    p.add_argument("--scale", type=int, default=4, help="how much the picture is enlarged before tracing")
    p.add_argument("--line-width", type=float, default=2.5, help="the widest line, in picture pixels")
    p.add_argument("--line-depth", type=float, default=7, help="how much darker than its surroundings a line is, in L units of Lab")
    p.add_argument("--no-line", action="store_true", help="skip the line layer")
    p.add_argument("--outline", type=float, default=0, help="also draw the line this wide, in picture pixels, wherever two colours meet, so every shape is closed")
    p.add_argument("--speckle", type=int, default=12, help="the smallest fill kept, as an area in picture pixels")
    p.add_argument("--smooth", type=float, default=1.0, help="how hard texture is flattened before colours are read")
    return p.parse_args()


def main():
    a = parse_args()
    paint = [c.strip() for c in a.paint.split(",")]
    targets = paint + [a.ground]
    ground = len(paint)

    picture = Image.open(a.picture).convert("RGB")
    width, height = picture.size
    big_size = (width * a.scale, height * a.scale)
    big = picture.resize(big_size, Image.LANCZOS)
    lab = color.rgb2lab(np.asarray(big, dtype=np.float64) / 255)

    is_line = np.zeros(lab.shape[:2], dtype=bool)
    if not a.no_line:
        lightness = ndi.gaussian_filter(lab[..., 0], a.scale * 0.35)
        ridge = ndi.grey_closing(lightness, footprint=morphology.disk(int(a.line_width * a.scale))) - lightness
        is_line = ridge > a.line_depth
        is_line = morphology.remove_small_objects(is_line, max_size=a.scale * a.scale * 8)
        is_line = morphology.remove_small_holes(is_line, max_size=a.scale * a.scale * 2)

    flat_lab = lab
    if a.smooth:
        flattened = big.filter(ImageFilter.MedianFilter(2 * round(a.smooth * a.scale) + 1))
        flat_lab = color.rgb2lab(np.asarray(flattened, dtype=np.float64) / 255)
    off_line = ~ndi.binary_dilation(is_line, iterations=max(1, a.scale // 2))

    sample = flat_lab[off_line][:: max(1, off_line.sum() // 200_000)]
    centres, _ = kmeans2(sample, a.colours, minit="++", seed=1)
    cluster = nearest(flat_lab, centres)
    share = np.bincount(cluster[off_line], minlength=a.colours) / off_line.sum()
    found = [hex_of(v) for v in (color.lab2rgb(centres.reshape(1, -1, 3))[0] * 255).round()]

    target_lab = lab_of(targets)
    to_target = nearest(centres, target_lab)
    line_colour = len(targets)
    for pair in filter(None, a.map.split(",")):
        source, target = (s.strip() for s in pair.split("="))
        gap = np.sqrt(((lab_of([source]) - centres) ** 2).sum(-1))
        if gap.min() > 3:
            sys.exit(f"--map: this run found no colour {source}. It found: {', '.join(found)}")
        if target not in ("ground", "line") and target not in paint:
            sys.exit(f"--map: {target} is not ground, line or one of --paint")
        to_target[gap.argmin()] = {"ground": ground, "line": line_colour}.get(target) if target in ("ground", "line") else paint.index(target)
    named = targets + ["line"]

    order = np.argsort(-share)
    sheet = Image.new("RGB", (460, 34 * a.colours + 8), "white")
    draw = ImageDraw.Draw(sheet)
    print("found in picture -> painted as    share")
    for row, i in enumerate(order):
        target = named[to_target[i]] if to_target[i] != ground else "ground"
        print(f"{found[i]} -> {target:8} {share[i] * 100:5.1f}%")
        y = 8 + 34 * row
        draw.rectangle([8, y, 108, y + 26], fill=found[i])
        draw.rectangle([120, y, 220, y + 26], fill={"ground": a.ground, "line": a.line}.get(target, target), outline="black")
        draw.text((232, y + 8), f"{found[i]} -> {target}  {share[i] * 100:.1f}%", fill="black")
    sheet.save(f"{a.out}.palette.png")

    labels = to_target[cluster]
    is_line |= labels == line_colour
    labels = fill_from_neighbours(labels, ~off_line | (labels == line_colour))
    smallest = a.speckle * a.scale * a.scale
    for _ in range(2):
        speck = np.zeros_like(is_line)
        for value in np.unique(labels):
            mask = labels == value
            speck |= mask & ~morphology.remove_small_objects(mask, max_size=smallest)
        if speck.any():
            labels = fill_from_neighbours(labels, speck)

    if a.outline:
        border = np.zeros_like(is_line)
        border[:, 1:] |= labels[:, 1:] != labels[:, :-1]
        border[1:, :] |= labels[1:, :] != labels[:-1, :]
        is_line = is_line | ndi.binary_dilation(border, structure=morphology.disk(max(1, round(a.outline * a.scale / 2))))

    if a.groups:
        groups = json.loads(Path(a.groups).read_text())
    else:
        groups = {"all": [[0, 0], [width, 0], [width, height], [0, height]]}

    paint_rgb = np.array([rgb_of(c) for c in paint] + [[0, 0, 0]], dtype=np.uint8)
    tracer = dict(mode="spline", corner_threshold=60, length_threshold=4.0, splice_threshold=45, path_precision=0, filter_speckle=a.scale * 2)
    parts, counts = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for name, polygon in groups.items():
            inside_image = Image.new("1", big_size, 0)
            ImageDraw.Draw(inside_image).polygon([(x * a.scale, y * a.scale) for x, y in polygon], fill=1)
            inside = np.asarray(inside_image)
            shown = inside & (labels != ground)
            Image.fromarray(np.dstack([paint_rgb[labels], np.where(shown, 255, 0).astype(np.uint8)]), "RGBA").save(f"{tmp}/fills.png")
            vtracer.convert_image_to_svg_py(f"{tmp}/fills.png", f"{tmp}/fills.svg", colormode="color", hierarchical="stacked", color_precision=8, layer_difference=0, **tracer)
            fills = re.findall(r"<path[^>]*/>", Path(f"{tmp}/fills.svg").read_text())
            lines = []
            if is_line.any():
                Image.fromarray(np.where(is_line & inside, 0, 255).astype(np.uint8), "L").convert("RGB").save(f"{tmp}/line.png")
                vtracer.convert_image_to_svg_py(f"{tmp}/line.png", f"{tmp}/line.svg", colormode="binary", **tracer)
                lines = [re.sub(r'fill="[^"]*"', "", l) for l in re.findall(r"<path[^>]*/>", Path(f"{tmp}/line.svg").read_text())]
            parts.append(
                f'<g {a.group_attr}="{name}"><g data-layer="fills">{"".join(fills)}</g>'
                f'<g data-layer="line" fill="{a.line}">{"".join(lines)}</g></g>'
            )
            counts.append(f"{name}: {len(fills)} fills, {len(lines)} line shapes")

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><g transform="scale({1 / a.scale:g})">{"".join(parts)}</g></svg>\n'
    Path(a.out).write_text(svg)
    print("\n".join(counts))
    print(f"wrote {a.out}, {len(svg) // 1024} KB, and {a.out}.palette.png", file=sys.stderr)


if __name__ == "__main__":
    main()
