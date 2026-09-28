# Hand-drawn companions to the post 26 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**. The capstone needs a picture of each of three things -- what the harness is made of, how state survives a context reset, and the loop that improves the harness rather than the model -- and these are those three, drawn to carry the run the companion actually produces rather than a sketch of one.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-capstone-architecture` | 960 x 470 | published | Every component of the series in one harness, each card carrying the post it comes from: spec, Ralph driver, the three roles, the Build #2 gates, the two durable stores, the tracer and the cost meter. |
| `02-multi-context-run` | 960 x 556 | published | Section 3: three fresh windows above the line, two durable stores below it, and a dotted divider at each context reset. |
| `03-eval-observability-loop` | 960 x 580 | published | Section 7: run, evaluate, localise, ratchet, and a dashed return leg back to the run, with the model fixed the whole way round. |

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
npm run build:26
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/26-capstone-coding-agent/diagrams/excalidraw/02-multi-context-run.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:26` will fight over the same file, so fold anything worth
keeping back into `post26.js`.

## Notes on these

- **`01-capstone-architecture` labels every card with the post it comes from.** The capstone's
  job is to be a map back into the series, so a card that says only what it does is doing half
  the work; the post number is the other half.
- **`02-multi-context-run` puts the discard line across the whole canvas.** The three task
  cards are dashed because they are temporary and the two stores are solid because they are not,
  but the line is what makes the claim, and it has to span everything for that to read.
- **The per-gap `reset` labels were removed after the first render.** There are 20px between
  task cards, which is not enough for a word, and the label was clipping into the next card.
  The dotted divider carries the boundary and the caption names it instead.
- **`03-eval-observability-loop` draws the return leg dashed and the forward legs solid.** The
  forward path happens inside one turn of the cycle; the return leg is the part that only
  happens because someone acts on what the traces said, and the weight difference says so.
- **The stage arrows sit in the gap, not across it.** The first render ran each arrow 34px into
  the following card, which reads as a connector drawn over a box rather than between two.
