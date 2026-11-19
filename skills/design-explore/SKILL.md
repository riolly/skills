---
name: design-explore
description: Explore a new design from real references and generated image mockups, before any UI code. The owner curates the references, they are grouped into directions, and each direction gets mockups to pick from. Use when the user asks for a new screen, a redesign, design directions or mockups, or says "design explore".
---

# Design explore

An **exploration** takes one design job from references to a picked mockup, before any UI code. A **reference** is a screenshot of a real, shipped interface. A **direction** is a named group of references with one stance. A **mockup** is a generated image of one screen in one direction, made for choosing. The **owner** curates and picks, and you gather, group and generate.

An exploration lives in `design/<slug>/` in the project and is committed with the work: `exploration.md` holds the brief and every table below, next to `references/` and `mockups/`. Every row stays. A dropped row keeps the owner's reason, because the tables are how the owner finds the step where an exploration went wrong.

## 1. Scope

Write the brief at the top of `exploration.md`:

- the screens or components, and the one decision or action each must support
- the viewport of each screen, and the state it is shown in when it changes by role or by data
- the real copy and labels that go on them, word for word, with invented sample values wherever the real data is personal or secret, because step 5 sends this text to an outside service. A long page gives its headings and its first screen of copy.
- what is fixed (brand, design system, content) and what is open
- a screenshot of each screen as it looks today, when it exists, saved as `references/current-<screen>.jpg`

Then the **scale**: how many directions (one to three) and which screens each direction gets. The owner sets the scale and what is fixed. Ask for whatever part they haven't given, in one message, with your recommendation.

Done when the brief names every screen with its viewport and real content, and the owner has set the directions, the screens and what is fixed.

## 2. Gather

Collect about four candidates for each direction in the scale, at least five in all, and some for every screen. Take them from these sources, in order:

1. What the owner gave: links, screenshots and products they named.
2. References the project already kept, in earlier explorations or in its design docs.
3. Real products you know do the same job well, and others found by web search. Galleries such as Godly and Land-book hold marketing pages only, and Mobbin needs a login. The free search in `ui-radar` returns product names without screenshots, so use it for names only.

Open each candidate's live page and take your own screenshot in a 1440 by 900 window, or 390 by 844 for a phone screen. Headless Chrome's `--screenshot` with `--window-size` is enough. Save it as `references/r<nn>-<product>.jpg`. Look at the screenshot. Retake or pass over one that shows a cookie banner, a login wall or a page still loading.

A candidate earns a row when you can name one visible thing worth taking from it. `take` says what that thing is. `part` says where it is: `whole page` when the reference is for the page's overall layout, type or colour, or else the one element, such as `the row of numbers above the chart`. When the thing is motion, say so in `take`, because the link is then the only evidence. Prefer candidates that differ visibly from each other and from the project's current screens.

| id | screenshot | link | source | part | take | direction | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

`screenshot` embeds the image. `source` is how you found it: owner, earlier exploration, agent pick, search, a gallery's name or ui-radar. `status` starts as `candidate`. `direction` and `reason` stay empty until steps 3 and 4. Under the table, write one line with how many pages you passed over and why.

Done when every candidate has a screenshot you have looked at and a row, and the pages passed over are counted.

## 3. Directions

Propose the directions the scale asks for, lettered A, B and C, by grouping the candidates. Write for each:

- a name of two or three words
- its stance on layout, type, colour and density
- **the one bold thing** a viewer would remember
- its references, by id, with what each one gives it

Set each row's `direction`. A candidate that fits no direction stays in the table with `direction` empty. Two directions differ enough when their thumbnails can't be confused. When the candidates only support one direction, return to step 2 for the other.

Done when every direction in the scale has all four parts and at least two references.

## 4. Curate

Show the owner one **contact sheet**, saved as `references/contact-sheet.jpg`: a section per direction with its name, stance and one bold thing, then its candidates in a grid, then the candidates with no direction. Each candidate shows its id, product, `part` and `take`, and a `part` that is an element is outlined on the screenshot. Give the questions the brief left open in the same message, each with your recommendation.

The owner keeps or drops each candidate, and may move one to another direction, change or reject a direction, or ask for more. Record `kept` or `dropped` with their reason in their words, and rewrite a direction they changed. When they ask for more, return to step 2 and search for what their reasons describe.

Done when the owner has approved the directions, says the kept set is enough, and no row is still `candidate`.

## 5. Mockups

Write one prompt file per mockup, `mockups/<direction>-<screen>.prompt.md`, holding:

- the screen and its viewport
- the copy and data from the brief, word for word
- the direction's stance and its one bold thing
- what to take from each attached reference, named by position and by its `part` ("from image 1, only the row of numbers above the chart")
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
