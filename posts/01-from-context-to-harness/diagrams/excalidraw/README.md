# Hand-drawn companions to the post 01 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**. Post 01 already had a picture for each of its two load-bearing claims, so the hand-drawn versions replaced clean vectors rather than filling a gap -- and `03-equation` is new, because the equation the post is named after had never been drawn at all.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-three-eras` | 960 x 568 | published | Section 1: prompt, context, harness -- each era engineers a larger surface because the last one stopped being the bottleneck. |
| `02-nested-rings` | 960 x 592 | published | Section 3: model inside scaffold inside harness inside orchestration, with what each layer owns. |
| `03-equation` | 960 x 524 | published | Section 2: Agent = Model + Harness, and the six things the second term stands for. |

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
npm run build:01
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/01-from-context-to-harness/diagrams/excalidraw/01-three-eras.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:01` will fight over the same file, so fold anything worth
keeping back into `post01.js`.

## Notes on these

- **`01-three-eras`.** The three bars under the panels are drawn to scale against each other,
  so the growth of the engineered surface is a measurement rather than a claim: one message,
  then the window, then window plus loop plus tools plus state plus checks plus guards.
- **`02-nested-rings`.** The rings nest rather than stack, because the argument is containment:
  a harness contains a scaffold contains a model. A row of boxes would say "these are four
  things", which is the reading section 3 spends its length arguing against.
- **`03-equation`.** The harness box is wider than the model box on purpose. The point of the
  equation is that the second term is the larger one, and the one you can actually change.
