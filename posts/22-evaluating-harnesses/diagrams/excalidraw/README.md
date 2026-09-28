# Hand-drawn companions to the post 22 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Sections 1 to 4 are about proxies you run
before shipping and have two figures between them. Section 5 is the one that connects all of it
to the ledger, and it had none.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-output-vs-trajectory` | 960 x 636 | published | One completion scored against one whole run scored, and why the unit had to move. |
| `02-harness-ab-pipeline` | 960 x 560 | published | Section 4: one fixed task set, two harness configs, and a verdict on resolved-rate against cost. |
| `03-production-funnel` | 960 x 622 | published | Section 5: three narrowing stages, each with the metric that measures it. |

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
npm run build:22
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/22-evaluating-harnesses/diagrams/excalidraw/03-production-funnel.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:22` will fight over the same file, so fold anything worth
keeping back into `post22.js`.

## Notes on these

- **The stages narrow and the metric cards do not.** The funnel shape carries the filtering;
  keeping the metric column at constant width stops the figure from implying that the
  measurements get smaller too, when in fact the last one is the largest claim in the post.
- **`02-harness-ab-pipeline` labels its own numbers illustrative, on the drawing.** They match
  the prose exactly -- thirteen points for thirteen cents -- and both are examples rather than
  measurements, which is a distinction a figure is unusually good at losing.
- **`01-output-vs-trajectory` gives both panels the same height.** The trajectory eval is the
  one the post argues for, but drawing it larger would make the case by layout rather than by
  content; the difference that matters is what is inside each panel, not how much room it got.
