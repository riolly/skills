"""Turn each raw traced element into a clean one: palette colours, no background."""
import re, glob, json, numpy as np
from skimage import color
PAINT = "#d9a93f #ecd9a0 #7c8b3f #c98b7a #c9b48f #8a6a45 #2f4f77 #f1ead8 #a37d33".split()
GROUND = "#eadcbc"
def rgb(h): return [int(h[i:i + 2], 16) for i in (1, 3, 5)]
def lab(c): return color.rgb2lab(np.array(c, dtype=float).reshape(1, -1, 3) / 255)[0]
paint_lab, ground_lab = lab([rgb(h) for h in PAINT]), lab([rgb(GROUND)])[0]
lib = {}
for f in sorted(glob.glob("el2/*.raw.svg")):
    name = f[4:-8]; s = open(f).read()
    grad = {}
    for gid, body in re.findall(r'<linearGradient id="(\w+)".*?>(.*?)</linearGradient>', s, flags=re.S):
        grad[gid] = np.mean([list(map(int, c)) for c in re.findall(r"rgb\((\d+),(\d+),(\d+)\)", body)], axis=0)
    vb = list(map(float, re.search(r'viewBox="([^"]*)"', s).group(1).split()))
    by = {}
    for fill, d in re.findall(r'<path[^>]*?fill="([^"]*)"[^>]*? d="([^"]*)"', s):
        c = grad[fill[5:-1]] if fill.startswith("url") else list(map(int, re.findall(r"\d+", fill)))
        L = lab([c])[0]
        if c[0] < c[1] - 35 and c[0] < c[2] - 15:
            continue
        to = PAINT[int(((L - paint_lab) ** 2).sum(-1).argmin())]
        by.setdefault(to, []).append(d)
    lib[name] = {"w": vb[2], "h": vb[3], "fills": {k: " ".join(v) for k, v in by.items()}}
    print(name, int(vb[2]), int(vb[3]), {k: len(v) for k, v in by.items()})
json.dump(lib, open("library.json", "w"))
