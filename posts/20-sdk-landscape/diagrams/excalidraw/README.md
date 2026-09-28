# Hand-drawn companions to the post 20 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The post opens with a feature matrix and
then spends a section explaining why a feature matrix is the wrong instrument, which left the
recommended alternative as the one thing in the post with no picture.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-sdk-feature-matrix` | 960 x 620 | published | Six harness components against four ways of getting them, marked illustrative rather than current. |
| `02-build-vs-buy` | 960 x 612 | published | Section 4: two gates between needing a harness and choosing how to get one. |
| `03-harness-ab` | 960 x 636 | published | Section 6: the A/B that settles the choice, the two things it quietly measures as well, and the arithmetic that says whether the gap it found is real. |

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
npm run build:20
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/20-sdk-landscape/diagrams/excalidraw/03-harness-ab.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:20` will fight over the same file, so fold anything worth
keeping back into `post20.js`.

## Notes on these

- **`03-harness-ab` carries section 6's worked numbers, and the panel that undercuts them.**
  The first cut named the four numbers and gave none of them, on the reasoning that inventing
  completion rates is the sin the section argues against. But the section works a comparison
  through -- 61 against 68 of 100 runs, at $0.42 and $0.61 -- and then spends a bullet showing
  the 7-point gap is about 1.5 standard errors on a denominator that is really 20 tasks, not 100
  runs. Without that bullet the figure promised a verdict the post declines to give, and read
  against Post 22 fig 2, which finds p = 0.39 on a *larger* task set, the two sheets disagreed.
  completion rates would be exactly the sin the section is arguing against, and the figure is
  about the method rather than about a result.
- **The two cautions are on the figure, not under it.** An A/B diagram without them reads as a
  clean experiment, and the section's real content is that it is not one: you are partly
  measuring the model-and-harness pairing, and the migration cost sits somewhere else entirely.
- **`01-sdk-feature-matrix` labels its own columns generically** -- a batteries-included SDK,
  a provider agent SDK, a graph framework -- rather than naming products in cells that would be
  wrong within months. The post names the products in prose, where they can be dated.
