# One page of harness engineering

One scene, in two forms:

| File | What it is |
|---|---|
| `one-page-of-harness-engineering.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `one-page-of-harness-engineering.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Twenty-six posts on one canvas, in seven panels: the claim the series is built on, the
eleven components in the three bands they fall into with the loop at the centre, the four
exits checked after every turn, the six failure modes, the verifier ladder, what survives a
context reset, three measured costs, and the order to build the whole thing in. At 1200 by
1700 it sits three pixels off the A-series ratio, which is to say it prints at A2 without a
crop worth noticing.

It is not a larger version of post 02's anatomy figure. That figure answers "what is a
harness made of"; a poster is read standing up and out of order, so this one also has to
answer how it stops, how it fails, what it costs, and what order to build it in.

Three things about it are worth knowing before you edit it.

- **The type is smaller than the per-post figures.** A poster holds about four times as
  much text in the same column and Excalifont runs wide, so body sits at 11–12 where a
  figure would use 13.

- **Text on a coloured fill uses `--ce-on-accent`,** which is dark ink in both themes, not
  `--ce-on-fill`. The component badges are the only text on a fill here, and they are set
  at 8.5, so they need the contrast rather than merely benefiting from it.

- **Every number is carried from a post that sources it, and the post number is printed
  beside it.** `$0.94` against `$0.33` is post 23 §6; `20 min, $9` against `6 h, $200` is
  post 12 §9; `97%` and `17% to 5%` are post 15 §8; `max_iters = 12` and
  `no_progress_window = 3` are the defaults in `code/03-agent-loop`, not round numbers
  chosen to look tidy. Nothing on the sheet is illustrative. If you add a figure, add its
  post number with it, or the sheet stops being checkable.

## Regenerating

The generator lives at `assets/diagrams/excalidraw-generator/`, alongside the twenty-six
that draw the per-post companions:

```bash
cd assets/diagrams/excalidraw-generator
npm install
npm run build:poster
```

Every element carries a seed derived from its index, so a rebuild is byte-identical.
Nothing here depends on a random number, which is what keeps a regeneration from showing up
as a diff.

**Render it and look at it before you commit.** Three of the faults in the first cut of this
sheet were invisible in the build output and obvious in a PNG: `circle()` takes a radius and
was being passed a diameter, so the badges swallowed their own digits; the failure panel's
last line was cut by its own bottom border; and its first row was drawn on top of the panel
subtitle. `fit()` reports none of that. It measures a string against a width; it cannot see
what is already drawn where the string lands.

```bash
node preview.js ../../../poster/one-page-of-harness-engineering.svg /tmp/poster.png
node preview.js ../../../poster/one-page-of-harness-engineering.svg /tmp/poster-dark.png dark
```

Check both. The palette inverts through the token block, so a mistake that only shows in one
mode is easy to ship.

## Editing it by hand instead

The `.excalidraw` file is a real scene, so you can open and edit it. How it saves depends on
where you open it:

- **The VS Code Excalidraw extension** edits the file in place. Ctrl-S and the scene on disk
  is your edit. This is the one to use.
- **excalidraw.com** works on a copy in browser storage. Your change is not on disk until
  you use *File → Save to...* and overwrite the original.

Then re-render, from the generator directory:

```bash
cd assets/diagrams/excalidraw-generator
npm run render -- ../../../poster/one-page-of-harness-engineering.excalidraw
```

It writes the SVG next to the scene, inheriting the canvas size, `<title>` and `<desc>` from
the file already there, so an edit does not cost you the accessible description.

**Do not use Excalidraw's own Export to SVG.** It bakes literal hex into every shape, and the
whole point of the renderer here is that it emits `var(--ce-ink)` and friends so one file
serves light and dark mode. An exported SVG looks right in whichever mode you exported from
and wrong in the other.

Two more things worth knowing before you edit:

- **`npm run build:poster` overwrites hand edits.** The generator is the source of truth and
  it does not read the scene, it replaces it. Once you start editing by hand, either stop
  running the build script or fold the change back into `poster.js`. For anything
  structural, `poster.js` is the better place to make it.
- **Colours picked from Excalidraw's palette will not follow the theme.** Only the `--ce-*`
  values map back to CSS variables; anything else is baked in as a literal and will be wrong
  in one of the two modes.

## A note on where this lives

`HARNESS-PLAN.md` §6 names this sheet `assets/poster/harness-anatomy.svg`. It is here
instead, at `poster/` in the repository root, because that is where the sibling Context
Engineering series keeps its one-pager and where `build:poster` has always pointed. The plan
is stale on the path, not on the requirement.
