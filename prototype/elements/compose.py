"""Compose a painting from the element library and a scene list."""
import json, sys
lib = json.load(open("library.json"))
def symbols(names):
    out = []
    for n in names:
        e = lib[n]
        paths = "".join(f'<path fill="{c}" d="{d}"/>' for c, d in e["fills"].items())
        out.append(f'<symbol id="{n}" viewBox="0 0 {e["w"]:g} {e["h"]:g}">{paths}</symbol>')
    return "".join(out)
def use(n, cx, bottom, height, flip=False):
    e = lib[n]; w = height * e["w"] / e["h"]; x = cx - w / 2; y = bottom - height
    t = f' transform="translate({2 * cx:g} 0) scale(-1 1)"' if flip else ""
    return f'<use href="#{n}" x="{x:g}" y="{y:g}" width="{w:g}" height="{height:g}"{t}/>'
if __name__ == "__main__":
    names = list(lib); cols = 5; cell = 300
    rows = -(-len(names) // cols)
    body = "".join(use(n, 150 + (i % cols) * cell, 280 + (i // cols) * cell, min(250, 250 * lib[n]["h"] / lib[n]["w"])) for i, n in enumerate(names))
    open("library.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cols * cell} {rows * cell}"><rect width="100%" height="100%" fill="#2f4f77"/>{symbols(names)}{body}</svg>')
