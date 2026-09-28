# Hand-drawn companions to the post 21 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 3 claims failures "deform the shape
in characteristic ways" and then names four deformations in prose, which is the one claim in
this post that a picture can settle outright.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-trace-tree` | 960 x 684 | published | One run as a waterfall of nested spans, with the slow tool call flagged. |
| `02-trace-to-ratchet` | 960 x 560 | published | Section 4: a trace localised to a component, then converted into a rule, a hook, and a replay. |
| `03-trace-shapes` | 960 x 470 | published | Section 3: a healthy shape, and the four ways a named failure mode deforms it. |

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
npm run build:21
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/21-observability-traces/diagrams/excalidraw/03-trace-shapes.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:21` will fight over the same file, so fold anything worth
keeping back into `post21.js`.

## Notes on these

- **The healthy shape is drawn once and at full width**, above the four failures, because
  every deformation is relative to it. Four failure panels with no reference would be four
  patterns rather than four deviations.
- **The victory declaration panel draws an absence.** A dashed empty slot where the gate span
  should be is the only honest way to render a failure whose signature is that nothing is
  there, and it is the panel that most repays being a picture rather than a sentence.
- **No panel carries numbers.** These are shapes, not measurements, and putting token counts
  on them would invite a reader to check the arithmetic instead of learning the geometry.
