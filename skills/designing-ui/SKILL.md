---
name: designing-ui
description: Designing user interfaces. Use when building or restyling a screen or component, creating or changing a theme or design tokens, or reviewing how a UI looks.
---

A screen reads well when three things hold. **Rank**: the eye lands on what matters most, because everything else was made quieter. **Group**: things that belong together sit closer to each other than to anything else. **Scale**: every size, gap, radius, shadow and colour is a step from the project's system, chosen by comparing neighbouring steps.

Run the steps in order. The reference sections under them are what the steps apply, and step 7 checks every one.

Three more bodies of reference live in sibling files. Read each when its condition holds:

- [`foundations.md`](foundations.md): the project has no tokens or scales yet, or the task creates or changes a theme, palette, type scale, spacing scale, radius or shadows.
- [`images.md`](images.md): the screen places a photo, a user-uploaded image, a screenshot, a logo, or an icon larger than 24px.
- [`prose.md`](prose.md): the screen shows long-form text or rendered markdown, such as an article, a docs page or a chat message.

## Steps

1. **Read the system.** Find, in the project's own files, its tokens, spacing and type scales, component library, icon set, and whether it has a dark mode. Done when you can name the tokens, scale steps and components this work will use, or have found that none exist and read `foundations.md`.
2. **Name the feature and the page type.** Design the one feature asked for, and include only what works now or what you are building now; navigation appears once there are real destinations for it. Then name the page type: an _app_ screen, or a _marketing or reading_ page. Done when the feature fits in one sentence, the page type is named, and every element on your list does something real.
3. **Rank.** Before styling anything, give every piece of content and every action a rank: primary, secondary or tertiary. Done when each element has a rank and each view has exactly one primary action, or none.
4. **Structure without colour.** Lay the feature out with spacing, size and weight alone, at about 400px wide first and then wider. Done when the rank order is readable in greyscale, every gap is a scale step with more space around each group than inside it, and the layout holds with the worst content the screen can receive.
5. **Colour, depth and decoration.** Add them through role tokens and component variants. Done when every colour at a use site is a role token or a variant, and every text and surface pair meets the contrast floor by calculation.
6. **States.** Design the empty, no-results, loading, failed, invalid and focused state of every region that depends on data or input. Done when each such region has every state that applies to it.
7. **Look and correct.** Render the screen and look at it, narrow and wide, and in dark mode when the project has one. Then open each menu and overlay, tab to a control and submit an invalid value, and look at each result. Walk every rule in the reference sections against what you see and fix what fails. Done when each rule is met, or its exception is reported to the user with the reason. When you cannot render the screen, say so in your report.

To review an existing UI, run step 1, then run step 7 across the whole screen, and report findings rule by rule, most visible first.

For a small edit to one component, run step 1, make the change, then run step 7 on that component and what sits beside it.

## Rank

- **Quieten the competition first.** When the primary thing fails to stand out, soften what competes with it (inactive nav items, a sidebar's background) before making it larger.
- **Weight and colour carry rank as much as size.** Primary text is dark and heavier at a moderate size; secondary text takes the muted text token; tertiary text is smaller. Use two weights per typeface, a normal one and an emphasis one. When the emphasis weight is 500, add colour or size to it.
- **Displayed data speaks for itself.** Let format and context identify a value: "12 left in stock", an email address, a role under a name. When a label is needed, the label is the quiet part and the value the loud one. Reverse that on spec sheets, where people scan for the label. Keep explicit labels in dense admin data and in translated text.
- **A title takes the size its rank earns.** A page or card title inside an app is often small, whatever its tag. A title the content makes redundant stays in the markup for screen readers and is hidden visually.
- **Actions are styled by rank.** Primary is solid, secondary is outline or soft fill, tertiary is ghost or link. Delete among other actions is secondary or tertiary, as a red tint. Delete is solid red only as the primary action of its own confirmation dialog.
- **Balance weight against contrast.** An icon beside text takes a softer colour than the text. A border that is too faint becomes 2px wide rather than darker.

## Group

- **More space around a group than inside it.** Label to input is tighter than field to field. A heading sits closer to its own section than to the one above. An icon sits closer to its count than to the next pair.
- **Separate with space first, then a border.** When space alone is not enough, add a soft border: 1px at about 10% of the text colour. Inputs always keep a visible boundary at 3:1 or better.
- **Every gap, size, font size and radius is a scale step.** Change density by choosing other steps or component sizes, so each step keeps one meaning across the project.
- **Density follows the page type.** App screens are compact; marketing and reading pages are generous. When unsure, start with too much space and remove it.
- **Content gets the width it needs.** Forms, cards and paragraphs take a max-width. Sidebars, avatars and icons take fixed widths, and only the main region flexes. A narrow form in a wide layout splits into columns.
- **Design for the worst content.** Lay out with the longest name, the longest translated label, an empty list, a very long list and an image of an odd shape. Decide what each one does: wrap, truncate with an ellipsis, or scroll.
- **A component responds to its container.** A component that can sit in a sidebar, panel or dialog uses container queries. Viewport breakpoints are for page-level layout.
- **Parts scale independently.** Headlines shrink faster than body text on small screens. Button height, padding and font size are set per size.
- **Stack with gap, and use start and end** in place of left and right, so the layout flips for right-to-left languages.

## Text

- **Line-height follows line length and size**: about 1.5 for narrow text, up to 2 for wide text, about 1 for large headlines.
- **Paragraphs run 45 to 75 characters**, a max-width of 20 to 35em, even inside a wider layout.
- **Text beside text aligns on the baseline** when the font sizes differ. Icons, avatars and buttons beside text are centred.
- **Numbers in a table column are right-aligned.** Centred text stays within two or three lines; longer text is left-aligned.
- **Links in link-heavy screens** carry weight or a darker colour in place of the link colour. Ancillary links show their style on hover.
- **Inputs use 16px text on small screens** and 14px from medium screens up. Titles and short descriptions use balanced wrapping.

## Colour

- **Use sites reference role tokens, in pairs**: a surface token with its matching foreground token. Dark mode comes from the same tokens taking other values. A role the theme lacks is added to the theme as a new pair.
- **Three groups**: neutrals for most of the interface, the brand colour for primary actions and active states, accents for status and highlights.
- **Status keeps its meaning.** Success, warning and destructive each have a token pair, shown as dark text on a light tint, and always paired with an icon, a sign or a word.
- **Contrast floor**: 4.5:1 for normal text; 3:1 for large text, input boundaries and focus rings. Check muted text on muted surfaces as its own pair.
- **Compute the ratio from the final colour values.** Blend a translucent colour with the surface behind it first. A token's name is no evidence that the pair passes.
- **Secondary text on a coloured surface** is a solid colour in the surface's hue. Reduced opacity is acceptable on flat colour only.
- **Decoration is quiet on app screens.** Accent borders, tints and patterns stay low in contrast and sit behind the content. Its best use is a cue that tells similar items apart, such as a colour tile or pattern on each row of a file list where only the title differs. Marketing pages use decoration freely.

## Depth

- **Shadow says which layer.** Slight for raised controls and cards, medium for menus and popovers, large for dialogs.
- **Lighter is closer.** A raised surface is lighter than the page and a well is darker, in light and dark mode alike.
- **Depth gives feedback.** A dragged item lifts; a pressed button flattens or shifts down 1px.
- **Overlays keep their own stacking order** and enter and leave in about 100ms.

## Components

- **Read a component before composing it**: its docs, its source, and the structure of its parts as they are in this project.
- **Existing parts first, then a variant.** Compose from components the project already has. When they fall short, add a variant or a new component to the project.
- **Change a component's look in this order**: a built-in variant, then a token, then a new variant in its source. Use sites carry layout classes only: width, margin and placement.
- **Use the full structure.** A card has header, title, description, content and footer. Menu and select items sit inside a group, and tab triggers inside a list.
- **The component sizes and spaces its icons.** Icons come from the project's icon set.
- **Compose in place of adding props.** A loading button is a disabled button with a spinner inside it.
- **Pick the control by the choice.** A handful of visible options: toggle group. A few exclusive options: radio group. A long or searchable list: select or combobox. An on/off setting: switch.
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

## States

- **Empty**: a title, one line of help and the next action. Consider holding tabs and filters back until there is content for them to act on.
- **No results**: a search or filter that matches nothing says so, keeps the query and filters in view, and offers a way to clear them. It is a separate state from empty.
- **Loading**: a skeleton shaped like the content, and a spinner inside the control that is busy.
- **Refreshing**: content already on screen stays there while it reloads, with a small spinner to show the refresh.
- **Failed**: a request that fails shows a message saying what went wrong and a retry action.
- **Invalid**: the field's label and message change, the control is marked for assistive technology, and a message says what is wrong.
- **Focus**: a visible ring on every focusable control, at 3:1 or better against its background.
- **Target size**: every control has a click area of at least 24px, and 44px on touch screens. A small icon keeps its size inside a larger button.
- **Names**: every dialog has a title and every field a label, hidden visually when the content speaks for itself.
- **Behaviour**: keyboard handling, focus trapping and ARIA come from the project's headless library.
