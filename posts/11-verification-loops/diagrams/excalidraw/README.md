# Hand-drawn companions to the post 11 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 2 ranks the kinds of ground truth
and section 6 says how often to run each; those are the same table seen from two sides, and
neither section had a figure.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-verification-gate` | 960 x 560 | published | A gate on the loop exit: pass and the run ends verified, fail and the report re-enters the loop. |
| `02-compounding-vs-failfast` | 960 x 612 | published | Section 5: the same five-step task with and without a per-step check. |
| `03-verifier-ladder` | 960 x 490 | published | Sections 2, 3 and 6: five verifiers with their cost, whether they can be wrong, and how often to run each. |

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
npm run build:11
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/11-verification-loops/diagrams/excalidraw/03-verifier-ladder.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:11` will fight over the same file, so fold anything worth
keeping back into `post11.js`.

## Notes on these

- **The dashed line is the figure.** The rows are ordered by strength, but the line is drawn on
  a different question: can this verifier be wrong? Above it a failure is a fact; below it a
  verdict is an opinion that can fail in the direction the agent would prefer.
- **Self-critique is on the drawing at all**, which a ladder of "ground truth" would exclude.
  Section 3 argues it is worth a first pass and never the last word, and that is a position on
  the table rather than an absence from it.
- **`02-compounding-vs-failfast` colours only the failing rows.** The right-hand panel has one
  coloured row out of five, which is the whole economic argument: the blast radius is one step.
