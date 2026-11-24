import base64, json, sys, urllib.request, pathlib
key = pathlib.Path.home().joinpath(".config/recraft/api-key").read_text().strip()
src = pathlib.Path("/home/alberto/.t3/worktrees/bible-first-app/feat-ruth-wall-painting-e78967cb39dd3bdb/design/books/ruth-wall/source.prompt.md").read_text()
scenes = src[src.index("## The scenes"):]
prompt = """A tall narrow vector painting for the Book of Ruth, a montage like a painted film poster: six scenes stacked from the bottom to the top, overlapping each other, in the order of the story.

Style: flat, warm, storybook illustration. Every shape is a closed outline in one even dark gold line, #a37d33, with one flat colour inside it. No texture, grain, gradient, shading or hatching. Prefer fewer, larger shapes. Barley is drawn as big sweeping ears and long leaves.

The background is bare flat silk, #e2d5b7, with nothing drawn on it: no clouds, bushes, trees, rocks, birds or filler. Use only these eight colours: barley gold #d9a93f, straw #ecd9a0, olive green #7c8b3f, dusty rose #c98b7a, warm stone #c9b48f, earth brown #8a6a45, night blue #2f4f77, pale moon #f1ead8.

People are small and have no faces: a plain round head in straw under a veil or head cloth, no eyes, nose, mouth or beard. No words, letters or numbers anywhere. The painting has an uneven outline and no straight sides, and bare silk shows between scenes that do not touch. In the bottom third only the sheaf is drawn, in the middle, with bare silk on both sides of it.

""" + scenes
def rgb(h): return {"rgb": [int(h[i:i+2], 16) for i in (1, 3, 5)]}
controls = {"colors": [rgb(h) for h in "#d9a93f #ecd9a0 #7c8b3f #c98b7a #c9b48f #8a6a45 #2f4f77 #f1ead8 #a37d33".split()], "background_color": rgb("#e2d5b7")}
def data_url(p):
    ext = p.rsplit(".", 1)[1]
    return f"data:image/{ext};base64," + base64.b64encode(open(p, "rb").read()).decode()
which = sys.argv[1]
if which == "a":
    url, body = "images/generations", {"prompt": prompt, "model": "recraftv4_1_vector", "size": "1:2", "controls": controls}
elif which == "b":
    url, body = "images/generations", {"prompt": prompt, "model": "recraftv4_styles_vector", "size": "1:2", "controls": controls, "style_reference_urls": [data_url("ref.png"), data_url("jonah.webp")]}
else:
    url, body = "images/imageToImage", {"prompt": prompt, "model": "recraftv4_1_vector", "strength": float(sys.argv[2]), "controls": controls, "image_url": data_url("src2.png")}
req = urllib.request.Request("https://external.api.recraft.ai/v1/" + url, json.dumps(body).encode(), {"Authorization": "Bearer " + key, "Content-Type": "application/json"})
try:
    r = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    sys.exit(f"{e.code} {e.read().decode()[:600]}")
print(which, "credits", r.get("credits"))
urllib.request.urlretrieve(r["data"][0]["url"], f"dl/gen-{which}.svg")
