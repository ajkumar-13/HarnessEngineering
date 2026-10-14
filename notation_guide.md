# Notation and vocabulary guide

One vocabulary, shared by every post in the series. The goal is that a term means the same thing in every post: a reader who learns in post 02 that the fourth component is "context management" never meets it as "compaction and resets" in post 18 and has to wonder whether that is something else. The [glossary](GLOSSARY.md) gives a one-paragraph definition of every term; this page fixes the names, the order, the numbers, and the typography.

Two rules govern everything below:

1. **One concept, one name, everywhere.** The same component is never "tools" in one post and "tools and code execution" in the next as if they were two things; the same failure is never "victory declaration" in one post and "premature completion" in another.
2. **Each term is reintroduced on first use in every post**, and every acronym is expanded on first use in every post, because readers arrive mid-series from a search engine.

## Contents

1. The equation and the nesting
2. The eleven components
3. The four exits of the loop
4. The six failure modes
5. The evidence grades
6. The ratchet
7. Claim labels
8. House conventions
9. Sibling series
10. Figure roles
11. Checklist before publishing a post

---

## 1. The equation and the nesting

The series is built on one equation, always written in code font: `Agent = Model + Harness`. The harness is everything that is not the model (Trivedy, 2026).

Four words name four nested things, from the inside out, and are never used interchangeably (post 01):

| Term | What it is |
|---|---|
| model | the trained weights behind a provider's API, treated as fixed; it keeps no state between calls |
| scaffold | the behaviour-defining layer around the model: system prompt, tool descriptions, how responses are parsed, what is remembered across steps |
| harness | the runtime that drives one agent: the loop and the components around it |
| orchestration | the layer one level up, which coordinates several agents as units |

Concentric rings are drawn for this nesting and for nothing else.

## 2. The eleven components

A harness has eleven components, numbered 01 to 11 and always named exactly as below (post 02 owns the list). The number is written with two digits when it is used ("component 04, context management"); the name is never replaced by a variant ("tools / code exec", "memory / continual learning", "permissions and sandbox"). Lower case in prose, sentence case at the start of a sentence, in a table cell, or on a figure.

| Number | Name | Group | Owning post |
|---|---|---|---|
| 01 | loop | the centre | post 03 |
| 02 | tools | feeds the loop | post 06 (skills and MCP, post 07) |
| 03 | state | feeds the loop | post 08 |
| 04 | context management | feeds the loop | post 09 |
| 05 | memory | feeds the loop | post 10 |
| 06 | verification | governs the loop | post 11 (roles, post 12) |
| 07 | hooks | governs the loop | post 13 |
| 08 | permissions | governs the loop | post 14 (approvals, post 15) |
| 09 | orchestration | a larger scale | post 16 (shared repositories, post 17) |
| 10 | long-horizon patterns | a larger scale | post 18 (loop engineering, post 19) |
| 11 | observability | governs the loop | post 21 |

The groups: **the loop** at the centre; **four that feed it** (tools, state, context management, memory), which decide what capability and information the model has on each turn; **four that govern it** (verification, hooks, permissions, observability), which decide what the model may do, whether its work is real, and what can be seen afterwards; and **two at a larger scale** (orchestration, long-horizon patterns), which are about many agents or one agent running longer than one window allows. Four of the eleven (loop, tools, context management, verification) are the conditions a system must meet to count as a harness at all (de Macedo, 2026; post 02).

## 3. The four exits of the loop

Every real loop carries four stop conditions, numbered the same way everywhere, written (1) to (4) in plain text, and checked in this order (post 03):

| Exit | Name | What fires it |
|---|---|---|
| (1) | final answer | the model finishes, signalled by a terminal stop reason from the provider, not by the mere absence of a tool call; the intended exit, which verification then confirms |
| (2) | iteration cap | a hard ceiling on turns, so that a loop that never reaches (1) still ends |
| (3) | budget | a ceiling in tokens or wall-clock seconds, because a turn can be cheap or enormous |
| (4) | no progress | the stall detector: successive turns stop changing anything |

Exit (1) is the intended exit; (2) to (4) are guard exits, and a run that takes one returns where it stopped as well as why (post 19). In code and traces the stop reasons are spelled `completed`, `max_iters`, `budget`, `no_progress`, with `error` for a run that raised (post 21).

## 4. The six failure modes

The six agent failure modes are **victory declaration, context anxiety, one-shotting, doom loop, silent drift, and destructive action**, named in that order (post 05). Each is tied to the component that fixes it:

| Failure mode | One clause | Component that fixes it |
|---|---|---|
| victory declaration | the agent announces the task complete when it is not | verification |
| context anxiety | output quality drops as the window fills and the agent races to finish | context management |
| one-shotting | the agent attempts the whole task in one sweep, one large change that is hard to review | verification (a planner, generator, evaluator split) |
| doom loop | the agent repeats the same ineffective action, busy but making no progress | the loop's no-progress exit |
| silent drift | the agent quietly ignores the project's conventions, run after run | memory and hooks (the ratchet) |
| destructive action | the agent runs something dangerous, such as `rm -rf` or a force-push | hooks and permissions |

Destructive action is the safety failure among the six: the only one that is not merely a wasted run. The singular "doom loop" is the name; "doom loops" is its plural in prose.

## 5. The evidence grades

A claim that the harness is a bigger lever than the model is graded by the strength of its evidence, in three words, never encoded as colour (post 04):

| Grade | What it means | The series' example |
|---|---|---|
| firm | the same model on the same benchmark, before and after a harness change | one coding agent on Terminal-Bench 2.0 with the model held fixed (Trivedy, 2026) |
| controlled | a comparison of scaffolds with the model and the tasks held fixed | a pre-registered study of three scaffolds across five models (Starace, 2026) |
| reported | a multiple quoted at one remove, whose model, benchmark or base cannot be checked | a same-model spread of "up to sixfold" in secondary write-ups (MindStudio, 2026) |

A reported multiple is never promoted to a measured one, and a post states what the evidence does not show.

## 6. The ratchet

The ratchet is the principle "every mistake becomes a rule" (Osmani, 2026; post 10): one failure becomes three durable constraints, a memory-file line (so the model reads it), a hook (so it is enforced), and a reviewer check (so it is caught). The series writes "the ratchet", or "the ratchet principle" when the principle rather than the mechanism is meant. In the capstone companion it is the `Ratchet` class (post 26).

## 7. Claim labels

Every cost, token count, test count, line count, and percentage in a post carries one of three labels, in the sentence that uses it:

| Label | What it means | How the sentence shows it |
|---|---|---|
| cited | taken from a dated source | the source and its date are named in the sentence; the full entry is in [REFERENCES.md](REFERENCES.md) |
| measured | produced by code the reader can run | the sentence names the snippet or the companion test that prints or asserts it, with its command |
| illustrative | an example chosen to make the arithmetic concrete | the word "illustrative" appears in the sentence, caption, or table heading |

Cost arithmetic names the model tier and the published rate it uses, with the date of the price page, and tells the reader to re-derive it against current rates. Line and test counts are those of the committed companion. Mathematics stays at cost arithmetic: token counts, rates and probabilities, inline as `$...$`.

## 8. House conventions

- **Post numbers** are two digits with a lower-case "post" in prose: "post 06", "posts 09 and 11".
- **Spelling** is British: *summarise*, *behaviour*, *centre*, *defence*, *artefact*, *labelled*, *organisation*. A quoted title and a code identifier keep their own spelling.
- **Acronyms** are expanded on first use in every post: large language model (LLM), Model Context Protocol (MCP), software development kit (SDK), human-in-the-loop (HITL), Harness-as-a-Service (HaaS), and so on.
- **Inline citations** are parenthetical author and year, (Trivedy, 2026), or organisation and year, (Anthropic, 2024); every one has a full entry in [REFERENCES.md](REFERENCES.md). Quotations are verbatim and attributed to the person who wrote them.
- **Voice** is third person and neutral: "the reader", "a team", "the agent", never "you" in body prose.
- **Punctuation:** no em or en dashes; a range is written "5 to 50 iterations"; a title's subtitle follows a colon.
- **Code identifiers, field names, and file names** are in code spans with their exact casing: `stop_reason`, `tool_use`, `AGENTS.md`, `CLAUDE.md`.

## 9. Sibling series

Another series is named by its key and its posts by id in code font, never by a path, a URL, or a phrase such as "CE Post 05":

| Series | Key | Ids | How this series cites it |
|---|---|---|---|
| Context Engineering | `context-engineering` | `ctx-001` to `ctx-030` | by id: prompt caching and the economics of one call (`ctx-005`), context rot and the context failure modes (`ctx-006`), write, select, compress and isolate (`ctx-007` to `ctx-013`) |
| Model Context Protocol | `mcp` | `mcp-001` to `mcp-024` | by id: the architecture (`mcp-002`), the host's tool loop and permissions (`mcp-011`), security the protocol does not stop (`mcp-019`) |
| AI Security | `ai-security` | `sec-NNN` | in prose only, until that series locks its ids |

## 10. Figure roles

Every figure in the series uses one colour per job a thing does in the harness, so that colour carries the job and the written name carries the identity:

- **Blue (model):** the model call and what the model produces: its reasoning, a proposed tool call, a draft, a final answer. The "reason" step of the loop.
- **Orange (act):** an action in the world: a tool call executed, a bash command, a file written, a request sent, a sub-agent dispatched. The "act" step and the tools component.
- **Green (state):** what persists beyond one turn: files on disk, git, a handoff or memory file, a task board, a trace store, a rule the ratchet wrote. The state component.
- **Purple (gate):** anything that checks or blocks: verification, a test run as a gate, a hook, a permission rule, an approval, a sandbox boundary, a loop exit condition. A gate is purple whether it passes or blocks.
- **Red (error):** a failure mode, a blocked or denied action, an overrun budget, a doom loop's repeated turn, a regression. Red never means a component.

The harness as a whole, the human, an orchestrator, a benchmark, a vendor product, and every neutral quantity are drawn in ink and neutral fills. There is no series accent colour, a chart with one series is ink, and no figure relies on colour alone: every shape carries its name ("verification", "hook: pre-tool").

## 11. Checklist before publishing a post

- [ ] `Agent = Model + Harness` in code font; model, scaffold, harness, orchestration used as Section 1 defines them.
- [ ] Every component named exactly as Section 2 names it; no slash variant.
- [ ] The four exits numbered and named as Section 3; the six failure modes spelled as Section 4.
- [ ] Every performance claim graded firm, controlled, or reported (Section 5); no reported multiple presented as measured.
- [ ] Every number cited, measured, or labelled illustrative (Section 7).
- [ ] Every acronym expanded on first use in this post; British spelling; no em or en dashes.
- [ ] Sibling series by key and id only (Section 9).
- [ ] Every relative link resolves, with forward slashes only.
