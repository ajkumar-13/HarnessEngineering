# Diagram style guide

Every diagram in this series uses the same visual language as the sibling Context
Engineering series, so the two read as one body of work. The tokens are shared and
imported unchanged: the `--ce-*` prefix is deliberate and is **not** renamed.

`python tools/audit.py` enforces the mechanical half of this contract.

---

## 1. The file contract

Every SVG must have all of:

- An XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
- A root `<svg>` with **`viewBox` only** — no `width`, no `height`
- `role="img" aria-labelledby="t d"`
- `<title id="t">` — one line, what the figure shows
- `<desc id="d">` — **over 200 characters.** A full prose reading of the figure for
  someone who cannot see it. Describe the content, not the shapes.
- An inline `:root{--ce-*}` token block **and** a
  `@media (prefers-color-scheme:dark)` block redefining them
- A `<rect class="bg">` covering the viewBox
- **No raw hex in any paint attribute.** Every `fill` and `stroke` references a token.
- **No emoji, and no ✓ / ✗ glyphs.** Nothing outside Latin-1 plus en/em dashes.

Copy the header and both token blocks verbatim from an existing figure, for example
`posts/11-verification-loops/diagrams/03-verifier-ladder.svg`.

---

## 2. Tokens

```css
:root{
  --ce-bg:#FAFAF7;         --ce-surface:#FFFFFF;
  --ce-ink:#1A1A1A;        --ce-ink-muted:#5C5C5C;   --ce-ink-subtle:#9A9A9A;
  --ce-border:#D9D9D4;
  --ce-primary:#5B7FBF;    --ce-accent:#D98E5F;
  --ce-success:#5C9E78;    --ce-warn:#B8895A;        --ce-alert:#C66B5E;
  --ce-neutral-1:#EAEAE4;  --ce-neutral-2:#CFCFC8;   --ce-neutral-3:#8E8E88;
  --ce-on-fill:#FFFDF9;    --ce-on-accent:#1A1A1A;
}
@media (prefers-color-scheme:dark){
  :root{
    --ce-bg:#0E0F12;       --ce-surface:#16181C;
    --ce-ink:#F2F2EE;      --ce-ink-muted:#B4B4AE;   --ce-ink-subtle:#6E6E68;
    --ce-border:#2A2D33;
    --ce-primary:#8BA8E0;  --ce-accent:#E8B088;
    --ce-success:#7FBF9B;  --ce-warn:#D4B58A;        --ce-alert:#D88880;
    --ce-neutral-1:#1F2229;--ce-neutral-2:#2C3038;   --ce-neutral-3:#6E6E68;
    --ce-on-fill:#14161A;  --ce-on-accent:#1A1A1A;
  }
}
```

**Semantics.** `--ce-success` for a good outcome, `--ce-warn` for caution,
`--ce-alert` for a bad one, `--ce-primary` for the main subject, `--ce-accent` for
the secondary. Never use `#FFFFFF` for knockout text; use `--ce-on-fill`.

---

## 3. Rules that are easy to break

- **Colour is never the only carrier of a distinction.** Anything told apart by
  colour must also differ in label, position, or line style. A colour-blind reader
  and a greyscale printout must both survive.
- **Stroke widths come from a set**: `1.5`, `1.3`, `1.0`, `0.75`. A thin accent
  spine is a 4px stroke, not a filled rectangle.
- **Draw a tint before the card it sits behind, never over it.**
- **Type**: `Excalifont` with the full fallback stack for hand-drawn scenes; sizes
  from roughly 8.5 (column headers) to 22 (title).
- **Canvas** is 960 wide. Height follows the content; check the last element's
  baseline sits inside the `viewBox` or the caption will clip.
- `fit()` is not a collision checker. Render a PNG with `preview.js` and look at it.

---

## 4. Per post

Three figures per post, in `posts/NN-slug/diagrams/`:

```
diagrams/
├── 01-name.svg          # the hero, referenced by frontmatter
├── 02-name.svg
├── 03-name.svg
└── excalidraw/
    ├── 01-name.excalidraw    # editable source
    ├── 01-name.svg           # rendered companion
    ├── ...
    └── README.md             # generated, see below
```

Scene filenames mirror the figures one directory up, so the two directories read
side by side. Generate the README from a spec rather than by hand:

```bash
python tools/mk_scene_readme.py tools/scene-specs/NN.json
```

---

## 5. Embedding a figure

```markdown
![Alt text describing what the figure shows, in a full sentence.](diagrams/02-name.svg)
*Italic caption saying what the figure argues, not what it contains.*
```

- **Alt text describes the content**, not the title. The audit rejects placeholder
  alt text, and a caption that merely repeats the heading is wasted.
- **A figure must be referred to by the prose around it.** Adding a figure means
  adding a sentence or two that reads it. A figure dropped in without commentary is
  decoration.
- Adding a figure changes `reading_time` (`figures * 0.5` is a term in the formula).
  Recompute it.

---

## 6. Toolchain

- **Excalidraw** for hand-feel conceptual scenes; the generator lives at
  `assets/diagrams/excalidraw-generator/`.
- **Hand-written SVG** for precise charts and canonical heroes.
- **Mermaid** for sequence and state diagrams where source-controllable text wins.

```bash
cd assets/diagrams/excalidraw-generator
npm install
npm run build:NN                   # scenes + svgs for post NN
node publish.js NN name-a          # promote named figures into diagrams/
node render-scene.js <scene>       # re-render after a hand edit
node preview.js <svg> <png> [dark] # rasterise so you can actually look at it
```

Always name the figures you mean to promote. A bare `node publish.js NN` overwrites
the clean vectors with the hand-drawn mirrors.
