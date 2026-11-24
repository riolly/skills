"""Repaint a Recraft SVG in a fixed palette. usage: repaint.py in.svg out.svg [from=to,...]"""
import re, sys, numpy as np
from skimage import color
PAINT = "#d9a93f #ecd9a0 #7c8b3f #c98b7a #c9b48f #8a6a45 #2f4f77 #f1ead8 #a37d33 #e2d5b7".split()
pairs = {h: h for h in PAINT}
pairs.update({"#e9dab9": "#e2d5b7", "#f8cc68": "#ecd9a0", "#f5c357": "#ecd9a0"})
if len(sys.argv) > 3:
    pairs.update(dict(p.split("=") for p in sys.argv[3].split(",")))
def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def lab(c): return color.rgb2lab(np.array(c, dtype=float).reshape(1, -1, 3) / 255)[0]
keys = list(pairs); key_lab = lab([rgb(k) for k in keys])
s = open(sys.argv[1]).read()
grad = {}
for gid, body in re.findall(r'<linearGradient id="(\w+)".*?>(.*?)</linearGradient>', s, flags=re.S):
    grad[gid] = np.mean([list(map(int, c)) for c in re.findall(r"rgb\((\d+),(\d+),(\d+)\)", body)], axis=0)
out, used = [], {}
for i, (fill, d) in enumerate(re.findall(r'<path[^>]*?fill="([^"]*)"[^>]*? d="([^"]*)"', s)):
    c = grad[fill[5:-1]] if fill.startswith("url") else list(map(int, re.findall(r"\d+", fill)))
    to = pairs[keys[int(((lab([c]) - key_lab) ** 2).sum(-1).argmin())]]
    used[to] = used.get(to, 0) + 1
    if i == 0 and to == "#e2d5b7":
        continue
    out.append(f'<path fill="{to}" d="{d}"/>')
vb = re.search(r'viewBox="([^"]*)"', s).group(1)
open(sys.argv[2], "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" preserveAspectRatio="none">{"".join(out)}</svg>')
print(sys.argv[2], len(out), "shapes", used)
