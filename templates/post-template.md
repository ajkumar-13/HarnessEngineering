# Post template

Every post is a folder `posts/NN-slug/` containing:

```
posts/NN-slug/
├── frontmatter.yaml     # all metadata; never inline in index.md
├── index.md             # the post body, starting at the H1
└── diagrams/            # 3 SVGs, plus excalidraw/ sources
```

`python tools/audit.py NN` enforces most of what follows. Run it after every edit.

---

## 1. `frontmatter.yaml`

```yaml
slug: NN-short-kebab-slug
title: "NN · Short title — subtitle"
date: 2026-MM-DD
tags: [harness-engineering, <part-tag>, <2-3 topic tags>]
hero: diagrams/01-hero-slug.svg
reading_time: 13
part: "Part X — Group title"
```

- `slug` must equal the directory name.
- `title` must match the `index.md` H1 **exactly**, middle dot and em dash included.
- `part` must match the number's part: I 01–05, II 06–10, III 11–15, IV 16–20, V 21–26.
- `reading_time` is computed, never assigned:

  ```
  minutes = round(prose_words / 200 + code_lines / 25 + figures * 0.5)
  ```

  where `prose_words` excludes fenced code. The audit fails a post whose stated
  minutes drift from this.

---

## 2. `index.md` shape

```markdown
# NN · Title — subtitle

> **TL;DR.** Two to four sentences. State the thesis, not the topic. A reader who
> reads only this block should be able to repeat the post's central claim.
>
> **After reading this you will be able to:**
> - Verb-first capability.
> - Verb-first capability.
> - Verb-first capability.

![Alt text describing what the figure actually shows, not what it is called.](diagrams/01-hero.svg)
*One-line italic caption that says what the figure argues, not what it contains.*

---

## 1. First section

Prose.

---

## 2. Second section

...

---

## Common pitfalls

- **Bolded lead-in.** The explanation, and where in the post it is covered (§4).
- ... 4–7 bullets total.

---

## Further reading

- Author, "Title" (Year): what this source gives you that the others do not.
- ... at least 6 bullets.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post NN — Title](../NN-slug/index.md)**: why a reader goes there next.
- Include **both forward and back** links. Forward-only is a defect.
```

---

## 3. Density floors

These are derived from the sibling Context Engineering series' medians. They are
floors, not targets, and none of them is met by padding.

| Dimension | Floor | Notes |
| --- | --- | --- |
| Prose words | 2,800 | 2,900 for Part I; 3,100 for the builds (24–26) |
| Numbered sections | 8 | 10 for the builds |
| Fenced code blocks | 2 | ≥18 on-page code lines; ≥120 for a build |
| Tables | 1 | a decision matrix, comparison, or symptom-to-fix lookup |
| Parenthetical citations | 3 | every non-obvious claim carries one |
| Further reading bullets | 6 | |
| Figures | 3 | each with real alt text and an italic caption |
| Em dashes | **≤ 10** | target 4–5; see §4 |

---

## 4. Voice

- **British spelling**: behaviour, defence, recognise, artefact, minimise, catalogue,
  optimise, summarise, analyse.
- Second-person "you" is fine. **Never** "I" or "we" in body prose.
- Neutral textbook tone. No marketing voice, no hype, no rhetorical questions as
  section openers.
- Examples before formalism; concrete before abstract.
- **Framework-agnostic.** Plain Python and direct provider SDKs first. A framework
  appears only where it materially changes the shape of the code, never as the
  protagonist.
- Expand every acronym on first use *in that post*.
- **Em dashes are capped at 10 per post.** Count them mechanically, not by eye:

  ```bash
  python -c "import io;print(io.open('posts/NN-slug/index.md',encoding='utf-8').read().count(chr(8212)))"
  ```

  PowerShell miscounts BOM-less UTF-8; use Python.

---

## 5. Settled framing

Do not re-litigate these; posts across the series depend on them.

- The harness has **eleven components**; orchestration is the "scale tier" one level
  up, not renumbered.
- There are **six agent failure modes**: five performance, one safety, all
  harness-fixable, none fixed by a bigger model.
- MCP defers a tool's **implementation**, not its **schema**; keeping schemas out of
  the window is progressive disclosure.
- `Agent = Model + Harness` and "if you're not the model, you're the harness" are
  **Viv Trivedy's** (LangChain, 10 March 2026), popularised by Osmani (2026).
- The four stop conditions are numbered ① final answer, ② hard iteration cap,
  ③ token/wall-clock budget, ④ no-progress detection. Cite them by number.

---

## 6. Before you call a post done

```bash
python tools/audit.py NN                 # structure, frontmatter, links, diagrams
python -c "import io;print(io.open('posts/NN-slug/index.md',encoding='utf-8').read().count(chr(8212)))"
```

Then read the post start to finish as a reader. New sections belong where the
argument needs them, not bolted on at the end.
