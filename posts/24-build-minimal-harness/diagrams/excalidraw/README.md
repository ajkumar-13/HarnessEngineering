# Hand-drawn companions to the post 24 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The build had a picture of what it is
(section's architecture) and a picture of what it does (one task run), and none of the claim it
actually rests on: that four injected seams make the swap to production cheap. Section 9 carried
that on a table alone, and a seam is a two-sided thing, which is what a figure is for.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-minimal-architecture` | 960 x 430 | published | The four primitives wired together: the loop at the centre, the model on one side, the tools and the gate on the other, and the four exits along the bottom. |
| `02-task-run-sequence` | 960 x 590 | published | Section 5: declared done, failed, informed, verified. The two middle steps are the ones that separate a shipped bug from a finished task. |
| `03-the-four-seams` | 960 x 506 | published | Section 9: each seam with the double the tests inject, the implementation production injects, and the blast radius the swap opens. |

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
npm run build:24
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/24-build-minimal-harness/diagrams/excalidraw/03-the-four-seams.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:24` will fight over the same file, so fold anything worth
keeping back into `post24.js`.

## Notes on these

- **`03-the-four-seams` puts the risk in its own column rather than in a footnote.** The table
  in the post lists what changes; the figure's fourth column is the part readers skip in prose,
  and giving it equal width is the whole reason to draw the section at all.
- **The shell-runner row is drawn heavier and labelled WIDEST.** All four seams swap with the
  same one-line move, so nothing in the shape distinguishes them; the weight is the only thing
  saying that one of the four is not like the others.
- **The workspace row says `not shipped` rather than leaving the cell empty.** An empty cell
  reads as an oversight in the figure; the point is that the omission is in the build.
- **`01-minimal-architecture`'s return path is labelled to the left of its own arrow.** The
  first render put the caption where it overlapped the gate card, which `fit()` cannot catch
  because it measures text against a width and not against what is already drawn there. Render
  a PNG and look at it; that is the only check for this class of fault.
