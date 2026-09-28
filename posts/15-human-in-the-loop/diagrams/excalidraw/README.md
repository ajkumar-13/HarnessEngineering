# Hand-drawn companions to the post 15 diagrams

Three scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Three **published figures**, all hand-drawn. The existing figures answer where the human
should be and how the pause works. Neither answers what an approval gate is actually made of,
which is what the post gained in its expansion.

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
| `01-autonomy-spectrum` | 960 x 564 | published | Four stops from suggest to autonomous, chosen per action rather than per agent. |
| `02-approval-gate` | 960 x 614 | published | Section 4: a flagged action pausing for a decision that arrives on the reviewer's schedule. |
| `03-anatomy-of-a-gate` | 960 x 500 | published | Sections 2, 5 and 7: the two halves, the four outcomes, and the record every decision leaves. |

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
npm run build:15
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/15-human-in-the-loop/diagrams/excalidraw/03-anatomy-of-a-gate.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:15` will fight over the same file, so fold anything worth
keeping back into `post15.js`.

## Notes on these

- **Four outcome cards, not two.** "Approved" and "denied" are the pair everyone builds; "not
  gated" is the common case and "no answer" is the one asynchronous approval introduces and
  synchronous approval never had. Drawing all four is what makes the timeout a design decision
  rather than an omission.
- **The two halves carry their signatures.** The section's argument is that the policy is
  ordinary testable code and the decider is a seam, and the two type signatures are the
  shortest way to show why substituting an auto-deny function tests the whole flow.
- **The record is drawn as five fields, not as prose.** Each is a thing a real gate has to
  store, and the last one -- how long it sat -- is the field that makes the rubber-stamp rate
  measurable, which is the only reason section 7 can propose watching it.
