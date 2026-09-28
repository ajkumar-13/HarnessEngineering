# Hand-drawn companions to the post 05 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 4 is what turns the taxonomy from a
vocabulary into a diagnostic, because it says what each mode looks like *in a trace* -- and a
bulleted list cannot show a shape.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-failure-modes-grid` | 960 x 596 | published | The six modes as symptom and fix, one card each, with the component that closes it. |
| `02-where-failures-strike` | 960 x 636 | published | Section 3: the same six placed at the loop stage where each strikes. |
| `03-trace-signatures` | 960 x 582 | published | Section 4: the shape each mode leaves behind in a run's trace. |

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
npm run build:05
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/05-agent-failure-modes/diagrams/excalidraw/03-trace-signatures.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:05` will fight over the same file, so fold anything worth
keeping back into `post05.js`.

## Notes on these

- **`03-trace-signatures` draws shapes, not screenshots.** A trace excerpt would be a picture
  of one vendor's log format; the shape -- a slope, a repetition, a spike, a recurrence -- is
  what actually transfers, and it is what a reader is pattern-matching against.
- **Four of the six signatures are sequences.** Victory declaration, context anxiety, doom
  loop, and silent drift are only visible across turns or across runs, which is the figure's
  quiet argument for a per-run trace over a per-call log.
- **`02-where-failures-strike` uses a dashed ring** for the across-turns mode rather than a
  fifth box, because silent drift does not have a stage: it is the one failure that spans them.
