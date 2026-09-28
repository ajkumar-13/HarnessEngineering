# Hand-drawn companions to the post 07 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 settles which of the three
mechanisms to reach for, and it is also the only place the post's sharpest correction becomes
visible: MCP moves a tool's *code* out of your process, not its *schema* out of your window.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-progressive-disclosure` | 960 x 632 | published | A dormant catalogue on disk, with one skill loaded per turn and the window staying small. |
| `02-mcp-dispatch` | 960 x 600 | published | Section 5: one turn, six steps, from model to client to server and back. |
| `03-three-distances` | 960 x 470 | published | Section 6: general tool, skill, and MCP server, compared by what each keeps out of your window and out of your process. |

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
npm run build:07
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/07-skills-mcp-runtime/diagrams/excalidraw/03-three-distances.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:07` will fight over the same file, so fold anything worth
keeping back into `post07.js`.

## Notes on these

- **`03-three-distances` has two "keeps out of" rows on purpose.** They are the whole figure.
  Read down the window row and only the skill removes anything; read down the process row and
  only the MCP server does. Collapsing them into one row is exactly the mistake section 4
  spends a paragraph correcting.
- **The cards are ordered by distance, not by preference.** Nothing in the figure says the
  furthest one is best; the ordering is physical, and the choice is made by the middle rows.
- **`02-mcp-dispatch` numbers the steps on the drawing and explains them in a legend below.**
  Six labelled arrows inside the figure would have crowded the transport channel, which is the
  one place the reader needs to see a boundary being crossed.
