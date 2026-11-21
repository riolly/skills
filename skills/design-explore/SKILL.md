---
name: design-explore
description: Explore a new design from real references and generated image mockups, before any UI code. The owner curates the references, they are grouped into directions, and each direction gets mockups to pick from. Use when the user asks for a new screen, a redesign, design directions or mockups, or says "design explore".
---

# Design explore

An **exploration** takes one design job from references to a picked mockup, before any UI code. A **reference** is a screenshot of a real, shipped interface. A **direction** is a named group of references with one stance. A **mockup** is a generated image of one screen in one direction, made for choosing. The **owner** curates and picks, and you gather, group and generate.

Run an exploration in a thread of its own, because every screenshot and mockup you look at stays in the thread. When the request comes in a thread that already holds other work, write the brief there and offer to continue in a new thread.

An exploration lives in `design/<slug>/` in the project and is committed with the work: `exploration.md` holds the brief and every table below, next to `references/` and `mockups/`. Every row stays. Under **What the owner said**, keep each round of the owner's replies in their words with what you changed for it. A dropped row keeps the owner's reason, because the tables are how the owner finds the step where an exploration went wrong.

## 1. Scope

Write the brief at the top of `exploration.md`:

- the screens or components, and the one decision or action each must support
- the viewport of each screen, and the state it is shown in when it changes by role or by data
- the real copy and labels that go on them, word for word, with invented sample values wherever the real data is personal or secret, because step 5 sends this text to an outside service. A long page gives its headings and its first screen of copy.
- what is fixed (brand, design system, content) and what is open
- a screenshot of each screen as it looks today, when it exists, saved as `references/current-<screen>.jpg`

Then the **scale**: how many directions (one to three) and which screens each direction gets. The owner sets the scale and what is fixed. Ask for whatever part they haven't given, in one message, with your recommendation. Ask in that message for what only the owner has: products and images they already like, an earlier try of their own in any repo, and the content the brief can't settle, such as which items the screen lists. Wait for the answer before step 2, because a changed brief sends the whole gathering round back.

Done when the brief names every screen with its viewport and real content, and the owner has set the directions, the screens and what is fixed.

## 2. Gather

Hand steps 2 and 3 to one subagent when you can start one, so the screenshots stay out of this thread. Give it the path of this file, the path of `exploration.md` with its brief, and the owner's own references. It writes the table and the directions and draws the sheets of step 4, and it returns only how many candidates each direction has and the pages it passed over. You then look at the sheets, not at each screenshot.

Collect about four candidates for each direction in the scale, at least five in all, and some for every screen. Take them from these sources, in order:

1. What the owner gave: links, screenshots and products they named.
2. References the project already kept, in earlier explorations or in its design docs.
3. Real products you know do the same job well, and others found by web search. Galleries such as Godly and Land-book hold marketing pages only, and Mobbin needs a login. The free search in `ui-radar` returns product names without screenshots, so use it for names only.

Open each candidate's live page and take your own screenshot in a 1440 by 900 window, or 390 by 844 for a phone screen. Headless Chrome's `--screenshot` with `--window-size` is enough. Save it as `references/r<nn>-<product>.jpg`. Look at the screenshot. Close a cookie banner and retake. Pass over a login wall or a page that never finishes loading.

A candidate earns a row when you can name one visible thing worth taking from it. `take` says what that thing is. `part` says where it is: `whole page` when the reference is for the page's overall layout, type or colour, or else the one element, such as `the row of numbers above the chart`. When the thing is motion, say so in `take`, because the link is then the only evidence. Prefer candidates that differ visibly from each other and from the project's current screens.

| id | screenshot | link | source | part | box | take | direction | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

`screenshot` embeds the image, and `link` is `[Product](url)`. `box` is the element's corners on the screenshot in pixels, as `left,top,right,bottom`, and stays empty for a whole page. `source` is how you found it: owner, earlier exploration, agent pick, search, a gallery's name or ui-radar. `status` starts as `candidate`. `direction` and `reason` stay empty until steps 3 and 4. Under the table, write one line with how many pages you passed over and why.

Done when every candidate has a screenshot you have looked at and a row, and the pages passed over are counted.

## 3. Directions

Propose the directions the scale asks for, lettered A, B and C, by grouping the candidates. Write for each:

```markdown
### A. Quiet print

Stance: its layout, type, colour and density, in two or three sentences.

The one bold thing: what a viewer would remember.

- r01 gives the half-empty opening page, for the reading page.
```

The name has two or three words, and the list has one line per reference with what it gives and the screen it serves. Set each row's `direction` to its letter. A candidate that helps every direction, such as an emblem or an icon style, gets `shared`. Two directions differ enough when their mockups could not be confused at thumbnail size. When the candidates only support one direction, return to step 2 for the other.

Done when every direction in the scale has all four parts and at least two references, and every row has a `direction`.

## 4. Curate

Draw the **contact sheets**, one image per direction and one for the shared references. Run both scripts from the project's root, with the full path of this skill's folder:

```bash
uv run <this skill's folder>/scripts/sheet.py design/<slug>/exploration.md
```

Each sheet, `references/sheet-<direction>.jpg`, shows the direction's name, stance and one bold thing, then its candidates with their id, product, `part` and `take`. A `box` is outlined, and the screenshot is cropped closer when the element is small. Look at every sheet and fix a `box` that misses its element. Show the owner the sheets in order, and give the questions the brief left open in the same message, each with your recommendation.

The owner keeps or drops each candidate, and may move one to another direction, change or reject a direction, or ask for more. Record `kept` or `dropped` with their reason in their words, and rewrite a direction they changed. When they ask for more, return to step 2 and search for what their reasons describe.

The owner may approve one direction while another still changes. Redraw the sheets after every change, and take the approved direction on to step 5 without waiting for the other.

A direction is done when the owner has approved it, says its kept set is enough, and none of its rows is still `candidate`. The step is done when every direction is, and no shared row is still `candidate`.

## 5. Mockups

Write one prompt file per mockup, `mockups/<direction>-<screen>.prompt.md`, and a new one for every redo, holding:

- the screen and its viewport
- the copy and data from the brief, word for word
- the direction's stance and its one bold thing
- what to take from each attached reference, the direction's kept ones and the kept shared ones, named by position and by its `part` ("from image 1, only the row of numbers above the chart")
- a line that keeps the references' brand names, logos and photos out

Then generate it:

```bash
bash <this skill's folder>/scripts/mockup.sh \
  --prompt design/<slug>/mockups/a-home.prompt.md --out design/<slug>/mockups/a-home.webp \
  --ref design/<slug>/references/r03-linear.jpg --ref design/<slug>/references/r07-stripe.jpg
```

Attach only the references that serve this screen. `--size` defaults to a desktop screen, so pass `1024x1536` for a phone or a tablet in portrait. `--help` lists the quality and model options. Exit code 3 means the script found no OpenAI API key: ask the owner for one and stop until they give it.

Generate each direction's **key screen** first, the screen that carries most of the design. Tell the owner how many images the round will make before you run it. You may redo an image once on your own when it misses the prompt, and you say so when you show it. Show the key screens side by side. The owner picks one, asks for a redo, drops a direction, or mixes two ("A's layout with B's type"). A mix becomes a new direction with its own key screen. Then generate the remaining screens for the picked direction only, with its key mockup as the first `--ref` so the screens match.

| id | direction | screen | file | status | reason |
| --- | --- | --- | --- | --- | --- |

`file` embeds the image. A redo gets a new file, such as `a-home-2.webp`, and its own row, so the earlier mockup stays. Attach the mockup you are replacing only when the redo keeps its layout, because the image model copies the shapes of an attached mockup.

An image model can't draw a part that has to be exact, such as a chart, a count, or which of many items are in which state. Give the prompt a small state, with a handful of named items. Draw an exact part in code, as a small page in `design/<slug>/tools/`, and paste its screenshot onto the mockup. `status` starts as `candidate` and ends as `picked`, `dropped` or `redone`, with the owner's reason. Look at each mockup before you show it, and redo one whose copy or layout misses the prompt.

Done when every screen in the scale has one picked mockup, or the owner has ended the exploration, and every mockup has a row.

## 6. Build

A mockup shows a direction. Its small text is garbled and its components are not the project's, so it is no specification. Under **What we take** in `exploration.md`, write what the picked mockups settle: the layout structure, the type pairing and scale, the palette as hex values, the density and the one bold thing. Build the real screens from that list, with the project's own components and the brief's copy.

Review each built screen with its screenshot beside the picked mockup and the kept references of its direction. When another thread builds the screens, hand it `exploration.md`, and that thread does this review and step 7.

Done when every picked screen is built and has been compared that way.

## 7. Close

Write **Outcome** at the end of `exploration.md`:

- the direction that was built, or why the exploration ended without one
- per source, how many candidates it gave and how many the owner kept
- how many mockups were generated and how many were picked
- how many times the owner asked for more references or a redo, and at which step

Done when the outcome is written and the folder is committed.
