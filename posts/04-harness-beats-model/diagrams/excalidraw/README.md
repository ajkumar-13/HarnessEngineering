# Hand-drawn companions to the post 04 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 is where the post stops arguing
and tells you what to do, and it is an *ordered* procedure whose whole content is the order.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-harness-gap` | 960 x 580 | published | Section 2: one model at two leaderboard ranks, with the reported figures labelled as reported. |
| `02-cotraining-flywheel` | 960 x 582 | published | Section 5: the four-step loop between harness patterns and model training, and why a model feels sharper in its native harness. |
| `03-choose-model-order` | 960 x 470 | published | Section 6: the five moves in order, the cost of each rung, and the jump most teams actually make. |

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
npm run build:04
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/04-harness-beats-model/diagrams/excalidraw/03-choose-model-order.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:04` will fight over the same file, so fold anything worth
keeping back into `post04.js`.

## Notes on these

- **`01-harness-gap` charts one number and no more.** The post's own rule is that reported
  figures stay labelled as reported, so the figure draws the single attributable data point --
  a rank move -- rather than inventing per-harness scores to make a prettier chart.
- **`03-choose-model-order` puts a cost on every rung**, because that is what makes the order
  an argument rather than a preference. Steps 1 to 3 are one-off costs in engineer-hours; step
  4 is a recurring cost per token, forever. The dashed arrow is the move teams actually make.
- **Step 4 is the only rung drawn in the alert colour**, and it is also the only one with a
  heavier border, so the emphasis survives a reader who cannot separate the hues.
