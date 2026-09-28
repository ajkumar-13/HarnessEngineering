# Hand-drawn companions to the post 23 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The post prices a run from three angles and
then ends on a decision, and the decision was the part running on prose alone: sections 1 to 8
carry the arithmetic between two figures, and section 9 turns all of it into a build-or-rent
call that had no picture at all.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-loop-cost` | 960 x 596 | published | Section 1: per-iteration cost climbing as each turn re-reads a context that grew the step before, with caching flattening the re-read of the stable prefix. |
| `02-llm-api-vs-haas` | 960 x 612 | published | Section 8: where the service boundary sits, with the loop, tools, context management and hooks outside it for an LLM API and inside it for a harness API. |
| `03-build-vs-rent` | 960 x 486 | published | Section 9: the three questions that decide build against rent, with the rent case and the build case for each, and differentiation marked as the one that overrides the other two. |

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
npm run build:23
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/23-economics-haas/diagrams/excalidraw/03-build-vs-rent.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:23` will fight over the same file, so fold anything worth
keeping back into `post23.js`.

## Notes on these

- **`03-build-vs-rent` marks one card as the deciding question and draws the other two the
  same.** Volume and control are cost questions a team can compute; differentiation is a
  question about what the product is. Giving the third card a heavier spine and a label, rather
  than more space, keeps the three readable as one comparison while saying which one wins.
- **The cards grew after the first render.** At 240 tall the coloured footer line in each card
  sat a few pixels past the card's own bottom edge, which `fit()` cannot see because it measures
  text against a width, not against the box it is drawn in. Rendering a PNG and looking at it is
  the only check that catches this; the cards are 264 tall for that reason.
- **`01-loop-cost` splits every bar into the re-read and the new tokens.** The post's argument is
  that the growth is in the part you already paid to produce, so drawing one flat bar per
  iteration would have hidden exactly the quantity the section is about.
- **`02-llm-api-vs-haas` keeps both panels the same size.** What changes between them is which
  side of the boundary the four components sit on, not how much there is of them.
