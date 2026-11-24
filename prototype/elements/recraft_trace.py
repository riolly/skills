"""Trace each PNG given on the command line with Recraft's vectorizer, one call per file.

Each call costs 10 API units, which is one cent. A file that already has its .raw.svg is skipped,
so a rerun never pays twice. The key is read from ~/.config/recraft/api-key.
"""
import json, pathlib, subprocess, sys, time, urllib.request

key = pathlib.Path.home().joinpath(".config/recraft/api-key").read_text().strip()
for name in sys.argv[1:]:
    png = pathlib.Path(name)
    out = png.with_suffix(".raw.svg")
    if out.exists():
        print(out, "kept")
        continue
    for wait in (0, 5, 15, 40):
        time.sleep(wait)
        reply = subprocess.run(
            ["curl", "-sS", "https://external.api.recraft.ai/v1/images/vectorize", "-H", f"Authorization: Bearer {key}",
             "-F", f"file=@{png}", "-F", "shape_stacking=cut_out"],
            capture_output=True, text=True, check=True,
        )
        answer = json.loads(reply.stdout)
        if "image" in answer:
            urllib.request.urlretrieve(answer["image"]["url"], out)
            print(out, "traced,", answer.get("credits"), "units")
            break
        if answer.get("code") != "rate_limit_exceeded":
            sys.exit(f"{png}: {answer}")
    else:
        sys.exit(f"{png}: still rate limited after four tries")
