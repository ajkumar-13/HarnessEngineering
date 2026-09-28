"""Write a posts/NN-slug/diagrams/excalidraw/README.md from a small spec.

Twenty-six of these READMEs share the same six paragraphs of boilerplate and
differ in four places: the lede, the scene table, the file named in the
re-render example, and the notes at the end. Writing them by hand is how the
boilerplate drifts, so the boilerplate lives here and the spec carries only the
parts that are actually per-post.

    python tools/mk_scene_readme.py tools/scene-specs/03.json

The spec is JSON:

    {
      "num": "03",
      "slug": "03-the-agent-loop",
      "lede": "Two alternates and one published figure. ...",
      "scenes": [["01-agent-loop", "960 x 600", "published", "what it argues"], ...],
      "example": "03-batch-vs-streaming",
      "notes": ["- **`01-agent-loop`.** ...", ...]
    }
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TEMPLATE = """# Hand-drawn companions to the post {num} diagrams

{count_word} scenes, each in two forms:

| File | What it is |
|---|---|
| `NN-name.excalidraw` | An Excalidraw scene. Open it at [excalidraw.com](https://excalidraw.com) or in the VS Code Excalidraw extension and edit it directly. |
| `NN-name.svg` | The same scene rendered to a self-contained SVG with [roughjs](https://roughjs.com), themed with the repo's `--ce-*` tokens so it works in light and dark mode. |

{lede}

| Scene | Canvas | Status | What it argues |
|---|---|---|---|
{rows}

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
npm run build:{num}
```

Every element carries a seed derived from its index, so a rebuild is
byte-identical. Nothing here depends on a random number, which is what keeps a
regeneration from showing up as a diff.

## Editing one by hand

Open the `.excalidraw`, move things, save over it, then re-render:

```bash
cd assets/diagrams/excalidraw-generator
node render-scene.js ../../../posts/{slug}/diagrams/excalidraw/{example}.excalidraw
```

Use Excalidraw's own "Export to SVG" instead and you lose the thing that makes
these files work in dark mode: it bakes literal hex into every shape, where this
renderer emits `var(--ce-ink)` and friends. A hand edit and a later
`npm run build:{num}` will fight over the same file, so fold anything worth
keeping back into `post{num}.js`.

## Notes on these

{notes}
"""

COUNT = {1: 'One scene', 2: 'Two', 3: 'Three', 4: 'Four'}


def main(spec_path):
    spec = json.load(io.open(spec_path, encoding='utf-8'))
    rows = '\n'.join('| `%s` | %s | %s | %s |' % tuple(s) for s in spec['scenes'])
    out = TEMPLATE.format(
        num=spec['num'],
        slug=spec['slug'],
        count_word=COUNT[len(spec['scenes'])],
        lede=spec['lede'],
        rows=rows,
        example=spec['example'],
        notes='\n'.join(spec['notes']),
    )
    dest = os.path.join(ROOT, 'posts', spec['slug'], 'diagrams', 'excalidraw', 'README.md')
    io.open(dest, 'w', encoding='utf-8', newline='\n').write(out)
    print('wrote %s (%d bytes)' % (dest, len(out)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    main(sys.argv[1])
