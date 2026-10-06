# UI design principles: Refactoring UI + shadcn/ui

2026-10-06 · Alberto

## Scope and sources

This doc holds the UI design rules we kept from two sources, with the points we rejected removed and the nine conflicts between them decided.

| Tag | Source | What was read |
| --- | --- | --- |
| book | Refactoring UI, Adam Wathan and Steve Schoger (2018 PDF) | All 218 pages, figures included |
| shadcn | [shadcn/ui docs](https://ui.shadcn.com/docs) and [repo](https://github.com/shadcn-ui/ui), as of 5 October 2026 | Introduction, [theming](https://ui.shadcn.com/docs/theming), [Typeset](https://ui.shadcn.com/docs/typeset), RTL, [changelog](https://ui.shadcn.com/docs/changelog), the [agent skill rules](https://github.com/shadcn-ui/ui/tree/main/skills/shadcn), component source and the eight style sheets |

A rule tagged "both" appears in the book and is built into shadcn's defaults. "Ours" marks a limit or addition we agreed on while reviewing the two.

## Process

Start with one feature, design it in low fidelity, build it early, and make each small decision once by choosing from a system.

| Rule | In practice | From |
| --- | --- | --- |
| Detail comes later | Sketch rough first. Hold colour back and design in greyscale so spacing, contrast and size carry the hierarchy. | book |
| Work in cycles | Design a simple version, build it, fix what real use exposes, then design the next piece. | book |
| Be a pessimist | Don't show functionality that isn't ready to build. Ship the smallest useful version and design nice-to-haves later. | book |
| Decide the personality once | Typeface, colour, corner radius and tone of voice set it. Keep each one consistent everywhere. | book |
| Limit choices with systems | Define scales for type, spacing, colour, radius and shadow up front, then pick by elimination. | both |
| Own the top layer | Component source lives in the project. Change the component itself instead of overriding it where it is used. | shadcn |
| Read before composing | Check a component's docs and composition tree before using it, not from memory. | shadcn |
| Review what gets installed | Read added files, fix imports and icons to match the project, and never overwrite local changes without approval. | shadcn |
| Start with a feature, not the shell | Design one working feature first, such as a search form. Add a shell block once a few features show what navigation is needed. | book, decided |
| Short path for a small edit | For an edit to one component, read the system, make the change, then check that component and what sits beside it. | ours |

## Hierarchy

Make importance visible by weakening what matters less before enlarging what matters more.

| Rule | In practice | From |
| --- | --- | --- |
| Don't lean on size alone | Use weight and colour too, so primary text isn't huge and secondary text isn't tiny. | book |
| Two or three text colours | Dark for primary, grey for secondary, lighter grey for tertiary. shadcn ships two: `foreground` and `muted-foreground`. | both |
| Emphasise by de-emphasising | When something won't stand out, soften its competitors: inactive nav items, a sidebar's background. | book |
| Labels are a last resort for displayed data | Let format and context identify a value ("12 left in stock"). When a label is needed, make it the quiet part. Weaker for dense admin data and for translated text. | book, with our limit |
| Emphasise the label when people scan for it | Spec sheets and reference pages: darker label, slightly lighter value. | book |
| Titles are often labels | Style by role, not by tag. A page or card title can be small inside an app with clear navigation. A title can be hidden visually but kept for screen readers. | both, with our limit |
| Rank actions by importance | One primary (solid), secondary (outline or soft fill), tertiary (ghost or link). Colour by rank first, meaning second. | both |
| Destructive is not automatically loud | Outside a confirmation step, delete gets a secondary or tertiary treatment. | both |
| Balance weight and contrast | Solid icons beside text get a softer colour. A border that is too faint can go from 1px to 2px instead of darker. | book |
| No weights under 400 for interface text | De-emphasise with colour or size instead. | book |
| Two weights | One normal and one emphasis weight, chosen per typeface and kept. At 500, emphasis also needs colour or size. | both, as proposed |
| Solid red only when confirming | Delete is a solid destructive button inside its confirmation dialog and a red tint everywhere else. | both, as proposed |

## Layout and spacing

Spacing shows what belongs together, so leave more space around a group than inside it.

| Rule | In practice | From |
| --- | --- | --- |
| Group by spacing | Label to input is tighter than field to field. shadcn's Vega style uses 12px inside a field and 28px between fields. Same rule for headings, list items and icon-plus-count pairs. | both |
| Non-linear spacing scale | Steps at least about 25% apart, built on 16px: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 and up. | book |
| Keep the scale's meaning fixed | Change density through component sizes, never by redefining what a spacing step means. | shadcn |
| Don't fill the screen | Give content the width it needs. If a narrow form looks lost, split it into columns instead of stretching it. | book |
| Fixed where content has a natural size | Sidebars, avatars and icons get fixed widths and the main area flexes. Use percentages only when something should scale. | book |
| Don't shrink until needed | Prefer a max-width over grid-column widths, so a card stays at its best size until the screen is narrower. | book |
| Design small first | Start at about 400px wide, then adjust what felt like a compromise on larger screens. | book |
| Scale parts independently | Large headlines shrink faster than body text on small screens. Button height, padding and font size are set per size, not by one ratio. | both |
| Space with gap | Stacks use flex or grid gap, not margins between siblings. | shadcn |
| One spacing value per component | A card's padding and section gap come from one variable, so edge-to-edge content can cancel it exactly. | shadcn |
| Layout classes only where a component is used | Width, margin and placement belong at the call site. Colour and type do not. | shadcn |
| Space first, then a border | Separate with spacing before drawing a line. When space is not enough, add a soft border. Inputs always keep a visible boundary. | both, decided |
| Density follows the page type | Data-heavy app screens are compact. Marketing and reading pages are generous. When unsure, start with too much space and remove it. | both, decided |
| Design for the worst content | Lay out with the longest name, the longest translated label, an empty list, a very long list and an image of an odd shape. Decide what each one does: wrap, truncate with an ellipsis, or scroll. | ours |
| A component responds to its container | A component that can sit in a sidebar, panel or dialog uses container queries. Viewport breakpoints are for page-level layout. | ours |

## Typography

Pick sizes from a short hand-made scale, and set line-height by line length and font size.

| Rule | In practice | From |
| --- | --- | --- |
| Hand-picked type scale | 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72px. Small steps at the bottom, big steps at the top. | book |
| Safe typeface choices | A neutral sans or the system stack. Prefer families with five or more weights. Avoid condensed faces with a short x-height for interface text. | book |
| Line length of 45 to 75 characters | Cap paragraphs at about 20 to 35em, even inside a wider layout. | book |
| Line-height is proportional | About 1.5 for narrow text and up to 2 for wide text. Taller for small text, about 1 for large headlines. | book |
| Baseline for text beside text | Mixed font sizes on one line align by baseline. Icons, avatars and buttons beside text are centred. | book, with our limit |
| Align for reading | Left-align by default, centre at most two or three lines, right-align numbers in tables, hyphenate justified text. | book |
| Letter-spacing | Leave it alone by default. Tighten large headlines and widen all-caps text. | book |
| Not every link needs colour | In link-heavy screens use weight or a darker colour. Ancillary links can show their style only on hover. | book |
| 16px controls on small screens | Inputs use 16px text on mobile and 14px from medium screens up. | shadcn |
| Balanced wrapping | Titles and short descriptions use balanced or pretty text wrapping. | shadcn |
| Rendered markdown has three controls | Size, leading and flow (the space between blocks). Heading sizes, list indents and gaps derive from them, with a preset per context such as chat, docs or reading. | shadcn |
| Streaming-safe prose | A new block must not restyle earlier ones: no last-child or has() layout rules, and spacing only above each block. | shadcn |
| Fixed sizes for interface text | Interface text uses the px or rem scale. Only rendered long-form content sizes itself from its container. | both, as proposed |

## Colour

Components use role tokens instead of raw colours, and every surface token has a matching text token.

| Rule | In practice | From |
| --- | --- | --- |
| Work in OKLCH | Lightness, chroma and hue. Equal lightness looks equally light across hues, which HSL does not give. | shadcn, ours over the book's HSL |
| Role tokens in pairs | `primary` with `primary-foreground`, `card` with `card-foreground`, and so on. The pair is what guarantees readable text on that surface. | shadcn |
| Dark mode swaps values | The same token names are redefined under a dark selector. No per-component dark overrides. | shadcn |
| No raw colours where components are used | Use a token or a variant. If a role is missing, add a token pair to the theme. | shadcn |
| Status gets its own tokens | Add success and warning pairs. Don't drop the meaning, and don't reach for a raw green. | ours, from both |
| Greys can carry a temperature | Tint greys slightly cool or warm and keep the tint consistent. Avoid pure black for text. | both |
| Don't rely on colour alone | Pair colour with an icon, a sign or text. In charts prefer light-versus-dark over different hues. | book |
| Flip the contrast for badges | Dark text on a light tint instead of white text on a strong colour. | both |
| Rotate hue for contrast | For coloured text on a coloured surface, shift toward a brighter hue instead of toward white. | book |
| Secondary text on a coloured surface | On flat colour, reduced opacity is acceptable. Over images or patterns, pick a solid colour in the surface's hue. | book, with our limit |
| Contrast floor | 4.5:1 for normal text, 3:1 for large text, 3:1 for input boundaries and focus rings. Check muted text on muted surfaces separately. | book and ours |
| Shade scale first | Define the shades up front (8 to 10 greys, 5 to 10 per colour), then assign role tokens from that scale. Components still reference roles only. | both, decided |
| Three colour groups | Neutrals for most of the interface, one brand colour for primary actions and active states, and accent colours for status and highlights. | book, decided |
| Decoration is quiet outside marketing pages | On app screens and other non-marketing pages, accent borders, tints and patterns are allowed as long as they are subtle and never pull attention from the content; keep their contrast low. Marketing pages can use decoration much more freely. | book, decided |
| Decoration earns its place as a cue | Its best use is helping people tell similar items apart quickly, such as a pattern or colour tile on each row of a file list where only the title differs. | ours, decided |
| Compute contrast from the final colours | Calculate the ratio from the final colour values. Blend a translucent colour with the surface behind it first. A token's name is no evidence that the pair passes. | ours |

## Depth and surfaces

A shadow says how far a surface sits above the page, so choose it by layer and not by taste.

| Rule | In practice | From |
| --- | --- | --- |
| An elevation scale | About five shadows from small to large: slight for raised controls and cards, medium for menus and popovers, large for dialogs. | both |
| Two-part shadows | A large soft shadow for direct light plus a tight dark one for contact. Fade the tight one as elevation rises. | book |
| Depth as feedback | Lift an item while it is dragged. Flatten or nudge a button when pressed; shadcn shifts it down 1px. | both |
| Lighter is closer | Raised surfaces are lighter than the page and wells are darker. This works without shadows and in dark mode, where a card is lighter than the background. | both |
| Soft edges | Draw a surface's edge as a 1px line at about 10% of the text colour, so it adapts to any background and to dark mode. | shadcn |
| One radius, derived | A single radius value generates the whole scale, and small controls cap their radius so large-radius themes don't distort them. Don't mix square and rounded corners. | both |
| Overlap to create layers | Let a card cross the boundary between two backgrounds. Overlapping images get a border in the background colour. | book |
| Overlays manage their own stacking | Don't hand-set z-index on dialogs, popovers and menus. | shadcn |
| Quick transitions | Overlays enter and leave in about 100ms. | shadcn |

## Components and composition

Components share one composable shape, and their look changes through variants, tokens or their own source.

| Rule | In practice | From |
| --- | --- | --- |
| One interface everywhere | Every component, including wrapped third-party ones, is built from named parts with the same conventions. | shadcn |
| Use the full structure | A card has header, title, description, content and footer. Menu and select items sit inside a group. Tab triggers sit inside a list. | shadcn |
| Change the look in this order | Built-in variant, then a token, then a new variant in the component's source. Not colour or type overrides where it is used. | shadcn |
| Components adapt to their contents | Padding and layout respond to what is inside (an icon, a footer, an image) instead of to extra props. | shadcn |
| Components size their icons | Don't add size or margin classes to icons inside buttons, menus or alerts. Mark the icon's position and let the component space it. | shadcn |
| Compose instead of adding props | A button has no loading prop: put a spinner in it and disable it. | shadcn |
| Don't abstract what always differs | Data tables are built per case from a table primitive and a headless library, not from one do-everything component. | shadcn |
| Forms use field parts | A field wraps label, control, description and error. A field group spaces fields. A fieldset with a legend groups related checkboxes or radios. | shadcn |
| Pick the control by the choice | A handful of visible options: toggle group. Few exclusive options: radio group. Long or searchable list: select or combobox. An on/off setting: switch. | shadcn |
| Semantics still matter | A link styled as a button stays a link element. | shadcn |
| Existing parts first, then a variant | Compose from components the project already has. When they fall short, add a variant or a new component to the project instead of a one-off override. | both, decided |
| Check the other uses of a shared part | After changing a shared component or token, look at the other places that use it. | ours |

| Need | Overlay |
| --- | --- |
| Focused task that needs input | Dialog |
| Confirming a destructive action | Alert dialog |
| Side panel of details or filters | Sheet |
| Bottom panel on mobile | Drawer |
| Small contextual content on click | Popover |
| Quick information on hover | Hover card |

## Images and icons

Every image and icon has a size it was made for, so design around that size instead of scaling it.

| Rule | In practice | From |
| --- | --- | --- |
| Use good photos | Professional or quality stock. Don't design around placeholders you plan to replace with phone shots. | book |
| Text over photos needs even contrast | Add an overlay, lower the image's contrast, colourise it, or put a soft glow behind the text. | book |
| Don't scale icons up | A 16 to 24px icon stays that size inside a tinted shape. shadcn's empty-state and list-item media do this. Otherwise use icons drawn for large sizes. | both |
| Don't scale screenshots or logos down | Capture at a smaller layout, crop to one region, or redraw a simplified version (favicons). | book |
| Control user uploads | Fixed container, image cropped to cover it. A faint inner shadow or semi-transparent inner border stops it bleeding into the background. | book |
| Avatars need a fallback | Show initials when the image fails to load. | shadcn |
| Icons come from the project's set | Use the configured icon library, and pass icons as components and not as string keys. | shadcn |

## States and accessibility

Design the empty, no-results, loading, failed, invalid and focused states with the same care as the filled one.

| Rule | In practice | From |
| --- | --- | --- |
| Empty states are designed | A title, one line of help and the next action. An icon or image is optional. Consider hiding tabs and filters that do nothing yet. | both, with our limit |
| Loading uses placeholders | Skeletons shaped like the content, and a spinner inside the control that is busy. | shadcn |
| Invalid shows in two places | Mark the field so label and message change, and mark the control for assistive technology. Pair the colour with a message. | shadcn and book |
| Every dialog has a title, every field a label | Hidden visually if the content speaks for itself, never removed. | both |
| Visible focus | A ring on every focusable control, at 3:1 or better against its background. | shadcn and ours |
| Behaviour comes from a headless library | Keyboard handling, focus trapping and ARIA come from Base UI, Radix or React Aria. Don't rebuild them. | shadcn |
| Right-to-left ready | Use start and end instead of left and right. Directional icons and slide animations flip. | shadcn |
| Use the feedback components | Alert for callouts, badge for status, skeleton for loading, instead of hand-styled blocks. | shadcn |
| No results is its own state | A search or filter that matches nothing says so, keeps the query and filters in view, and offers a way to clear them. It is a separate state from empty. | ours |
| Refreshing keeps the content | Content already on screen stays there while it reloads, with a small spinner to show the refresh. | ours |
| Failed requests are designed | A request that fails shows a message saying what went wrong and a retry action. | ours |
| Target size | Every control has a click area of at least 24px, and 44px on touch screens. A small icon keeps its size inside a larger button. | ours |
| Look at the states a still page hides | When checking a rendered screen, open each menu and overlay, tab to a control and submit an invalid value, and look at each result. | ours |

## Conflicts and decisions

The two sources pull apart in nine places. Rows 1 to 6 were decided on 6 October 2026 and rows 7 to 9 follow the original proposal.

| # | Question | Book | shadcn | Decision |
| --- | --- | --- | --- | --- |
| 1 | Invent or conform? | "Think outside the box": rich dropdowns, combined table columns, selectable cards instead of radio buttons. | Use existing components first, and built-in variants before custom styles. | Build from existing parts first. When they fall short, add a variant or a new component to the project, not a one-off override. |
| 2 | How is the palette organised? | 8 to 10 greys and 5 to 10 shades per colour, defined up front; pick from the scale. | About 30 role tokens with one value each per mode; no shade scale where components are used. | Shade scale first, then role tokens assigned from it. Components reference roles only. |
| 3 | Lines or space? | Fewer borders: separate with spacing, a background shift or a shadow first. | A ring or border on cards, inputs, tables and menus, plus a separator component. | Space first, then a soft border. Inputs always keep a visible boundary. |
| 4 | Default density | Start with too much white space and remove it; dense is a deliberate exception. | The default preset, Nova, is compact; Rhea was added because teams asked for more density. | Density follows the page type. Apps default compact; marketing and reading pages default generous. The grouping rule holds at any density. |
| 5 | How much colour and decoration? | Choose a brand colour; add accent borders, tinted or patterned backgrounds, brand-coloured checkboxes. | Near-black primary, colour kept for destructive actions and charts, almost no decoration. | Three colour groups: neutrals, one brand colour for primary actions, and accent colours. Decoration is used freely on marketing pages and subtly everywhere else, where it must not pull attention; it is most useful as a cue for telling similar items apart. |
| 6 | Where does design start? | One feature; the shell comes after a few features exist. | Blocks and example prompts start from whole shells such as a dashboard, sidebar or login page. | Design the feature first. Pull in a shell block once the features show what navigation is needed. |
| 7 | Units for text | A fixed px or rem scale; avoid em because relative sizes don't hold across contexts. | Typeset sizes rendered markdown in em from its container. | Fixed scale for interface text. Container-relative sizing only inside rendered long-form content. |
| 8 | Weight for emphasis | Normal at 400 to 500, emphasis at 600 to 700. | Emphasis is 500 almost everywhere. | Two weights only, chosen per typeface and kept. At 500, emphasis also needs colour or size. |
| 9 | Delete inside a confirmation | Solid, bold red when delete is the primary action of the confirmation. | The destructive variant is a red tint in all eight styles. | Add a solid destructive variant for confirmation dialogs and keep the tint elsewhere. |

Each decision is also written as a rule in its own section above.

## Left out on purpose

These six points were rejected in our review and are not rules here.

| Point | From | Why it is excluded |
| --- | --- | --- |
| Light-source highlights on buttons and inset wells | book | A style choice, not a correctness rule, and dated in many current designs. |
| Hand-tuning saturation and rotating hue in HSL to build shades | book | A workaround for HSL. OKLCH gives even lightness directly. |
| De-emphasising text below the contrast floor | book | The book's own tertiary text example is about 4.4:1 on white, under the 4.5:1 it cites (our calculation). |
| Turning a status value into a neutral badge | shadcn | It removes the positive or negative meaning. Add a status token instead. |
| Faint input boundaries and focus rings | shadcn | The default theme measures about 1.26:1 for the input border and 2.59:1 for the focus ring at full strength (our calculation). |
| Assembly recipes as design guidance | shadcn | "Dashboard = Sidebar + Card + Chart + Table" says how to assemble parts, not what to emphasise. |
