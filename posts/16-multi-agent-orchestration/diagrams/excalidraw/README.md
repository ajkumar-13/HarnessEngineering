# Hand-drawn companions to the post 16 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 5 exists because "coordination
cost" gets asserted a lot and quantified rarely, and it is the section that decides whether a
topology pays.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-topologies-gallery` | 960 x 632 | published | Four shapes for arranging agents, with the default drawn first. |
| `02-orchestration-decision` | 960 x 620 | published | Section 7: three gates, any one of which sends you back to a single agent. |
| `03-the-coordination-tax` | 960 x 470 | published | Section 5: tokens, latency and partial failure, each priced. |

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
npm run build:16
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/16-multi-agent-orchestration/diagrams/excalidraw/03-the-coordination-tax.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:16` will fight over the same file, so fold anything worth
keeping back into `post16.js`.

## Notes on these

- **The token bars use the same work segment on both rows.** That is the entire point: the
  work did not change, only the number of contexts carrying a system prompt and tool schemas
  before doing any of it. Scaling the work segment too would have hidden the argument.
- **The latency panel uses the post's own numbers**, four workers at ten seconds and one at
  ninety, rather than a tidier illustration. Uneven work is the case where fan-out
  disappoints, so the figure is drawn uneven.
- **The partial-failure panel leaves the three options unanswered**, because the post does
  not answer them either. The finding is that most systems never decided, and a figure that
  picked one would be asserting a default the prose declines to assert.
