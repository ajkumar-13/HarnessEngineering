# Hand-drawn companions to the post 13 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**. One of them *replaces* a clean vector rather than restating it, and it is the only figure in the series that does: the old one was wrong.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-hook-lifecycle` | 960 x 500 | published | The four points, each marked by whether it can block, supply, or only report. |
| `02-blocked-command` | 960 x 616 | published | A pre-tool deny-list stopping a destructive command before it reaches the shell. |
| `03-gates-and-reports` | 960 x 460 | published | Section 3: the gate and the report as two signatures with two composition rules. |

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
npm run build:13
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/13-hooks-enforcement/diagrams/excalidraw/01-hook-lifecycle.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:13` will fight over the same file, so fold anything worth
keeping back into `post13.js`.

## Notes on these

- **`01-hook-lifecycle` was redrawn because the old one made a claim the post now corrects.**
  The clean vector labelled the post-edit hook "(can reject)"; a post-tool hook surfaces a
  message to the model and cannot undo the write. It also drew three lifecycle points where the
  post names four. The sketch is drawn to the corrected prose and promoted over it.
- **The power of each point is written in words on a pill, not carried by colour.** The four
  hues are there to link the bar on the loop to its card; "CAN BLOCK THE CALL" against
  "REPORTS ONLY" is what a reader actually needs, and it survives a greyscale print.
- **`03-gates-and-reports` puts the composition rule next to the return type**, because one
  causes the other: a verdict has a first-match short circuit, a finding does not, and a hook
  system that shares one type between them will get exactly that wrong.
