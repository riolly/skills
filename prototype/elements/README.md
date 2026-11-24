# Prototype: a painting built from traced elements

These scripts are the throwaway test of 2026-11-24 that built Ruth's wall painting for the Bible app from 13 separate elements. They are not part of the `trace-svg` skill yet. The skill is rewritten from them once Ruth's painting has been redone this way and approved.

The steps, in order:

1. `sheet.prompt.md` asks the image model for one sheet of separate elements on a plain background.
2. `split.py` cuts the sheet into one PNG per element and replaces the background with a key colour.
3. `recraft_trace.py` traces each PNG with Recraft's vectorizer, at one cent each.
4. `elements.py` repaints each trace in the book's palette, drops the key colour, and writes `library.json`.
5. `compose.py` and `ruth_scene.py` place the elements into the painting.

Paths, names and the palette are written into the scripts for that one test.
