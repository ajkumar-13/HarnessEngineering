# Hand-drawn companions to the post 02 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 carries the post's most practical
claim -- that most of the map is inherited, and the leverage sits in the layer you add -- and it
was running on two bullet points and no picture.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-harness-anatomy` | 960 x 560 | published | The map: one loop at the core, four components that feed the model, four that govern it, two at larger scale. |
| `02-layered-harness` | 960 x 636 | published | Section 7: the same eleven components regrouped as the six layers of a shipping system. |
| `03-prebuilt-vs-custom` | 960 x 634 | published | Section 6: what the SDK ships against what your team adds, and the three components that sit on both sides. |

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
npm run build:02
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/02-anatomy-of-a-harness/diagrams/excalidraw/03-prebuilt-vs-custom.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:02` will fight over the same file, so fold anything worth
keeping back into `post02.js`.

## Notes on these

- **`01-harness-anatomy`.** The loop sits in a taller box than any component card, and the stop
  conditions get their own ruled-off block inside it. Both are deliberate: the post's claim is
  that the loop is the core rather than one item in a list of eleven, and that most bugs live in
  the stopping rather than the reasoning.
- **`03-prebuilt-vs-custom`.** Rows two, four, and five line up across the seam because tools
  (02), hooks (07), and permissions (08) genuinely appear on both sides. The prose lists them in
  two separate bullets and leaves the overlap implicit; the figure is where it becomes visible,
  which is the reason this one was worth drawing.
- **The numbers are the component index**, shared with `01-harness-anatomy` and with the post
  numbers in section 8, so a badge in one figure means the same thing in the other.
