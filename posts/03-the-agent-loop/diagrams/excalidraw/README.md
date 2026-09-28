# Hand-drawn companions to the post 03 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 is the only part of the post
that makes a claim about *time*, and it had nothing to show it with.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-agent-loop` | 960 x 600 | published | The cycle and its four exits, with the one exit that means success marked apart from the three backstops. |
| `02-stateless-model` | 960 x 580 | published | Section 3: the model as a stateless function beside the history the loop re-sends on every call. |
| `03-batch-vs-streaming` | 960 x 550 | published | Section 6: one turn on two schedules, and the bracket showing what streaming actually buys. |

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
npm run build:03
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/03-the-agent-loop/diagrams/excalidraw/03-batch-vs-streaming.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:03` will fight over the same file, so fold anything worth
keeping back into `post03.js`.

## Notes on these

- **`01-agent-loop`.** The final-answer exit is drawn in a different colour *and* leaves the
  cycle in a different direction, because colour alone should not carry the distinction. The
  three backstops live in a panel rather than on the cycle: they are not steps, they are checks.
- **`03-batch-vs-streaming`.** Both rows share one time axis and the model bar is the same
  length in each, which is the honest part: streaming does not make generation faster. The only
  thing that moves is where the harness lane starts, and the bracket measures exactly that.
- **The dashed marker is the whole figure.** It sits where the tool call becomes fully formed,
  mid-stream. Everything the post says about streaming follows from that one position, and it
  is also where the extra parsing complexity comes from.
