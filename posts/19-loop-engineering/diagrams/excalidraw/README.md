# Hand-drawn companions to the post 19 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The existing figures answer how the loop
stops and how loops compose. Section 5 asks what neither of them does: what the loop leaves
behind when a guard catches it.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-layered-exits` | 960 x 570 | published | Four exits checked in order, all converging on a stop that always carries a reason. |
| `02-nested-loops` | 960 x 624 | published | Section 4: an inner verify-and-retry loop inside an outer one-task-per-pass loop. |
| `03-after-a-guard-exit` | 960 x 470 | published | Section 5: what a guard exit must leave behind, and the cost of each thing it skips. |

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
npm run build:19
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/19-loop-engineering/diagrams/excalidraw/03-after-a-guard-exit.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:19` will fight over the same file, so fold anything worth
keeping back into `post19.js`.

## Notes on these

- **Every duty carries its own "if you skip it" line.** Three pieces of advice are easy to
  nod at and skip; three consequences are harder to, and the consequences are what the section
  actually argues -- a guard that forfeits the spend it was protecting is a strange guard.
- **The two bands are drawn at equal weight.** The intended exit is not the important one
  here; the guards are, because they are the ones whose behaviour is undesigned. Making exit 1
  a small aside would have inverted the emphasis of the section.
- **`01-layered-exits` numbers the exits with plain digits.** The clean vector uses circled
  numerals, which sit outside the character range these hand-drawn figures commit to, so the
  sketch draws the numbers into badges instead.
