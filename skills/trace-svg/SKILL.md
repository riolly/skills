---
name: trace-svg
description: Draw an illustration as SVG by tracing a picture, not by writing coordinates. Use when asked to draw, redraw or vectorize an illustration, painting or scene as SVG, from an image, a mockup or a description.
---

# Trace SVG

A picture becomes an SVG by tracing. The image model or a reference supplies the drawing. You choose the source, the colours and the groups, and `scripts/trace.py` writes every path.

Write paths by hand only for a mark of about twenty simple shapes or fewer, such as an icon or a glyph. On 2026-11-24 a wall painting written as coordinates from a written plan scored 5 out of 10 against its mockup, and a trace of the same mockup kept its drawing.

## Steps

1. **Get a source that traces.** It traces when every area is one flat colour, the line is darker than the colours on both sides of it, the background is one bare colour, and the short side is 1024 pixels or more.
   - A reference that already shows the wanted drawing is the source. Take the original file at full size, because a shrunken or lossy copy traces ragged.
   - With only a description, or a reference that is soft, textured or shows the wrong subject, generate the source with `design-explore`'s `scripts/mockup.sh`. Attach the reference for its style. Ask for flat fills, one even dark line around every shape, the exact hex colours, a bare background in one named colour, and no texture, grain, gradient or soft edge.
   - Parts that overlap and must each be whole get one source each.
2. **Trace it.** Run `scripts/trace.py <picture> <out.svg> --paint <hex,hex,...> --ground <hex> --line <hex>`. `--paint` is the palette to paint with, `--ground` the picture's background, which the SVG leaves empty, and `--line` the colour to draw the line in. `--help` lists the other options.
3. **Correct the colours.** The run prints each colour it found in the picture and the paint it chose, and draws the same rows in `<out.svg>.palette.png`. Look at the sheet. Correct a row with `--map <found>=<paint>`, `<found>=ground` or `<found>=line`. Done when every row is painted as the picture means it.
4. **Name the groups.** For parts that the page shows, hides or colours apart, write `--groups groups.json` as `{"name": [[x, y], ...]}`: one polygon per group, in picture pixels, drawn back to front. Each group is cut along its polygon, so run the polygon's edge where the two parts meet. `--group-attr` sets the attribute that carries the name.
5. **Compare.** Render the SVG in headless Chrome at the size the page shows it, beside the source at the same size. Then compare two crops at double size, one where the detail is finest and one where colours meet. Fix what differs with the table below and trace again. Done when the pair differs only by the palette.
6. **Fit it to the page.** Wrap the traced `<g>` in the page's `viewBox` with a `transform`. A line-only state is one CSS rule, `[data-layer=fills] path { fill: <ground> }`, and it reads well only when the trace ran with `--outline`. Run `svgo` on the result and report its size in bytes after gzip.

Keep the trace command in the repo that owns the SVG, next to the source picture, so a rerun writes the same file. To change the drawing, change the source or an option and trace again. A shape the source lacks goes in its own hand-written group on top.

## What to change

| The render shows | Change |
|---|---|
| A line that breaks or is missing | Lower `--line-depth` to 5. For a thick line raise `--line-width`, or map its colour with `<found>=line`. |
| A shape with no line where it meets the background or a darker colour | Add `--outline 1.2`. |
| A thin dark shape drawn as line | Raise `--line-depth`, or lower `--line-width`. |
| Specks and ragged islands | Raise `--speckle` to 30 and `--smooth` to 1.5. If they stay, the source is textured: generate a flatter one. |
| Two tones painted as one | Map the lighter one to another paint. If the run found only one of them, raise `--colours`. |
| `--map` says the run found no such colour | The found colours change with `--smooth` and `--colours`. Take the row from this run's sheet. |
| A file that is too heavy | Raise `--speckle`, and ask the source for fewer, larger shapes. `--scale` does not change the size. |
