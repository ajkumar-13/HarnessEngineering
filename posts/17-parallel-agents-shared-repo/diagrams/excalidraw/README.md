# Hand-drawn companions to the post 17 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Section 6 is what stops the atomic claim
from being read as a stronger guarantee than it is, and its argument is a *sequence* -- the one
thing prose is worst at and a timeline is best at.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-shared-repo-swarm` | 960 x 560 | published | A file-based task board claimed by three agents, with no coordinator anywhere. |
| `02-worktree-isolation` | 960 x 536 | published | Section 3: one worktree and one branch per agent, and the three properties that matter for a swarm. |
| `03-at-least-once` | 960 x 490 | published | Section 6: the seven-step sequence in which one task runs twice, and the three ways to make that harmless. |

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
npm run build:17
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/17-parallel-agents-shared-repo/diagrams/excalidraw/03-at-least-once.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:17` will fight over the same file, so fold anything worth
keeping back into `post17.js`.

## Notes on these

- **Nothing in the timeline is a bug**, and the figure is drawn so that reads that way: every
  chip is an ordinary step, only two are marked, and the note under the axis says the board
  behaved exactly as designed. A figure that drew the double execution as an error would be
  making the opposite point.
- **The board gets its own lane.** The lease expiry is a *board* event, not something either
  agent did, and putting it in agent A's lane would suggest A released the task, which is
  precisely what did not happen.
- **The three mitigations are ordered, not listed.** Idempotence is first because it is
  cheapest and mostly a matter of how tasks are phrased; compare-and-set is last because it
  still wastes the loser's tokens.
