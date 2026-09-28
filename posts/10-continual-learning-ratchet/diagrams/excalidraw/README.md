# Hand-drawn companions to the post 10 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. Both existing figures draw the ratchet
*working*. Neither draws what the post spends its added length on: that a rule has to be earned
before it becomes permanent, and watched afterwards.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-ratchet-mechanism` | 960 x 640 | published | One failure fanning into three independent constraints: a memory line, a hook, and a reviewer check. |
| `02-ratchet-over-time` | 960 x 588 | published | Section 6: a staircase of reliability, one step per failure, that only climbs. |
| `03-life-of-a-rule` | 960 x 470 | published | Sections 3, 5 and 7: the five stages a rule passes through, from failure to a signal that it still works. |

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
npm run build:10
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/10-continual-learning-ratchet/diagrams/excalidraw/03-life-of-a-rule.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:10` will fight over the same file, so fold anything worth
keeping back into `post10.js`.

## Notes on these

- **`03-life-of-a-rule` puts the three teeth in the middle, not at the end.** Step 4 is the
  part everyone already implements; the argument of the post is that steps 2, 3 and 5 are what
  decide whether the mechanism accumulates knowledge or folklore.
- **The flow wraps rather than compressing into five narrow columns.** Five columns across 960
  would leave about 150px each, which is not enough for a rule you can actually read, and the
  rules in step 3 are the ones a reader is most likely to copy.
- **`02-ratchet-over-time` marks each riser with a dot and a rule.** The staircase alone would
  say "it goes up"; the dots say what each rise was bought with, which is the whole claim.
