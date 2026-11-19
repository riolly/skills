---
name: design-explore
description: Explore a new design from real references and generated image mockups, before any UI code. The owner curates the references, they are grouped into directions, and each direction gets mockups to pick from. Use when the user asks for a new screen, a redesign, design directions or mockups, or says "design explore".
---

# Design explore

An **exploration** takes one design job from references to a picked mockup, before any UI code. A **reference** is a screenshot of a real, shipped interface. A **direction** is a named group of kept references with one stance. A **mockup** is a generated image of one screen in one direction, made for choosing. The **owner** curates and picks, and you gather, group and generate.

An exploration lives in `design/<slug>/` in the project and is committed with the work: `exploration.md` holds the brief and every table below, next to `references/` and `mockups/`. Every row stays. A dropped row keeps the owner's reason, because the tables are how the owner finds the step where an exploration went wrong.

## 1. Scope

Write the brief at the top of `exploration.md`:

- the screens or components, and the one decision or action each must support
- the real copy and labels that go on them, word for word, with invented sample values wherever the real data is personal or secret, because step 5 sends this text to an outside service
- what is fixed (brand, design system, content) and what is open

Then the **scale**: how many directions (one to three) and which screens each direction gets. The owner sets the scale. Ask for whatever part they haven't given, in one message, with your recommendation.

Done when the brief names every screen with its real content, and the owner has set the directions and the screens.

## 2. Gather

Collect about four candidates per direction, and at least five. Take them from these sources, in order:

1. What the owner gave: links, screenshots and products they named.
2. References kept in the project's earlier explorations.
3. Real products that do the same job, and curated galleries such as Godly, Land-book, Mobbin and Awwwards, found by web search. The free search in `ui-radar` returns product names without screenshots, so use it for names only.

Open each candidate's live page and take your own screenshot at 1440 px wide, or 390 px for a phone screen, of the part that matters to the job. Save it in `references/` as JPEG or WebP when the tool allows. Look at the screenshot. A candidate earns a row when you can name one visible thing worth taking from it: a layout, a type pairing, a use of colour, a density or a detail. Prefer candidates that differ visibly from each other and from what the project already looks like.

| id | screenshot | link | source | take | status | reason |
| --- | --- | --- | --- | --- | --- | --- |

`source` is how you found it: owner, earlier exploration, the gallery's name, search or ui-radar. `status` starts as `candidate`.

Done when every candidate has a screenshot you have looked at and a full row.

## 3. Curate

Show the owner every candidate with its screenshot, link and `take`. The owner keeps some, drops some, and may ask for more. Record `kept` or `dropped` with their reason in their words. When they ask for more, return to step 2 and search for what their reasons describe.

Done when the owner says the kept set is enough and no row is still `candidate`.

## 4. Directions

Group the kept references into the directions the owner asked for, lettered A, B and C. Write for each:

- a name of two or three words
- the references it draws on, and what it takes from each
- its stance on layout, type, colour and density
- **the one bold thing** a viewer would remember

Two directions differ enough when their thumbnails can't be confused. With more than one direction, show the owner this list and wait for their approval, because every mockup costs money.

Done when each direction has all four parts, and the owner has approved the list when there is more than one.

## 5. Mockups

Write one prompt file per mockup, `mockups/<direction>-<screen>.prompt.md`, holding:

- the screen and its viewport
- the copy and data from the brief, word for word
- the direction's stance and its one bold thing
- what to take from each attached reference, named by position ("from image 1, the column layout")
- a line that keeps the references' brand names, logos and photos out

Then generate it:

```bash
bash <this skill's folder>/scripts/mockup.sh --prompt mockups/a-home.prompt.md --out mockups/a-home.webp \
  --ref references/r03.webp --ref references/r07.webp
```

`--help` lists the size, quality and model options. Exit code 3 means the script found no OpenAI API key: ask the owner for one and stop until they give it.

Generate each direction's **key screen** first, the screen that carries most of the design. Tell the owner how many images the round will make before you run it. Show the key screens side by side. The owner picks one, asks for a redo, drops a direction, or mixes two ("A's layout with B's type"). A mix becomes a new direction with its own key screen. Then generate the remaining screens for the directions still alive, with the picked key mockup as the first `--ref` so the screens match.

| id | direction | screen | file | status | reason |
| --- | --- | --- | --- | --- | --- |

`status` is `picked`, `dropped` or `redone`.

Done when every screen in the scale has one picked mockup, or the owner has ended the exploration, and every mockup has a row.

## 6. Build

A mockup shows a direction. Its small text is garbled and its components are not the project's, so it is no specification. Under **What we take** in `exploration.md`, write what the picked mockups settle: the layout structure, the type pairing and scale, the palette as hex values, the density and the one bold thing. Build the real screens from that list, with the project's own components and the brief's copy.

Review each built screen with its screenshot beside the picked mockup and the kept references of its direction.

Done when every picked screen is built and has been compared that way.

## 7. Close

Write **Outcome** at the end of `exploration.md`:

- the direction that was built, or why the exploration ended without one
- per source, how many candidates it gave and how many the owner kept
- how many mockups were generated and how many were picked
- how many times the owner asked for more references or a redo, and at which step

Done when the outcome is written and the folder is committed.
