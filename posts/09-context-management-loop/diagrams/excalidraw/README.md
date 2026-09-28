# Hand-drawn companions to the post 09 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The post's ladder grew a rung -- clearing a
spent tool result to a stub -- and no figure showed it, nor the column the prose argues
hardest for: what each move does to the prompt cache.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-window-timeline` | 960 x 636 | published | Window fill across seven turns, managed against unmanaged, with the rot zone marked. |
| `02-three-moves` | 960 x 580 | published | Section 7: offload, compact and reset compared by what each does, when, and what it costs. |
| `03-escalation-ladder` | 960 x 626 | published | All four rungs, with what is lost and what happens to the prompt cache. |

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
npm run build:09
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/09-context-management-loop/diagrams/excalidraw/03-escalation-ladder.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:09` will fight over the same file, so fold anything worth
keeping back into `post09.js`.

## Notes on these

- **`03-escalation-ladder` exists because the prose outgrew `02-three-moves`.** The post now
  describes four corrective moves; the older figure describes three. Rather than redraw a
  published figure and lose its depth, the new one carries the full ladder and the older one
  keeps the per-move detail. `02-three-moves` gained a closing line pointing at the fourth rung.
- **The cache column is the reason this figure was worth drawing.** It turns "take the cheapest
  rung" from a preference into an argument: the two cheap rungs are cheap in three separate
  senses at once, and there is no case where the aggressive move is quietly the bargain.
- **`01-window-timeline` draws the unmanaged run in the same colour as the rot zone**, so the
  line visibly enters the band it is named after rather than merely rising near it.
