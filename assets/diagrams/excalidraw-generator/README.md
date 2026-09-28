# Excalidraw generator

Builds the hand-drawn companions to the series diagrams. One scene description
in JavaScript produces two files:

| Output | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

Both land in `posts/NN-slug/diagrams/excalidraw/`. What happens next depends on
whether the post already had a figure for that idea:

- **Alternate.** A hand-drawn version of a figure that already exists as clean
  vector one directory up. It stays where it is, for slides, talks, and anywhere
  a sketch reads better than a diagram.
- **Published.** A figure the post needed and did not have. Its `.svg` is
  promoted into `diagrams/` and the post embeds it like any other figure.

Each post's `diagrams/excalidraw/README.md` records which of its scenes is which.

## Setup

```bash
cd assets/diagrams/excalidraw-generator
npm install
```

`roughjs` does the sketching. `@resvg/resvg-js` is a dev dependency used only by
`preview.js`, which rasterises an SVG so you can eyeball it.

## The loop

```bash
npm run build:01          # postNN.js -> posts/01-.../diagrams/excalidraw/*.{excalidraw,svg}
node preview.js ../../../posts/01-from-context-to-harness/diagrams/excalidraw/00-hero-three-eras.svg /tmp/a.png
node preview.js ../../../posts/01-from-context-to-harness/diagrams/excalidraw/00-hero-three-eras.svg /tmp/b.png dark
```

Edit `postNN.js`, rebuild, look again. Every element carries a seed derived from
its index, so a rebuild is byte-identical: a regeneration that changed nothing
shows up as no diff at all.

### Editing by hand instead

Open the `.excalidraw` in Excalidraw, move things, save over the file, then:

```bash
node render-scene.js ../../../posts/01-from-context-to-harness/diagrams/excalidraw/00-hero-three-eras.excalidraw
```

That re-renders the SVG from the edited scene, inheriting canvas size, `<title>`
and `<desc>` from the SVG already sitting there. Do **not** use Excalidraw's own
"Export to SVG": it bakes literal hex into every shape, which loses dark mode.
`render-scene.js` warns if a shape carries a colour outside the `--ce-*` palette
for exactly that reason.

### Promoting a sketch to the published figure

```bash
node publish.js 02 02-prebuilt-vs-custom                    # named figures
node publish.js 02                                          # every figure in the post
```

This copies from `diagrams/excalidraw/` into `diagrams/` under the same filename, so
no Markdown image tag changes. **Name the figures.** A hand-drawn mirror of a figure
that already exists as clean vector is an alternate, and promoting it silently
replaces the published one; the bare form is for a post whose figures are all new.

The convention across the series: a figure the post had no clean vector for gets
promoted, and a mirror of one that already existed stays where it is. Each post's
`diagrams/excalidraw/README.md` records which of its scenes is which.

## Layout

| File | What it holds |
|---|---|
| `lib.js` | Element factories, the `--ce-*` palette, and the roughjs-to-SVG renderer. |
| `scaffold.js` | The shared left margin, the heading pair, and `emit()`. Every `postNN.js` uses it, which is what stops twenty-six generators from drifting apart one heading offset at a time. |
| `postNN.js` | One file per post. Each scene is a function returning `{ W, H, els, title, desc }`. |
| `render-scene.js` | Scene file back to SVG, for scenes edited by hand. |
| `preview.js` | Flattens the CSS variables and rasterises, for eyeballing. |
| `publish.js` | Promotes named figures into the directory the posts embed. |

## Adding a post

1. Write `postNN.js`. Import from `./lib` and `./scaffold`, build an array of
   elements per scene, return `{ W, H, els, title, desc }`, and call `emit(name, built)`.
2. Add a line to `package.json`:
   `"build:NN": "node postNN.js ../../../posts/NN-slug/diagrams/excalidraw"`.
3. `mkdir posts/NN-slug/diagrams/excalidraw` and copy a README into it.
4. Keep each scene's canvas size equal to the clean figure it accompanies, so the
   two remain interchangeable.

`title` and `desc` are not optional. Every diagram in this repository carries a
real `<desc>` — two or three sentences that let someone who cannot see the image
follow the argument it is making.

## What the renderer does that Excalidraw does not

Excalidraw bakes literal colors into a scene. The `.svg` output instead emits
`var(--ce-ink)` and friends, with the `:root` and `prefers-color-scheme` blocks
inlined, so one file serves both themes the way every other diagram in this
repository does.

Two details worth knowing if you extend it:

- **Fill and stroke are drawn in two passes.** A filled roughjs shape traces its
  fill boundary independently of its outline, so at equal roughness the colour
  visibly overshoots the ink. The fill pass runs at lower roughness, which keeps
  the wobble in the line where it belongs.
- **Dashes are emitted by hand.** roughjs passes `strokeLineDash` to its own SVG
  renderer as an attribute rather than baking it into the path operations, so
  serializing the operations directly loses it. `dashFor()` puts it back.

## Where it departs from the style guide

The series' figures use three stroke widths (1.5 / 1.0 / 0.75).
A sketch needs a wider vocabulary — a 4px spine, a 2px lasso — and roughjs varies
the apparent weight anyway. Everything else holds: `--ce-*` tokens only (shared with the Context Engineering sibling, per HARNESS-PLAN.md section 4), no raw
hex in the body, no emoji, `viewBox` with no `width`/`height` on the root,
`role="img"` with `<title>` and `<desc>`, and legibility in both themes.
