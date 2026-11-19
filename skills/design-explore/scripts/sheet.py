# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.1"]
# ///
"""Draw one contact sheet per direction, and one for the shared references.

Usage: uv run sheet.py <path to exploration.md>

Reads the references table and the "## Directions" section of exploration.md,
and writes references/sheet-<direction>.jpg next to it, in place of the sheets from the last run.
A dropped row is left out.
"""

import math
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageDraw, ImageFont

WIDTH, MARGIN, GAP, COLUMNS = 1600, 40, 32, 2
CELL = (WIDTH - 2 * MARGIN - GAP * (COLUMNS - 1)) // COLUMNS
THUMB_MAX_HEIGHT, PORTRAIT_HEIGHT, ROW_ROOM = 560, 760, 1300
COLUMNS_NEEDED = ("id", "screenshot", "link", "source", "part", "take", "direction")
INK, MUTED, PINK, PAPER, LINE = (20, 20, 20), (105, 105, 105), (214, 0, 120), (255, 255, 255), (215, 215, 215)


def font(size):
    return ImageFont.load_default(size=size)


TITLE, BODY, LABEL, SMALL = font(34), font(20), font(22), font(18)


def wrap(text, face, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and face.getlength(trial) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return lines + [line] if line else lines


class Canvas:
    def __init__(self, rows):
        self.image = Image.new("RGB", (WIDTH, 800 + math.ceil(rows / COLUMNS) * ROW_ROOM), PAPER)
        self.draw = ImageDraw.Draw(self.image)

    def text(self, x, y, text, face, fill, width):
        for line in wrap(text, face, width):
            self.draw.text((x, y), line, font=face, fill=fill)
            y += round(face.size * 1.4)
        return y


def cells(row):
    return [cell.strip().replace("\\|", "|") for cell in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


def read_references(markdown):
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        header = cells(line)
        if line.startswith("|") and set(COLUMNS_NEEDED) <= set(header):
            rows = []
            for row in lines[index + 2 :]:
                if not row.startswith("|"):
                    break
                rows.append({**dict.fromkeys(header, ""), **dict(zip(header, cells(row)))})
            return rows
    sys.exit(f"sheet.py: found no references table with the columns {', '.join(COLUMNS_NEEDED)}")


def read_directions(markdown):
    section = re.search(r"^## Directions\n(.*?)(?=^## |\Z)", markdown, re.M | re.S)
    directions = {}
    for block in re.split(r"^### ", section.group(1) if section else "", flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        letter = heading.split(".")[0].strip().lower()
        plain = [re.sub(r"[*`]", "", line).strip() for line in body.splitlines()]
        paragraphs = [line for line in plain if line.startswith(("Stance:", "The one bold thing:"))]
        if len(paragraphs) != 2:
            sys.exit(f"sheet.py: '### {heading.strip()}' needs one 'Stance:' line and one 'The one bold thing:' line")
        directions[letter] = (heading.strip(), paragraphs)
    return directions


def screenshot_path(folder, row):
    embed = re.search(r"!\[[^\]]*\]\(<?([^)>]+)>?\)", row["screenshot"])
    path = folder / unquote(embed.group(1).strip()) if embed else None
    if not path or not path.is_file():
        sys.exit(f"sheet.py: row {row['id']} needs a screenshot cell like ![r01](references/r01-product.jpg) that points at a file")
    return path


def thumbnail(path, box):
    image = Image.open(path).convert("RGB")
    middle = None
    if box:
        x0, x1 = sorted((box[0], box[2]))
        y0, y1 = sorted((box[1], box[3]))
        ImageDraw.Draw(image).rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), outline=PINK, width=max(5, image.width // 240))
        middle = (y0 + y1) / 2 / image.height
        if (x1 - x0) * (y1 - y0) < 0.12 * image.width * image.height:
            width = min(image.width, max((x1 - x0) * 2.4, image.width * 0.45))
            height = min(image.height, width * 0.62)
            left = min(max((x0 + x1) / 2 - width / 2, 0), image.width - width)
            top = min(max((y0 + y1) / 2 - height / 2, 0), image.height - height)
            image = image.crop((round(left), round(top), round(left + width), round(top + height)))
            middle = None
    scale = CELL / image.width
    if image.height > 1.2 * image.width:
        scale = min(scale, PORTRAIT_HEIGHT / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    if image.height > PORTRAIT_HEIGHT:
        top = 0 if middle is None else min(max(middle * image.height - THUMB_MAX_HEIGHT / 2, 0), image.height - THUMB_MAX_HEIGHT)
        image = image.crop((0, round(top), image.width, round(top) + THUMB_MAX_HEIGHT))
    return image


def draw_sheet(folder, title, paragraphs, rows, out):
    canvas, y = Canvas(len(rows)), MARGIN
    y = canvas.text(MARGIN, y, title, TITLE, INK, WIDTH - 2 * MARGIN) + 10
    for paragraph in paragraphs:
        y = canvas.text(MARGIN, y, paragraph, BODY, INK, WIDTH - 2 * MARGIN) + 8
    y = canvas.text(MARGIN, y, "A pink outline marks the part to take. No outline means the whole page.", SMALL, MUTED, WIDTH - 2 * MARGIN) + 20
    for start in range(0, len(rows), COLUMNS):
        bottom = y
        for column, row in enumerate(rows[start : start + COLUMNS]):
            x = MARGIN + column * (CELL + GAP)
            numbers = [int(n) for n in re.findall(r"\d+", row["box"])]
            image = thumbnail(screenshot_path(folder, row), numbers if len(numbers) == 4 else None)
            canvas.image.paste(image, (x, y))
            canvas.draw.rectangle((x, y, x + image.width - 1, y + image.height - 1), outline=LINE)
            product = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", row["link"])
            cursor = canvas.text(x, y + image.height + 12, f"{row['id']}  {product}  ·  {row['source']}", LABEL, INK, CELL)
            cursor = canvas.text(x, cursor + 2, f"Part: {row['part']}", SMALL, PINK, CELL)
            bottom = max(bottom, canvas.text(x, cursor + 2, row["take"], SMALL, INK, CELL))
        y = bottom + 36
    canvas.image.crop((0, 0, WIDTH, y)).save(out, quality=82)
    print(f"wrote {out} ({len(rows)} references)")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    markdown = source.read_text()
    rows = [row for row in read_references(markdown) if not row.get("status", "").lower().startswith("dropped")]
    directions = read_directions(markdown)
    groups = sorted({row["direction"].strip().lower() for row in rows})
    if "" in groups:
        sys.exit("sheet.py: every row needs a direction: a letter, or shared")
    for stale in (source.parent / "references").glob("sheet-*.jpg"):
        stale.unlink()
    for group in groups:
        heading, paragraphs = directions.get(group, ("Shared references", ["These help every direction."]))
        if group != "shared" and group not in directions:
            sys.exit(f"sheet.py: direction {group.upper()} has rows but no '### {group.upper()}. Name' heading under '## Directions'")
        members = [row for row in rows if row["direction"].strip().lower() == group]
        draw_sheet(source.parent, heading, paragraphs, members, source.parent / "references" / f"sheet-{group}.jpg")


if __name__ == "__main__":
    main()
