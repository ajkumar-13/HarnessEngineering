# Hand-drawn companions to the post 12 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 complains that the three-role
diagram *hides* the hole in the pattern, which is a fair complaint about `01-pge-triangle`. The
remedy was not to redraw that figure but to draw the hole.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-pge-triangle` | 960 x 604 | published | The three roles in one loop, with the evaluator separated from the maker. |
| `02-sprint-contract` | 960 x 576 | published | Section 3: the definition of done frozen before the work, and the three phases around it. |
| `03-the-unchecked-edge` | 960 x 470 | published | Section 6: the same chain, with the one edge nothing grades marked as such. |

Scene filenames match the figures one directory up, because these *are* those figures: the
`.svg` beside each scene is promoted verbatim into `diagrams/` by `node publish.js`, so the
same name means the same picture in both places.

That was not always true. These scenes began as *alternates* -- hand-drawn versions sitting
beside clean Inter-and-arrows vectors, for slides and talks. All seventy-eight are now the
published figure, so there is no second style left to fall back to, and a bad render here is
a bad figure in the post.

## Regenerating

```bash
cd assets/diagrams/excalidraw-generator
npm install
npm run build:12
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/12-planner-generator-evaluator/diagrams/excalidraw/03-the-unchecked-edge.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:12` will fight over the same file, so fold anything worth
keeping back into `post12.js`.

## Notes on these

- **The two brackets are drawn differently on purpose**, and not only in colour: the checked
  edge is a solid bracket below the chain and the unchecked one is dashed and above it, so the
  distinction survives a reader who cannot separate red from green.
- **The chain is linear, where `01-pge-triangle` is a triangle.** A triangle is the right shape
  for showing three roles in tension; a line is the right shape for asking which links have a
  check on them, because it makes the missing one a gap rather than a corner.
- **`01-pge-triangle` sends the failure back along its own lane**, one row below the work
  arrow rather than retracing it, so the revision path is visibly a second trip and not a
  reversal of the first.
