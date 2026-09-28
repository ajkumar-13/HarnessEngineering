# Two animated figures

The series is about a loop, and a loop is a thing that happens over time. Seventy-eight static
figures can show the shape of one; they cannot show it turning. These two can.

| File | The moment it shows | Where the claim lives |
|---|---|---|
| `01-the-loop-turning.svg` | One revolution: reason, act, observe, and the stop check between every stage | [Post 03](../../posts/03-the-agent-loop/index.md), [Post 19](../../posts/19-loop-engineering/index.md) |
| `02-context-reset.svg` | A window filling to its limit, clearing on one frame, and the handoff file that survives it | [Post 09](../../posts/09-context-management-loop/index.md), [Post 18](../../posts/18-long-horizon-ralph/index.md) |

These are the two moments `HARNESS-PLAN.md` §4 asks for by name. They are drawn with the same
roughjs generator and the same `--ce-*` tokens as the post figures, so they sit beside them
rather than looking like they came from somewhere else.

## The three rules they follow

**Only opacity is animated.** No transforms, no `offset-path`, no SMIL. A roughjs shape is a
path with a hand-drawn wobble baked into its `d` attribute, so its geometry is not animatable
in any case, and opacity keyframes are the one technique that every renderer which already
draws these files supports.

**The still frame is the whole diagram.** Everything that carries meaning is drawn at full
opacity and never animated. What moves is a layer of highlights on top, and that layer starts
invisible. So a rasteriser that ignores CSS, a PDF export, and a reader who has asked for less
motion all get a complete figure rather than a half-drawn one — which is also why you can drop
either file into a slide deck as a still.

**The motion lives inside `prefers-reduced-motion: no-preference`.** The rule above is what
makes that safe: turning the motion off subtracts emphasis, never information.

Check the second rule the way you check everything else here — rasterise and look:

```bash
cd assets/diagrams/excalidraw-generator
node preview.js ../../animations/01-the-loop-turning.svg /tmp/a1.png
node preview.js ../../animations/02-context-reset.svg /tmp/a2.png dark
```

`preview.js` draws the still frame, because it does not run CSS animations. That is the point:
if the PNG is legible and complete, the reduced-motion rendering is too.

## Regenerating

```bash
cd assets/diagrams/excalidraw-generator
npm install
npm run build:animations
```

## No `.excalidraw` scene, unlike every other figure here

The other seventy-eight figures ship an editable scene beside the render. These two do not, and
the reason is not an oversight: the animation *is* a stylesheet, and an Excalidraw scene has
nowhere to put one. A round trip through the editor would return a still image that looks
correct and has quietly lost the thing the file exists for. `animations.js` is the only source.

## What the generator needed to gain

`renderSvg` grew two hooks for these, both additive and both unused by the post figures:

- an element may carry `animClass`, which wraps its output in `<g class="...">`
- the caller may pass `css`, which is appended to the `<style>` block

Both were checked against the whole series rather than reasoned about: all twenty-six
generators were run against the previous `lib.js` and the current one, and the 156 resulting
files — 78 SVGs and 78 scenes — are byte-for-byte identical. `JSON.stringify` drops an
`undefined` value, which is why an `animClass` nobody sets leaves the scenes untouched.

## Rendering caveat worth knowing

Both files are self-contained SVGs, so they animate in a browser, in an `<img>` tag, and in
anything that renders SVG with CSS. They do **not** animate in `resvg`, `librsvg`, most PDF
pipelines, or GitHub's own markdown sanitiser. In every one of those they fall back to the
still frame, which is the complete figure. Nothing breaks; the emphasis is simply absent.
