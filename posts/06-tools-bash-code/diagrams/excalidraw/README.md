# Hand-drawn companions to the post 06 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 3 is the section a reader will
actually copy from, and it was four bullets of advice with nothing to copy.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-tool-dispatch` | 960 x 634 | published | Validate then execute, with the invalid path returning an error observation instead of a crash. |
| `02-universal-vs-zoo` | 960 x 472 | published | Section 2: fifty narrow tools beside four general ones, priced by what each costs on every call. |
| `03-schema-that-teaches` | 960 x 470 | published | Section 3: the same tool defined twice, with the four rules numbered onto the lines they change. |

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
npm run build:06
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/06-tools-bash-code/diagrams/excalidraw/03-schema-that-teaches.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:06` will fight over the same file, so fold anything worth
keeping back into `post06.js`.

## Notes on these

- **`03-schema-that-teaches` shows one tool, not two tools.** The comparison only works if the
  capability is identical on both sides; a different tool on the right would let the reader
  attribute the improvement to the choice of tool rather than to the schema.
- **The badges sit on the lines, not beside the panel.** Each of the four rules changed a
  specific line, and putting the number on that line is the difference between a figure and an
  illustration of a list.
- **`02-universal-vs-zoo` draws sixteen chips and says "about thirty-four more"** rather than
  drawing fifty. Fifty legible chips would need a canvas nobody reads; sixteen plus a count
  makes the same point and stays honest about what is drawn.
