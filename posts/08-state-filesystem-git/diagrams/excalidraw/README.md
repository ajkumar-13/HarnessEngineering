# Hand-drawn companions to the post 08 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Sections 5 and 6 are the ones a reader has
to apply, and they are the same decision stated twice: state has a right place, decided by
*when* it is needed rather than by how big it is.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-filesystem-durable-state` | 960 x 560 | published | The small volatile window beside a durable filesystem under git, with commit as checkpoint and revert as rollback. |
| `02-handoff-lifecycle` | 960 x 588 | published | Section 4: one file carrying spec, progress and next steps across a context reset. |
| `03-where-state-belongs` | 960 x 470 | published | Sections 5 and 6: which state goes where, and the two mirror-image mistakes. |

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
npm run build:08
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/08-state-filesystem-git/diagrams/excalidraw/03-where-state-belongs.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:08` will fight over the same file, so fold anything worth
keeping back into `post08.js`.

## Notes on these

- **The window in `01-filesystem-durable-state` is drawn small, and says so.** The figure is
  about a size asymmetry, and a window box the same size as the disk box would quietly deny the
  argument it is illustrating.
- **`03-where-state-belongs` sorts by timing, not by size.** A one-line rule the model must
  honour every turn belongs in the window although it is tiny; a small intermediate result
  nobody reads again belongs on disk. Sorting by size is the proxy that produces both mistakes,
  which is why the axis is labelled with *when*.
- **The two mistakes are drawn as a pair, at equal weight.** The over-correction is as common
  as the original error and gets the same amount of ink, which a bulleted list under a single
  "anti-patterns" heading does not manage.
