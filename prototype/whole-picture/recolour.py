"""Repaint a traced SVG in a fixed palette and lift its line into a layer of its own."""
import re, sys, numpy as np
from skimage import color
from svgpathtools import parse_path

src, out, max_line_width = sys.argv[1], sys.argv[2], float(sys.argv[3])
SILK, LINE = "#e2d5b7", "#a37d33"
ANCHORS = {  # a colour in the picture -> what it is painted as
    "#eed9b2": SILK, "#dc9726": "#d9a93f", "#e6a33a": "#d9a93f", "#cf9136": "#d9a93f", "#e9b258": "#d9a93f",
    "#f8c364": "#ecd9a0", "#fdce74": "#ecd9a0", "#f6d8a4": "#f1ead8", "#436069": "#2f4f77", "#5e6259": "#2f4f77",
    "#ceaa73": "#c9b48f", "#d68c59": "#c98b7a", "#c37847": "#c98b7a", "#7f8057": "#7c8b3f", "#766a3e": "#7c8b3f",
    "#b17a32": "dark", "#926222": "dark", "#835318": "dark",
}
def lab(rgbs): return color.rgb2lab(np.array(rgbs, dtype=float).reshape(1, -1, 3) / 255)[0]
def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
anchor_lab, anchor_to = lab([rgb(h) for h in ANCHORS]), list(ANCHORS.values())

s = open(src).read()
grad = {}
for gid, body in re.findall(r'<linearGradient id="(\w+)".*?>(.*?)</linearGradient>', s, flags=re.S):
    grad[gid] = np.mean([list(map(int, c)) for c in re.findall(r"rgb\((\d+),(\d+),(\d+)\)", body)], axis=0)
viewbox = re.search(r'viewBox="([^"]*)"', s).group(1)
fills, lines = [], []
for i, (fill, d) in enumerate(re.findall(r'<path transform="translate\(0,0\)" fill="([^"]*)" d="([^"]*)"', s)):
    c = grad[fill[5:-1]] if fill.startswith("url") else list(map(int, re.findall(r"\d+", fill)))
    to = anchor_to[int(((lab([c]) - anchor_lab) ** 2).sum(-1).argmin())]
    if to == SILK and i == 0:
        continue
    if to == "dark":
        p = parse_path(d)
        area = sum(abs(sp.area()) for sp in p.continuous_subpaths() if sp.isclosed())
        length = p.length(error=1e-2)
        if length and 2 * area / length < max_line_width:
            lines.append(f'<path d="{d}"/>')
            continue
        to = "#8a6a45"
    fills.append(f'<path fill="{to}" d="{d}"/>')
open(out, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><g data-layer="fills">{"".join(fills)}</g><g data-layer="line" fill="{LINE}">{"".join(lines)}</g></svg>')
print(len(fills), "fills,", len(lines), "line shapes")
