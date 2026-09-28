# Hand-drawn companions to the post 14 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 5 is the section this post gained
from finding a real bug in the Build #2 companion, and it is the one a reader is most likely to
have in their own harness.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-sandbox-boundary` | 960 x 578 | published | The box, its five constraints, and the host system drawn deliberately out of reach. |
| `02-injection-defence` | 960 x 614 | published | Section 4: one injected instruction meeting four layers, each holding on its own. |
| `03-which-gate-fired` | 960 x 500 | published | Section 5: the outcome each gate must emit, and the bug that made one of them invisible. |

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
npm run build:14
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/14-permissions-sandboxes/diagrams/excalidraw/03-which-gate-fired.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:14` will fight over the same file, so fold anything worth
keeping back into `post14.js`.

## Notes on these

- **`03-which-gate-fired` has four rows because a naive trace has two.** A harness that tags
  spans blocked or ok collapses the middle two rows into the outer ones, and the sandbox row is
  the one that disappears -- which is exactly what happened in the Build #2 companion.
- **The fix is shown as code, at three lines.** The point of the section is that the fix is
  cheap and the omission is easy, and a paraphrase would lose both halves of that.
- **`01-sandbox-boundary` draws the host system dashed and empty of any arrow into it.** The
  crossed line is the only connection, and everything the box protects is listed on the far
  side of it, so the figure reads as a boundary rather than as a diagram of two systems.
