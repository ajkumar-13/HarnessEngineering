# Hand-drawn companions to the post 18 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The existing figures draw the loop from
outside. Neither draws what one iteration's context is actually made of, which is where the
re-entry tax, the cacheable prefix, and the read-only spec all live.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-ralph-loop` | 960 x 584 | published | Fresh context, one task, commit, reset, repeat, with the spec and repo persisting across every pass. |
| `02-multi-context-timeline` | 960 x 620 | published | Section 4: a bounded sawtooth of context usage against a staircase of progress on disk. |
| `03-inside-one-iteration` | 960 x 490 | published | Sections 2 and 3: the context stack, how to size a task, and which files the loop may edit. |

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
npm run build:18
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/18-long-horizon-ralph/diagrams/excalidraw/03-inside-one-iteration.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:18` will fight over the same file, so fold anything worth
keeping back into `post18.js`.

## Notes on these

- **The stack is drawn in the order the context is built**, stable first, because the order is
  the argument. Cached blocks at the top and rebuilt blocks below is not a taxonomy, it is the
  layout that makes the prefix cacheable, and a figure that grouped them any other way would
  lose the point.
- **The sizing panel puts all three bars against one window limit.** "Too large" and "too
  small" are failures on different axes -- overflow and overhead -- and drawing them on a
  shared scale is what shows that the right slice is a range rather than a number.
- **`02-multi-context-timeline` draws the unmanaged context as a straight climb across the
  limit**, deliberately without a reset, so the two curves differ in shape rather than only in
  height. The sawtooth stays under the line; the straight line does not.
