# shadcn/ui

The branch of [`designing-ui`](SKILL.md) for a project with a `components.json` file. The project owns the component source, so a floor is fixed once in the theme or a component, and every screen inherits it.

Done when the style, base and icon library are named, each failure in the table below has been measured on the project's own values and is fixed or reported as a system finding, and every file the CLI added or changed has been read.

## Read the project

- Run `npx shadcn@latest info --json` for the style, base, icon library, installed components and paths, and `npx shadcn@latest docs <component>` before composing a component.
- **The style is the system for look.** Nova, Vega, Maia, Lyra, Mira, Luma, Rhea and Sera each set density, radius, shadows and control height. A card with only a ring stays flat, and a dialog stays as its style draws it. Emphasis at 500 is the norm; add colour or size where rank needs more.
- A `DESIGN.md` outranks the style, and floors outrank both.

## Floors the defaults miss

Fixes here are system findings, so [Precedence](SKILL.md#precedence) decides when to make them. Run them as one theme pass, then measure each pair in light and dark mode with `scripts/contrast.py`. Figures are the neutral theme in light mode, October 2026, on a white background.

| Floor | Default | Fix |
| --- | --- | --- |
| Input boundary, 3:1 | `--input` measures 1.26. Rhea and Luma use a transparent border, and Sera draws only a bottom edge. | Add `--input-border`, at lightness 0.66 or lower in light mode and about 40% white in dark mode. Point the border classes of installed controls at it. `--input` also paints fills such as the unchecked switch and disabled fields, so it keeps its value. |
| Focus ring, 3:1 | `--ring` measures 2.59. | Lower `--ring` to 0.66 or lower. `focus-visible:border-ring` then draws the passing edge, and the `ring-ring/50` halo stays decoration. |
| Muted text on muted, 4.5:1 | 4.34. | Lower `--muted-foreground` to 0.54 or lower. |
| Delete button tint, 4.5:1 | `text-destructive` on `bg-destructive/10` measures 3.99, and lower on its hover tint. | Darken `--destructive` in light mode until both tints pass, about 0.46. |
| Solid delete in a confirmation | No such variant, no `--destructive-foreground`. White on dark-mode red measures 2.89. | Add the token pair and a `destructive-solid` variant to `button.tsx`, and pass it through `AlertDialogAction`'s `variant` prop. |
| Status tokens | The themes have none for success or warning. | Add both pairs to light and dark, and map them in `@theme inline`. Add matching badge variants. |
| Target size, 24px and 44px on touch | Checkbox and radio are 16px. Default buttons are 28 to 40px. | Extend the hit area with a positioned `after:` element, and grow it under Tailwind's `pointer-coarse:` variant. A label wrapped around its control counts toward the area. |

## Composing

- A card has header, title, description, content and footer. Menu and select items sit inside a group, and tab triggers inside a list.
- A status value takes a status token or status badge variant, so positive and negative stay distinct from each other and from neutral.
- Pull in a shell block once the features show what navigation is needed.

## Keeping local changes

- After `shadcn add`, read the added files, fix their imports and icons to match the project, and point new controls at `--input-border`.
- Update with `add --dry-run` and `add --diff`, keeping local changes file by file.
- `--overwrite` and `shadcn apply` rewrite components, fonts and CSS variables, floor fixes included. Run them with the user's approval, then repeat the theme pass.

## Other shadcn skills

The upstream `shadcn` skill and Vercel's `shadcn` skill own the CLI, component APIs and composition mechanics. This skill owns rank, floors, status and the project's design decisions. Where their defaults differ, such as dark mode by default, Geist, page recipes, neutral status badges or raw colours in variants, the project's system decides first and this skill second.
