---
name: designing-ui
description: Designing user interfaces. Use when building or restyling a screen or component, creating or changing a theme or design tokens, or reviewing how a UI looks.
---

A screen reads well when three things hold. **Rank**: the eye lands on what matters most, because everything else was made quieter. **Group**: things that belong together sit closer to each other than to anything else. **Scale**: every size, gap, radius, shadow and colour is a step from the project's system, chosen by comparing neighbouring steps.

Run the steps in order, or the route under them that fits the task. The reference sections are what the steps apply, and step 7 checks every one against [Precedence](#precedence).

Five more bodies of reference live in sibling files. Read each when its condition holds:

- [`foundations.md`](foundations.md): the project has no tokens or scales yet, or the task creates or changes a theme, palette, type scale, spacing scale, radius or shadows.
- [`images.md`](images.md): the screen places a photo, a user-uploaded image, a screenshot, a logo, or an icon larger than 24px.
- [`prose.md`](prose.md): the screen shows long-form text or rendered markdown, such as an article, a docs page or a chat message.
- [`shadcn.md`](shadcn.md): the project has a `components.json` file.
- [`finishing.md`](finishing.md): the page is a marketing page, or the screen passes step 7 and still looks plain.

## Steps

1. **Read the system.** Find, in the project's own files, its design docs such as `DESIGN.md`, tokens, spacing and type scales, component library, icon set, and whether it has a dark mode. Done when you can name the tokens, scale steps and components this work will use and whether the project owns the component source, or have found that none exist and read `foundations.md`.
2. **Name the feature and the page type.** Design the one feature asked for, and include only what works now or what you are building now; navigation appears once there are real destinations for it. Then name the page type: an _app_ screen, or a _marketing or reading_ page. Done when the feature fits in one sentence, the page type is named, and every element on your list does something real.
3. **Rank.** Before styling anything, give every piece of content and every action a rank: primary, secondary or tertiary. Done when each element has a rank and each view has exactly one primary action, or none.
4. **Structure without colour.** Lay the feature out with spacing, size and weight alone, at about 400px wide first and then wider. Done when the rank order is readable in greyscale, every gap is a scale step with more space around each group than inside it, and the layout holds with the worst content the screen can receive.
5. **Colour, depth and decoration.** Add them through role tokens and component variants. Done when every colour at a use site is a role token or a variant, and every text and surface pair meets the contrast floor as measured by `scripts/contrast.py`, or is reported as a system finding.
6. **States.** Design the empty, no-results, loading, failed, invalid and focused state of every region that depends on data or input. Done when each such region has every state that applies to it.
7. **Look and correct.** Render the screen and look at it, narrow and wide, and in dark mode when the project has one. Where a control has helper text, check that it stays close to its label or control when the text wraps. When the visible gap looks too large, inspect the stack gap, margins, padding, line-height and row height, and close it without shrinking the control's target size. Then open each menu and overlay, tab to a control and submit an invalid value, and look at each result. Walk every rule in the reference sections against what you see and apply [Precedence](#precedence) to each failure. Done when each failure is fixed at the use site, reported as a system finding, or reported as an exception with the reason. When you cannot render the screen, say so in your report.

## Routes

- **Review an existing UI.** Run step 1, then the checks of step 7 across the whole screen. Reviewing is read-only: every failure becomes a finding, reported rule by rule, most visible first. A system finding appears once, however many screens it touches.
- **Small edit to one component.** Run step 1, make the change, then run step 7 on that component and what sits beside it.
- **Restyle an existing screen.** Keep its features and content. Run step 1, then step 3 on what is there, then step 4 only if the layout changes, then steps 5 to 7.
- **Create or change a theme.** Run step 1, follow `foundations.md`, then run step 7 on the screens that use the theme, in each mode.

## Precedence

Where a rule here and the project's system disagree, the kind of rule decides.

- **Floors hold everywhere**: contrast, input boundaries, focus, target size, names, the states of a data region, and a status that keeps its meaning. A project's defaults never excuse a floor.
- **Judgement applies at every use site**: Rank, Group and Text, wherever the system leaves the choice open.
- **Look belongs to the system**: shadows, surface layering, radius, density, weights, motion, border treatment, decoration and palette. Follow what the project has settled. These rules decide only where the system is silent, or when you are building a system.

**Fix a failure where it starts.** A failure that starts at the use site is fixed there. A failure that starts in a token or a shared component is a _system finding_: report the token or component, the measured value, and what else it touches. Fix it when the task is about the system or the user approves. Until then, finish the task on the existing tokens.

## Rank

- **Quieten the competition first.** When the primary thing fails to stand out, soften what competes with it (inactive nav items, a sidebar's background) before making it larger.
- **Weight and colour carry rank as much as size.** Primary text takes the foreground token and the emphasis weight at a moderate size; secondary text takes the muted text token; tertiary text is smaller. Use two weights per typeface, a normal one and an emphasis one. When the emphasis weight is 500, add colour or size to it. Interface text stays at 400 or heavier; de-emphasise with colour or size.
- **Displayed data speaks for itself.** Let format and context identify a value: "12 left in stock", an email address, a role under a name. When a label is needed, the label is the quiet part and the value the loud one. Reverse that on spec sheets, where people scan for the label. Keep explicit labels in dense admin data and in translated text.
- **A title takes the size its rank earns.** A page or card title inside an app is often small, whatever its tag. A title the content makes redundant stays in the markup for screen readers and is hidden visually.
- **Actions are styled by rank.** Primary is solid, secondary is outline or soft fill, tertiary is ghost or link. Delete among other actions is secondary or tertiary, as a red tint. Delete is solid red only as the primary action of its own confirmation dialog.
- **Balance weight against contrast.** An icon beside text takes a softer colour than the text. A border that is too faint becomes 2px wide rather than darker.

## Group

- **More space around a group than inside it.** Label to input is tighter than field to field. A heading sits closer to its own section than to the one above. An icon sits closer to its count than to the next pair. List items that wrap sit further apart than their own lines.
- **Keep helper text with its label.** Beside a switch, checkbox, radio or other inline control, the label and description form one text stack, spaced by a small step such as 4 or 8px when the project's scale has them. Under an input, the description sits no further from the control than the label does. The larger field-to-field gap goes outside the field. When the project's field component sets these gaps, use them, and correct a gap that is too large in the component's source or theme. Tightening text never shrinks the control's target size.
- **Separate with space first, then a border.** When space alone is not enough, add a soft border: 1px at about 10% of the text colour. Surfaces that already differ in background take no border. Inputs always keep a visible boundary at 3:1 or better.
- **Every gap, size, font size and radius is a scale step.** Change density by choosing other steps or component sizes, so each step keeps one meaning across the project. Pick by elimination: try a step and the steps either side, then re-centre when an outer one wins.
- **Density follows the page type.** App screens are compact; marketing and reading pages are generous. When unsure, match the project's existing components; a project with none yet starts compact for an app and generous for a marketing or reading page. On a generous page, start with too much space and remove it until the layout holds. The grouping rules hold at either density.
- **Content gets the width it needs.** Forms, cards and paragraphs take a max-width. Sidebars, avatars and icons take fixed widths, and only the main region flexes. A section keeps its own width when the nav above it spans the page. Percentages are for elements meant to scale. A narrow form in a wide layout splits into columns.
- **Design for the worst content.** Lay out with the longest name, the longest translated label, an empty list, a very long list and an image of an odd shape. Decide what each one does: wrap, truncate with an ellipsis, or scroll.
- **A component responds to its container.** A component that can sit in a sidebar, panel or dialog uses container queries. Viewport breakpoints are for page-level layout.
- **Parts scale independently.** Headlines shrink faster than body text on small screens. Button height, padding and font size are set per size.
- **Stack with gap**, not margins between siblings. Stacks nest, each with a smaller gap than the one around it: label and description text, then the parts of a field, then the fields. A gap that already spaces text takes no paragraph margins as well.
- **Use start and end** in place of left and right, so the layout flips for right-to-left languages.

## Text

- **Line-height follows line length and size**: about 1.5 for narrow text, up to 2 for wide text, about 1 for large headlines.
- **Paragraphs run 45 to 75 characters**, a max-width of 20 to 35em, even inside a wider layout.
- **Text beside text aligns on the baseline** when the font sizes differ. Icons, avatars and buttons beside text are centred.
- **Numbers in a table column are right-aligned**, in tabular figures, so digits and decimals line up.
- **Text follows the reading direction.** Centred text stays within two or three lines; when one block in a set runs longer, shorten its copy.
- **Letter-spacing** stays at its default, tightened on large headlines and widened on all-caps text.
- **A link inside running text stands out**, and reads as a link by more than colour.
- **Links in link-heavy screens** carry weight or a darker colour in place of the link colour. Ancillary links show their style on hover.
- **Inputs use 16px text on small screens** and 14px from medium screens up. Titles and short descriptions use balanced wrapping.

## Colour

- **Use sites reference role tokens, in pairs**: a surface token with its matching foreground token. Dark mode comes from the same tokens taking other values. A role the theme lacks is added to the theme as a new pair.
- **Three groups**: neutrals for most of the interface, the brand colour for primary actions and active states, accents for status and highlights.
- **Status keeps its meaning.** Success, warning and destructive each have a token pair, shown as strong text on a soft tint of its colour, in either mode, and always paired with an icon, a sign or a word.
- **Colour never carries meaning alone.** Give a change, a state or a category a second cue, such as an icon or a word. Chart series differ in lightness as well as hue.
- **Contrast floor**: 4.5:1 for normal text; 3:1 for large text, input boundaries and focus rings. Large text is 24px and up, or about 19px and up when bold. Check muted text on muted surfaces as its own pair.
- **Measure the ratio from the final colour values.** Run `python3 scripts/contrast.py FOREGROUND BACKGROUND`, from this skill's folder, with the values behind the tokens. List a translucent colour's backdrop after it. A token's name is no evidence that the pair passes.
- **Secondary text on a coloured surface** is a solid colour in the surface's hue. Reduced opacity is acceptable on flat colour only. When the colour nears white before it passes, shift its hue toward a brighter one by up to about 30°.
- **Decoration is quiet on app screens.** Accent borders, tints and patterns stay low in contrast and sit behind the content. Its best use is a cue that tells similar items apart, such as a colour tile or pattern on each row of a file list where only the title differs. Marketing pages use decoration freely. Colour that categorises items comes from a fixed set of category tokens.

## Depth

- **Shadow says which layer.** Choose the layer first: slight for raised controls and cards, medium for menus and popovers, large for dialogs. A closer surface draws more attention.
- **Lighter is closer.** A raised surface is lighter than the page and a well is darker. On a white page, a raised surface stays white and takes its edge from a soft border or shadow.
- **Depth gives feedback.** A dragged item lifts; a pressed button flattens or shifts down 1px.
- **Overlays keep their own stacking order.** Those that fade enter and leave in about 100ms; panels that slide in take about 200ms.

## Components

- **Read a component before composing it**: its docs, its source, and the structure of its parts as they are in this project.
- **Existing parts first, then a variant.** Compose from components the project already has. When they fall short, add a variant or a new component to the project.
- **Change a component's look in this order**: a built-in variant, then a new variant in its source, or in the library's theme when the source is packaged. Change a token's value only when the change belongs everywhere the token is used. Use sites carry layout classes only: width, margin and placement.
- **Use the full structure**: the component's named parts, nested as its docs show.
- **Forms use field parts.** A field wraps its label, control, description and error; a field group spaces complete fields; a fieldset with a legend groups related checkboxes or radios. Use the project's field components when available.
- **The component sizes and spaces its icons.** Icons come from the project's icon set.
- **In components the project owns, compose in place of adding props.** A loading button is a disabled button with a spinner inside it.
- **Feedback uses the project's components**: alert for callouts, badge for status, skeleton for loading.
- **Pick the control by the choice.** A handful of visible options: toggle group. A few exclusive options: radio group, or selectable cards when the choice is central to the screen. A long or searchable list: select or combobox. An on/off setting: switch.
- **Existing parts can hold richer content.** A table column that needs no sorting can merge with a related one, ranked inside the cell, and cells can hold an image or a status. A dropdown can take sections, columns and supporting text.
- **A link styled as a button stays a link element.**
- **After changing a shared component or token, look at its other uses.**

| Need | Overlay |
| --- | --- |
| Focused task that needs input | Dialog |
| Confirming a destructive action | Alert dialog |
| Side panel of details or filters | Sheet |
| Bottom panel on mobile | Drawer |
| Small contextual content on click | Popover |
| Quick information on hover | Hover card |
| Short label for an icon or control | Tooltip |
| List of actions from a trigger | Dropdown menu |
| Brief result of an action | Toast |

Content in a hover card or tooltip is also reachable by keyboard and on touch.

## States

- **Empty**: a title, one line of help and the next action as the primary action. Consider holding tabs and filters back until there is content for them to act on.
- **No results**: a search or filter that matches nothing says so, keeps the query and filters in view, and offers a way to clear them. It is a separate state from empty.
- **Loading**: a skeleton shaped like the content, and a spinner inside the control that is busy.
- **Refreshing**: content already on screen stays there while it reloads, with a small spinner to show the refresh.
- **Failed**: a request that fails shows a message saying what went wrong and a retry action.
- **Invalid**: the field's label and message change, the control is marked for assistive technology, and a message says what is wrong.
- **Focus**: a visible ring on every focusable control, at 3:1 or better against its background.
- **Target size**: every control has a click area of at least 24px, and 44px on touch screens. A small icon keeps its size inside a larger button, and a small control extends its hit area past its visible edge.
- **Names**: every dialog has a title and every field a label, hidden visually when the content speaks for itself.
- **Behaviour**: keyboard handling, focus trapping and ARIA come from the project's headless library. Without one, use native elements such as button, select and dialog, and build a custom widget to its ARIA pattern.
