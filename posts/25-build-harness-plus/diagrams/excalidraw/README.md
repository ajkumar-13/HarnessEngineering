# Hand-drawn companions to the post 25 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The build had a picture of what it adds and
a picture of what that buys, and none of section 10, which is the most useful section in the post:
three bugs that shipped in this very companion behind a passing suite. The section's argument is
that the three share a shape, and a shape is the one thing prose states and a figure shows.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-layered-harness` | 960 x 434 | published | The unchanged Build #1 core, the three gates a call passes through in order, the sub-agent, and the tracer wrapped around all of it. |
| `02-blast-radius` | 960 x 604 | published | Section 8: the same wrong call in both builds, reaching everything on the left and stopping at one of three gates on the right. |
| `03-what-tests-miss` | 960 x 464 | published | Section 10: three real defects, each beside the property its test actually asserted and the neighbouring property the defect lived in. |

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
npm run build:25
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/25-build-harness-plus/diagrams/excalidraw/03-what-tests-miss.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:25` will fight over the same file, so fold anything worth
keeping back into `post25.js`.

## Notes on these

- **`03-what-tests-miss` puts PASSES and SHIPPED ANYWAY on the same row, at the same size.**
  The point of the section is that both were true at once. Drawing the failure larger, or in
  alarm colour alone, would turn a claim about test design into a claim about severity.
- **The fourth column is the figure's reason to exist.** The first three columns restate the
  post; the gap column is the generalisation, and reading down it gives the section's thesis
  in three phrases: tested with the traffic you expect, asserted the shape and never the
  contents, tested with its own source material.
- **Each row takes its layer's colour, not a severity colour.** The sandbox row is accent, the
  tracer row primary, the deny-list row alert, matching how those three layers are drawn
  everywhere else in the post, so the reader is not asked to learn a second colour language.
- **All three canvases shrank after the first render.** Footers that overran their declared
  width, and cards with dead space under the last line, are both invisible until a PNG is
  rasterised and looked at; `fit()` reports the first and cannot see the second.
