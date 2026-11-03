# Foundations

The branch of [`designing-ui`](SKILL.md) for defining or changing the system itself: personality, scales, palette, tokens, radius and shadows. Using a system that already exists is covered in `SKILL.md`.

Done when every item below exists in the project's theme file, each surface and foreground pair has been measured with `scripts/contrast.py` against the contrast floor, and the personality choices are stated to the user.

## Personality

Decide it once, from what the product is and who uses it, and keep each choice consistent everywhere: the typeface, the brand colour, the corner radius, and the tone of voice in the copy. State the four choices before building on them.

- Typeface: a serif reads classic, a rounded sans playful, a neutral sans leaves personality to other elements.
- Radius: none reads formal, small neutral, large playful.
- When undecided, look at what the audience already uses, and keep clear of a direct competitor's look.

## Spacing and size scale

- A non-linear scale built on 16px, with steps at least about 25% apart: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 and up.
- A project on Tailwind already has such a scale; use it as it stands.
- Each step keeps one meaning. Density is a matter of which steps the components use.
- Keep short sets for line-height, border width and opacity too. A minor decision met twice becomes a step.

## Type

- A hand-picked scale in px or rem, on whole pixels: 12, 14, 16, 18, 20, 24, 30, 36, 48, 60, 72. Small steps at the bottom, large steps at the top.
- Interface text uses this fixed scale. Rendered long-form content may size itself from its container; see [`prose.md`](prose.md).
- Typeface: a neutral sans or the system stack, from a family with five or more weights, with a tall x-height and normal width for interface text. Display faces stay at display sizes.
- For a face with more character, shortlist from a font directory's most popular, or from sites whose typography you admire.
- Two weights: a normal one and an emphasis one, chosen for this typeface and kept.

## Colour

Work in OKLCH: lightness, chroma, hue.

1. **Shade scale first.** Define the shades up front: 8 to 10 greys, and 5 to 10 shades for the brand colour and for each accent. Build each scale from three anchors: a base that works as a button background, a darkest shade for text, and a lightest shade for a tint. Fill the midpoints, then the gaps left, and adjust by eye once the shades are in use. Greys take the same route, from the darkest text colour to an off-white page, which lets a white card read as raised.
2. **Then role tokens, assigned from the scale**, in pairs of surface and foreground: background, card, popover, primary, secondary, muted, accent, destructive, plus border, input and ring. Every colour that carries text gets its pair, so a solid destructive button has a foreground token.
3. **Status pairs**: add success and warning beside destructive.
4. **Dark mode**: the same token names take other values under the dark selector.

- Every shade is a fixed entry in the scale, so variations come from the scale and new entries are rare.
- Light hues such as yellow rotate toward orange as they darken, by about 20 to 30°, so dark shades stay rich. OKLCH evens lightness and leaves this to you.
- Add category accents when colour tells similar items apart, such as chart lines, calendar events or tags.
- Greys carry a slight temperature, cool or warm, held consistent across the scale. The darkest text colour is a near-black.
- Three groups: neutrals for most of the interface, one brand colour for primary actions and active states, accents for status and highlights.
- Contrast floor for every pair: 4.5:1 for normal text; 3:1 for large text, input boundaries and focus rings. Measure muted text on the muted surface as its own pair.

## Radius

One radius value generates the whole scale. Small controls cap their radius so a large-radius theme leaves them in proportion. All corners belong to one family, square or rounded.

## Elevation

- About five shadows, small to large: slight for raised controls and cards, medium for menus and popovers, large for dialogs. Set the smallest and largest first, then fill the middle.
- Each shadow has two parts: a large soft one for direct light and a tight dark one for contact. The tight one fades as elevation rises.
- A surface's edge is a 1px line at about 10% of the text colour, so it holds on any background and in dark mode.
- A flat style shows depth with lighter and darker surfaces, or a short solid shadow with no blur.
