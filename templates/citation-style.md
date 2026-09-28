# Citation style

Every non-obvious claim in this series cites a source. Numbers, percentages,
benchmark results, vendor behaviour and "teams find that…" assertions **always**
carry one. The format is consistent so a reader can scan a Further reading section
and recognise the shape immediately.

This file exists because the series shipped, and was caught shipping, a **fabricated
quotation** — a phrase attributed to a named author who never wrote it. Everything
below is written to make that failure structurally harder to repeat.

---

## 1. In prose

Attribute mid-sentence with the parenthetical short form:

> Practitioners who instrument agents keep rediscovering the same handful
> (Faros AI, 2026).

When the title matters, name it inline in italics:

> Anthropic's *"Building Effective Agents"* (2024) draws the same distinction
> between a workflow and an agent.

For a source with a named author, use the surname:

> The founding equation is deliberately blunt (Trivedy, 2026).

---

## 2. Further reading bullets

End-of-post bullets say what the source *gives the reader*, not what it is about.
At least six per post.

```markdown
## Further reading

- Yao, S. *et al.* "ReAct: Synergizing Reasoning and Acting in Language Models"
  (2022): the reason → act → observe pattern this loop implements.
- Anthropic Engineering, "Building Effective Agents" (December 2024): workflow
  versus agent; the model-plus-loop framing.
- Trivedy, V. "The Anatomy of an Agent Harness" (LangChain, 10 March 2026): the
  origin of `Agent = Model + Harness`.

Full citations are in [REFERENCES.md](../../REFERENCES.md).
```

---

## 3. `REFERENCES.md`

The bibliography has one section per post plus a master list. A source cited in a
post's Further reading **must** appear in that post's REFERENCES section — the audit
does not check this, so it is on you.

Master-list shape:

```markdown
- **Surname, I.** "Title." *Publication*, D Month YYYY. https://url — what it
  supports in this series.
```

Per-post section shape:

```markdown
- Surname, "Title" — see Post NN (what it supports there).
```

---

## 4. The rules that stop a fabricated citation

1. **Quote marks are a promise.** If a phrase is inside quotation marks, the source
   must contain that phrase verbatim. If you are paraphrasing, drop the quote marks
   and reword until the sentence is honestly yours.
2. **Verify before you cite.** Fetch the page. Confirm it exists, confirm the author,
   confirm the date, and confirm it actually says what you are attributing to it. A
   search-result summary is not verification.
3. **Attribute the origin, not the amplifier.** Where a popular writer credits someone
   else for an idea, cite the originator and note the populariser:
   `(Trivedy, 2026; popularised by Osmani, 2026)`.
4. **Check the byline.** A piece hosted on a well-known person's site is not
   necessarily *by* them. "Humans and Agents in Software Engineering Loops" sits on
   martinfowler.com and is by **Kief Morris**.
5. **A secondary source is a fallback, not a default.** If a result is reported by an
   aggregator, find the primary write-up and cite it; give the aggregator as the
   summary.
6. **Numbers need a home.** A pricing constant, a benchmark score or a percentage with
   no citation is a defect, even when it is right.
7. **Do not inflate diversity.** The same author under two mastheads is one source.
   Say so.

---

## 5. Dates

Use the publication date the source itself carries, not the year you read it. Where a
post is revised, cite the original date and note the revision if it matters. Getting
this wrong is common and cheap to avoid: Huntley's "Ralph" technique is **2025**, not
2026.
