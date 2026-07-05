# Contributing

Contributions are welcome. This guide covers style, diagram standards, and the PR process. It is intentionally identical in shape to the *Context Engineering* series' guide, so the two series read as one body of work.

---

## TL;DR

- One topic per PR; small is better than complete.
- Match the **voice** template at the top of every post.
- Match the **design tokens** for any new diagram — the same `--ce-*` tokens as the Context Engineering series.
- Cite every non-obvious claim; no hand-waved numbers.
- Run the linters and the word-count script before submitting.

---

## Voice

Every post uses the same shape. Keep it.

**Metadata** lives in a `posts/NN-slug/frontmatter.yaml` sidecar (`slug, title, date, tags, hero, reading_time, part`) — never inline in `index.md`, and never restated in the body. `index.md` starts directly at the `# H1`.

**Top of post:**

```markdown
> **TL;DR.** Two-to-four-sentence summary. The first sentence names the claim;
> the rest name what the post delivers.
>
> **After reading this you will be able to:**
> - Three concrete capabilities. Each starts with a verb.
```

Then a hero diagram (SVG embedded inline if small; image link if large) with a one-line italic caption underneath.

**Body:** numbered sections (`## 1. …`). Textbook voice. Second-person "you" is fine when it addresses the reader directly; avoid first-person "we"/"I" (outside an explicit code-along) and any marketing tone. Concrete numbers and citations beat assertions.

**Bottom of post:** `## Common pitfalls` (4–7 bullets), `## Further reading` (citations, then "Full citations in REFERENCES.md"), `## What to read next` (forward and sideways links). Cross-link to the Context Engineering series wherever a token-level detail is assumed rather than re-taught.

Reading time targets 10–14 minutes for principles posts, 12–14 for the build posts.

---

## Design tokens (locked — shared with Context Engineering)

Use these for **every** new diagram. Variants are fine; departures are not.

**Light palette**

| Token | Value | Use |
|---|---|---|
| `--ce-bg` | `#FAFAF7` | page background |
| `--ce-surface` | `#FFFFFF` | cards, boxes |
| `--ce-ink` | `#1A1A1A` | text, primary strokes |
| `--ce-primary` | `#5B7FBF` | primary fills, links |
| `--ce-accent` | `#D98E5F` | secondary fills |
| `--ce-success` | `#5C9E78` | "good" outcomes |
| `--ce-warn` | `#B8895A` | "caution" |
| `--ce-alert` | `#C66B5E` | "bad" outcomes |

**Dark palette** (`prefers-color-scheme: dark`): `#8BA8E0` / `#E8B088` / `#7FBF9B` / `#D4B58A` / `#D88880`.

**Typography.** Inter for labels; JetBrains Mono for code. **Strokes.** 1.5 primary; 1.0 secondary; 0.75 grids.

**SVG hygiene.** Self-contained: every SVG inlines its own `:root` variables and a `@media (prefers-color-scheme: dark)` block; no external CSS. `viewBox` set; no fixed `width`/`height`. Text uses `<text>` elements; never images of text.

---

## Citations

Every non-obvious claim cites a primary source: a paper, a vendor doc, a talk, or an empirical post. Inline: `(Osmani, 2026)`. Full bibliography in `REFERENCES.md`; each post's "Further reading" names its sources and points there. If a number appears in a post (a percentage, a benchmark score), the source must appear in that post's Further reading. **No invented numbers** — where a figure is reported by a secondary source, say "reported" and attribute it.

---

## Code

- Python 3.11+. Direct provider SDKs and reference agent SDKs first; a framework appears only when it materially changes the shape.
- One `pyproject.toml` per `code/<post>/`; a `README.md` with quickstart + what's stubbed; tests under `tests/` with pytest. The smaller companions keep an offline-runnable core (whole suite passes with no API key).

---

## PR process

1. Open an issue first for anything beyond a typo.
2. Branch from `main`; one topic per PR.
3. CI runs the linters and (when present) the eval harnesses for code directories.
4. The series author reviews.

---

## Code of conduct

Be kind. Disagree on ideas; never on people.
