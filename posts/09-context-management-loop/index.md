# 09 - Context management inside the loop: compaction, offloading, resets

> **TL;DR.** A running agent fills its own window: every turn appends the model's output and the tool results, so left alone the window grows until quality degrades, the context rot of `ctx-006`, now happening while the loop runs. The harness pushes back with a ladder of moves tried cheapest first: **offload** a big output to disk (lossless), **clear** tool results already acted on (nearly lossless), **compact** older turns into a summary (lossy), and **reset** the window behind a handoff file (total). Every rung but offloading at the tool boundary rewrites the cached prefix, so each is priced against the prompt cache before the word "cheap" is trusted.
>
> **Prerequisites:** [post 08](../08-state-filesystem-git/index.md), state and the filesystem.
> **Safe to skip?** Skip it if the reader can already offload, clear, compact and reset a long agent run, cut a message history without orphaning a tool result, and price a compaction against the prompt cache.
>
> **After reading, you will be able to:**
>
> - Tell context rot from a healthy long run by reading the window fill and the tool-result share of each call in a trace.
> - Run the ladder offload, clear, compact and reset in order of cost, say what each loses, and record its tokens and cache reuse.
> - Compact a message history under a written information-loss budget without orphaning a tool result.
> - Price a clear or a compaction against the prompt cache, and explain why one deep compaction beats several shallow ones.
> - Keep bytes out of the cached prefix, and choose the cheapest rung that works, including the case where clearing is wrong.

![A line chart of input tokens per model call over 140 calls of one generated run. The unmanaged run climbs in steps at each build log and passes the illustrative 200,000-token window at call 54. The managed run offloads the six build logs at the tool boundary, clears spent results at calls 97 and 123 after crossing the soft trigger, and compacts at call 138 on the hard trigger, falling to 8,447 tokens.](diagrams/01-window-timeline.svg)

*The window fills itself; the ladder pushes back, cheapest rung first, and the expensive rung fires once, late.*

---

## 1. The question: how does a running harness keep its window from rotting?

The sibling series established that a context window is not a bucket but a sequence the model attends to unevenly: information in the deep middle is used less well than information at the ends (lost-in-the-middle, `ctx-003`), and as a window fills with tools, retrieved chunks and history, accuracy falls (`ctx-006`). The name for that decay is *context rot*, and it is measured rather than asserted: Chroma's report (Hong, Troynikov and Huber, 14 July 2025) evaluated 18 large language models (LLMs) and found that performance degrades as input length grows, "often in surprising and non-uniform ways", even on simple tasks the same models handle when the input is short. That series studied the phenomenon in a *single* assembled prompt.

In a harness the rot is **dynamic**. The loop appends to the window every turn (the model's reasoning, each tool's output, every observation), so a window that started lean is bloated later whatever the harness does, and how fast depends on what the tools return rather than on how many turns have passed. This is the setting of *context anxiety*, the failure mode of [post 05](../05-agent-failure-modes/index.md) in which a model wraps up early as the window fills (named by Anthropic, Rajasekaran, 24 March 2026, who also reports Opus 4.5 largely removing it). The window fills itself; the harness's job is to push back, and it can only because [post 08](../08-state-filesystem-git/index.md) gave the loop somewhere to put things. Every move in this post takes something out of the window, and the disk is what makes that safe.

The figure at the top is one generated run of 140 calls, sent twice by `snippets/ladder.py` with illustrative sizes. Unmanaged, its 2,000-line build logs push the request past an illustrative 200,000-token window at call 54. Managed, the one lossy move fires once, at call 138. The rest of the post builds that policy rung by rung.

---

## 2. Reading the window: telling rot from a live run

A harness that cannot report its own window fill cannot trigger on it. Five signals, all ordinary trace attributes ([post 21](../21-observability-traces/index.md)), separate the cases.

| Signal | What to log | What it says |
|---|---|---|
| **Window fill** | input tokens divided by the model's limit, on every call | The number every trigger below depends on. Log it per call, not per run. |
| **Tool-result share** | tool-result tokens as a fraction of input tokens per call | High, and the offload or clear rungs will help; low, and history itself is the weight, the compact case. |
| **Re-read rate** | repeat reads of a path already read this run | The direct symptom of a lost decision: the agent no longer sees, or no longer trusts, what it already learned. |
| **Turn length against fill** | output tokens per assistant turn, plotted against fill | Turns getting shorter as fill climbs is one shape context anxiety can take in a trace ([post 05](../05-agent-failure-modes/index.md)). |
| **Edits applied** | cleared tool uses and tokens freed, as the provider reports them | Whether the policy fired at all, and what it bought. Anthropic's context-editing responses carry exactly this. |

The tool-result share is the one to instrument first, because it decides the branch. For the generated run, `uv run python posts/09-context-management-loop/snippets/transcript.py` reports tool results at 72% of the whole run sent as one request, 227,592 tokens of it build logs. A window that is mostly stale tool output has a cheap fix; one that is mostly genuine history does not. No measured cut-off separates the two; "high" is a judgement made per run.

---

## 3. Offload: move a big output out (lossless)

The cheapest and safest move handles a sudden spike: a single tool that returns a wall of text, a build log or a database dump, two thousand lines that crowd out what the model needs and ride along on every later call.

The fix is **tool-output offloading**. Addy Osmani's "Agent Harness Engineering" (19 April 2026) describes it: "The harness keeps the head and tail tokens above a threshold and offloads the full output to the filesystem, where the agent can read it on demand" (Osmani, 2026). The window gets a *pointer*, a short note plus a way to get the rest.

```python
def offload_if_big(output, scratch, name, *, limit=4000):
    """A large tool output goes to disk; the window gets a pointer instead."""
    if len(output) <= limit:
        return output
    root = Path(scratch).resolve()
    path = (root / SAFE.sub("_", name)).resolve()
    if root not in path.parents:          # a model-supplied name must not escape
        raise ValueError("offload path escapes the scratch directory")
    root.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8")
    lines = output.splitlines()
    return (f"[offloaded {len(lines)} lines to {path.name}; read it, or grep it "
            f"for the pattern you want]\nfirst 15 lines:\n"
            + "\n".join(lines[:15])
            + "\nlast 15 lines:\n" + "\n".join(lines[-15:]))
```

Running `uv run python posts/09-context-management-loop/snippets/offload.py` from the series root applies it to the build log of turn 9 of the generated run and prints:

```text
offload: a build log of 2,000 lines, 35,907 tokens, becomes a pointer of 486 tokens
  4,000 characters of this log are 1,446 tokens
  the model-supplied name '../../turn 9.log' is written inside the scratch directory as .._.._turn_9.log
  at the tool boundary, the next call sends 15,461 tokens, not 52,849, and shares 14,752 of 15,461 tokens (95%) with the call before
  swapped in ten turns later instead, that call shares 14,917 of 32,405 tokens (46%) with the call before
```

Three details are the whole technique. **The threshold is a break-even, not a taste**: an output is worth offloading once carrying it costs more than the pointer plus the one re-read it will probably provoke; here the 4,000-character limit is 1,446 tokens of log against a pointer of 486. **Return the head *and* the tail**, because a failing build's error is at the end; a head-only pointer is the wrong default for the case offloading most exists to serve. And **a pointer must be actionable**: path, size, and the shape of the query that gets the rest. A pointer that says only "output truncated" teaches the model that its tools are unreliable.

The path handling matters too. If `name` comes from a model-supplied identifier, an unguarded join lets `../` write outside the scratch directory, the blast-radius problem of [post 14](../14-permissions-sandboxes/index.md); the sanitiser makes it a plain file name, and the containment check catches what it misses.

This move is **lossless**: nothing is thrown away, only relocated, and it is the one to reach for first. The last two lines of the output show why *where* it runs matters (section 8): at the tool boundary the log never enters the prefix; swapped in later, the pointer breaks the cache at the log's position.

---

## 4. Clear: retire spent tool results (nearly lossless)

A tool result has a short useful life. The agent reads a file, reasons about it, edits, and moves on; the lines stay in the transcript, re-sent on every later call. The *decision* made from them matters; the raw bytes do not.

So once a tool result has been acted on, replace it with a stub: `[cleared: read_file, 52 lines; re-run the call if needed]`. The agent keeps its own reasoning about the file, the part that carried the meaning, and the file is one call away if it is needed again. `ctx-012` treats the same move from the token side; this section is the runtime half.

### The provider's version is the reference policy

Anthropic's context editing implements this rung on the server, behind the beta header `context-management-2025-06-27`, as the strategy `clear_tool_uses_20250919` ("Context editing", Claude Platform documentation, consulted October 2026). The mechanism matters more than the names, which drift: the edit is applied to the prompt before it reaches the model, oldest tool results first, each replaced by placeholder text, while the client keeps its full history. Its parameters *are* this section's policy.

| Parameter | Default | What it decides |
|---|---|---|
| `trigger` | 100,000 input tokens | When clearing fires: a count of input tokens or of tool uses, never a fraction of the window. |
| `keep` | 3 tool uses | The "never clear the most recent" rule, as a number: the agent may still be reasoning about them. |
| `clear_at_least` | none | A floor on tokens freed per activation; the strategy is not applied if it cannot meet it. |
| `exclude_tools` | none | Tools whose uses and results are never cleared: the safety rule below, as configuration. |
| `clear_tool_inputs` | `false` | By default the tool *call* stays visible and only its result is replaced, so the transcript still reads coherently. |

One row corrects the naive version. `clear_at_least` exists because clearing "Invalidates cached prompt prefixes when content is cleared", so the documentation's advice is to "clear enough tokens to make the cache invalidation worthwhile". Clearing is not free of cache damage; section 7 prices it. A request that turns the rung on carries one edit:

```json
{"context_management": {"edits": [{
  "type": "clear_tool_uses_20250919",
  "trigger": {"type": "input_tokens", "value": 60000},
  "keep": {"type": "tool_uses", "value": 5},
  "clear_at_least": {"type": "input_tokens", "value": 10000},
  "exclude_tools": ["create_ticket", "charge_card"]
}]}}
```

The response's `context_management.applied_edits` reports each edit with `cleared_tool_uses` and `cleared_input_tokens`, which is the "edits applied" signal of section 2.

Anthropic's announcement, "Managing context on the Claude Developer Platform" (29 September 2025), gives the numbers behind the rung: on an internal agentic-search evaluation, "Context editing alone delivered a 29% improvement" and combining it with the memory tool "improved performance by 39% over baseline"; in a 100-turn web-search evaluation it let runs finish that would otherwise have exhausted the window "while reducing token consumption by 84%". These are **reported**: a vendor's own evaluation, whose tasks and baseline cannot be checked.

### The rule that decides whether clearing is safe at all

`keep` and oldest-first govern *when* to clear, not *what* is safe to clear, and a stub that says "re-run the call if needed" is a lie for a result that cannot be cheaply re-obtained. Only clear results that are **deterministic and cheap to re-issue**: a file read, a grep, a directory listing, a test run. A non-deterministic query, a timestamped snapshot, a metered call, or anything with a side effect (a payment confirmation, a created ticket's identifier) must not be cleared, because the stub promises a recovery path that does not exist and the agent will act on that promise. Those get **summarised**, the one case in this post where the cheaper rung is the wrong answer (`ctx-012` states the same rule). `exclude_tools` is that rule as configuration. In the generated run, the live latency readings of `query_metrics` and the ticket of `create_ticket` are excluded, and they are exactly what the compaction's brief later has to carry.

---

## 5. Compact: summarise the older turns (lossy)

Offloading and clearing handle *observations*. Sometimes the window fills with **history itself**, dozens of ordinary turns, and the move is **compaction**: replace the older turns with a summary.

The keyword is **lossy**: a summary is smaller *because it discards detail*, and the detail might have mattered. So compaction is governed by an **information-loss budget**: decide, in advance, what must survive a summary and what may be dropped. This is the runtime edge of the *compress* strategy of `ctx-012`; the harness concerns are *when* it fires, *what* the summary is required to keep, and *where* it is safe to cut.

### The contract is the prompt

An information-loss budget with no text is not a contract. A **structured** brief beats free prose, because a structure the harness controls is one it can trust to keep the load-bearing facts.

```text
Summarise the run so far for the agent that will continue it.
Preserve, in this order:
1. The goal, verbatim, and every constraint the operator set.
2. Decisions taken, each with the reason given for it.
3. Files touched, by absolute path, and the current branch or diff.
4. Which checks were last seen passing, and which are failing.
5. Open questions, and the next concrete action.
Drop: verbatim tool output, superseded attempts, recap, politeness.
Bullet points, under {target_tokens} tokens.
```

Fields three and four make this a *run* brief rather than a *conversation* brief. Without them, an agent resumed from the brief does not know which files it has edited or whether the suite was green, and rediscovers both at the cost of several turns.

### Cutting the history without breaking the request

The obvious implementation slices the message list by count, `messages[-keep_last:]`, and it cuts wherever the arithmetic lands. In an agentic transcript every user turn after the first carries the result of the call just before it, so half the possible cuts fall between an assistant turn's `tool_use` block and the user turn holding its `tool_result`, and the request then opens on a result whose call is gone. The Anthropic Messages application programming interface (API) rejects such a request with a 400 error that does not point at the compactor.

The fix is a policy and a loop: walk the cut back until no tool call is left open and the kept tail starts with an assistant turn, then put the brief in front of it as a user turn of its own, which keeps the roles alternating.

```python
def open_tool_uses(msgs):
    """Ids of tool_use blocks in msgs whose tool_result is not also in msgs."""
    used, answered = set(), set()
    for m in msgs:
        for b in m["content"] if isinstance(m["content"], list) else []:
            if b.get("type") == "tool_use":
                used.add(b["id"])
            elif b.get("type") == "tool_result":
                answered.add(b["tool_use_id"])
    return used - answered


def compact(messages, summarise, *, keep_last=6):
    """Fold the head into one brief, cutting only where no tool call is left open."""
    cut = max(1, len(messages) - keep_last)
    while cut > 1 and (open_tool_uses(messages[:cut])
                       or messages[cut]["role"] != "assistant"):
        cut -= 1
    head, tail = messages[:cut], messages[cut:]
    if len(head) < 2:
        return messages                       # nothing worth folding yet
    brief = {"role": "user", "content": [
        {"type": "text", "text": "[brief of earlier turns]\n" + summarise(head)}]}
    return [brief] + tail                     # user, then the assistant turn the tail starts with
```

The summariser is an injected callable, so the prompt above is what changes when the loss budget does, and the system prompt is pinned outside the message list, so a compactor can never fold an instruction into the summary it is meant to obey. In `snippets/compact.py` the callable is a deterministic stand-in that keeps the contract's named fields (a model would write the brief); run over the first 40 turns of the generated run, `uv run python posts/09-context-management-loop/snippets/compact.py` begins:

```text
naive cut, messages[-5:]: starts with a user turn; orphaned tool_result: ['tu_38']
compact(keep_last=5): 81 -> 7 messages; the kept tail starts with an assistant turn; open tool calls: []
compact(keep_last=6): 81 -> 7 messages; the kept tail starts with an assistant turn; open tool calls: []
request: 139,570 -> 4,869 tokens; the brief: 467 tokens
first call after it: 773 of 4,869 tokens are a byte-identical prefix (16%, tools and system prompt); the call after that: 4,869 of 8,169 (60%)
```

The figure below draws the first two lines: the naive cut lands on turn 38's result, and the safe cut moves back one message to the call that asked for it.

![Turns 37 to 40 of the generated run as a row of message cards, each assistant turn a blue tool call and each user turn its green result. A red line shows the cut by count, the last five messages, starting on the result tu_38 whose call is cut away; a purple line one message earlier is the safe cut. Below, the compacted request of 7 messages: one user brief, then turn 38's call and result onward.](diagrams/02-safe-cut.svg)

*A cut by count orphans a result half the time; walking back to an assistant turn never does.*

A server-side compactor takes the cut out of the caller's hands, and Anthropic documents two kinds ("Compaction", Claude Platform documentation, consulted October 2026). *At a token threshold* (strategy `compact_20260112`, beta header `compact-2026-01-12`), the API summarises older context once input tokens reach a trigger that defaults to 150,000, returns a `compaction` block, and ignores everything before it once the caller appends the response. *On demand* (`compact-2026-09-04`), the caller requests the summary and puts the returned block first in `messages`; the documentation recommends this kind wherever it is available. The boundary bug above is a reason to use the provider's compactor where there is one.

### When to fire it

`ctx-012` sets two triggers as its policy, a starting point rather than a measured law: a **soft trigger at 80%** of the budget, where the cheap moves run, and a **hard trigger at 95%**, where older turns are summarised; both move down when tool outputs are large and variable. The gap keeps the lossy move from being the first thing that happens when a window gets busy: in the generated run the soft trigger clears at calls 97 and 123, and the hard trigger compacts once, at call 138.

The hard trigger cannot sit as high as it reads: at 95% of a 200,000-token window only 10,000 tokens remain for the summarisation instruction and the brief, so the trigger has to leave headroom for the summary call, which is why `ctx-012` measures both against the window less an output reserve. Anthropic's server-side rungs use **absolute** triggers (100,000 input tokens for context editing, 150,000 for threshold compaction), easier to reason about when one policy runs against several windows. And trigger on *fill*, not turn count: twenty terse turns and five turns carrying build logs are not the same window.

---

## 6. Reset: wipe the window behind a handoff (total)

When the task has outgrown a single context, or rot has set in and a summary cannot rescue it, the most aggressive move is a **full reset**: write a handoff file, discard the window, and resume in a fresh one. That such a rung is needed is a reported finding. Anthropic's "Effective harnesses for long-running agents" (Young, 26 November 2025) says of an agent with compaction available, "However, compaction isn't sufficient", and its harness carried each fresh context across on files and git (Anthropic, 2025). Its successor, "Harness design for long-running application development" (Rajasekaran, 24 March 2026), defines the move, "clearing the context window entirely and starting a fresh agent, combined with a structured handoff that carries the previous agent's state and the next steps", and contrasts it with compaction, which "doesn't give the agent a clean slate". The same article dropped resets once Opus 4.5 largely stopped showing context anxiety: a harness fits the model it runs (Anthropic, 2026).

This is the handoff file of [post 08](../08-state-filesystem-git/index.md) doing context-management duty, and the loss is **total**: everything not written to the handoff is gone. That is why it is the last resort, and why "the handoff must be complete" needs a definition.

**The handoff contract.** Post 08's four sections (spec, done, next, state) plus two, six fields in all; a run that cannot fill one is not ready to reset:

- a pointer to the spec or issue the work serves, not a paraphrase of it;
- what is done, in terms a fresh session can verify (commits, passing checks);
- what is next, as one concrete action rather than a theme;
- the state: the branch, the last checkpoint, and the paths that matter, including the scratch files earlier rungs wrote;
- decisions taken and the reason for each, so they are not relitigated;
- open questions, including anything the run was blocked on.

**The completeness test.** Seed a fresh window with only the handoff and check that it can name the next concrete action without asking a question.

**The failure signature.** An incomplete handoff shows up in a trace as repeated work at the start of every fresh window: the resumed session re-derives a decision the previous one had settled. If each reset costs three turns of rediscovery, the handoff is short a field.

Done over and over against a written spec, the reset *is* the **Ralph loop** of [post 18](../18-long-horizon-ralph/index.md). It is the hardest move to picture, because its point is what is *not* carried over; [an animated version](diagrams/05-context-reset.svg) fills a window, clears it on one frame, and leaves the handoff file standing.

---

## 7. What each move costs the prompt cache

Every rung so far has been priced in tokens saved; the line item most harnesses fail to budget for is the **prompt cache**. Prompt caching works on an exact **prefix** match: an entry is a hash of everything up to a breakpoint, so a change to any block at or before the breakpoint misses it, and the render order is tools, then system, then messages, each level invalidating the levels after it ("Prompt caching", Claude Platform documentation, consulted October 2026). Two consequences are more precise than "compaction is a cache miss".

**A rewrite of the message list is not a *full* miss.** Tools and system render before messages, so a breakpoint at the end of the system prompt survives a compaction. The threshold-compaction page says so: with that breakpoint, "The system prompt cache remains valid and is read from cache" and "Only the compaction summary needs to be written as a new cache entry". What is lost is the message history's cache, from the rewrite onward; the compaction in section 5 kept 773 tokens, the tools and the system prompt.

**The bill is the summary and a write on the new prefix, not full price on the old window**, which is never sent again. The multipliers are per model; for Claude Sonnet 4.6, the rate post 03 uses, Anthropic's pricing page (consulted October 2026) gives input at 3 dollars per million tokens, output at 15 (5×), a five-minute cache write at 3.75 (1.25×; 2× for the one-hour cache) and a cache read at 0.30 (0.1×).

### The arithmetic

Take a session at 160,000 tokens and two candidate compactions, with a brief of 5,000 tokens (illustrative sizes). Costs are in *token-equivalents*, tokens times their price relative to base input, so a 0.1× read of 160,000 tokens costs 16,000. Without a compaction every later call reads the 160,000 from cache; with one, the summary call reads that same cached prefix warm and writes the brief, the first call after it writes the new prefix in place of that read, and every call after that reads the shorter prefix. `uv run python posts/09-context-management-loop/snippets/cache_cost.py` prints:

```text
multipliers: output 5x, cache write 1.25x, cache read 0.1x of base input
line item                                                 deep   shallow
session after the compaction (tokens)                   25,000   130,000
summary call: cached prefix read warm at 0.1x           16,000    16,000
summary call: 5,000 output tokens at 5x                 25,000    25,000
first call after: write at 1.25x less read at 0.1x      15,250   146,500
the compaction event                                    56,250   187,500
saved on every later call                               13,500     3,000
calls to break even                                        4.2      62.5
deep, summary call sent cold at 1x: event 180,250, break even after 13.4 calls
deep event in dollars: $0.17; saved per later call: $0.0405
ten shallow compactions to the same 25,000: 1,321,875, 23.5 times one deep one
```

That table is the argument for **compact rarely and deeply**. The write premium is charged on the entire surviving prefix, not on the part removed, so the shallow compaction pays nearly the full write to buy a tenth of the deep one's saving, and needs 62.5 later calls to earn it back against 4.2. Ten small compactions to the same size are not ten times as expensive as one large one; the last line says their events alone cost 23.5 times as much, because each pays a write on a prefix that is still nearly full.

The summary call is read *warm*: issued against the still-cached prefix with a trailing "summarise the above" instruction, rather than pasting the head into a fresh request, the head is read at 0.1× instead of 1×. Sent cold, the deep compaction costs 180,250 and breaks even after 13.4 calls instead of 4.2. The figure below plots the net cost of both compactions, call by call.

![A line chart of the net cost of a compaction, in token-equivalents, against the number of later calls, for two dashed illustrative lines. The deep compaction starts at 56,250 and crosses zero after 4.2 calls; the shallow one starts at 187,500 and crosses zero after 62.5 calls.](diagrams/03-break-even.svg)

*The shallow compaction pays nearly the deep one's bill and earns a fraction of its saving.*

Clearing pays a version of the same bill, because oldest-first lands the rewrite near the front: the clear that `snippets/offload.py` runs after turn 40 rewrote the run's first tool result, and the next call shares a prefix of only 4,465 of 51,775 tokens with the last, against 99% without it. The snippets report that byte-identical prefix, the most a cache can return: the API writes entries only at breakpoints and looks back at most 20 blocks for one. It is still the better rung (no model call, nothing paraphrased), but a few cleared results per turn buy a fraction of the headroom for the same invalidation. Batch the clears. The run-level economics of the stable prefix are [post 23](../23-economics-haas/index.md)'s.

---

## 8. Prevention: keeping bytes out of the prefix

**Progressive disclosure** ([post 07](../07-skills-mcp-runtime/index.md), with the Model Context Protocol, MCP) belongs alongside these: loading a skill's tools only when a turn needs them is context management applied to *tool schemas*.

The useful axis is not which move runs but *when* it acts. **Preventative** moves act before bytes enter the prefix: progressive disclosure keeps schemas out, and offloading at the tool boundary keeps large outputs out. **Corrective** moves act on bytes already there: clearing, compaction and reset all rewrite a prefix that has been built and cached. Offloading sits on both sides of that line. Run inside the tool wrapper it is preventative and costs nothing in cache terms (95% of the next call read from cache, in section 3's output); run after the output has been appended it is a clear, with a clear's bill (46%).

That is a second reason to build the preventative moves first: they are the only moves that leave the cached prefix untouched, and they make the corrective rungs run less often. Progressive disclosure earns that on one condition: a newly loaded schema must be *appended* to the conversation rather than swapped into the tool block, which renders first, so a swap invalidates the whole prefix and costs more than the schemas it keeps out ([post 07](../07-skills-mcp-runtime/index.md)). Anthropic's caching documentation now describes a beta for exactly that, `inline-tools-2026-09-15`, which sends a new tool's definition in a mid-conversation system message and leaves `tools` as first sent.

---

## 9. Choosing between them

The four moves form an escalation ladder, and the rule is to take the cheapest rung that solves the problem.

- **A single big output spiked the window?** Offload it, at the tool boundary. Lossless, cheap, no cache cost.
- **Old tool results nobody needs any more?** Clear them to stubs, in batches. No model call, nothing paraphrased.
- **Many ordinary turns are the weight?** Compact the old head deeply, keep recent turns verbatim.
- **The window is unrecoverable, or the task spans more than one window?** Reset behind a complete handoff.
- **The result cannot be re-obtained?** Break the ladder and summarise it, even though clearing looks cheaper.

![Four cards stepping up, cheapest first. Offload, lossless, loses nothing and leaves the cache untouched at the tool boundary; clear, nearly lossless, loses the raw bytes and breaks the cache from the first cleared result; compact, lossy, loses what the brief drops and rewrites the cache after the system prompt; reset, total, loses all the handoff lacks and starts the cache over.](diagrams/04-ladder.svg)

*Only offloading at the tool boundary leaves the cached prefix whole; every other rung rewrites it, so each rewrite should be large.*

With the cache column of the figure attached, offloading is cheap in three senses (no model call, nothing paraphrased, no cache damage), clearing in two, and compaction and reset in none. "Take the cheapest rung that works" survives, with a rule underneath it: a rung that rewrites the prefix should rewrite enough to be worth the invalidation. Above the ladder sit two meta-rules: **prefer prevention**, and **measure before trusting**: compaction and resets are lossy, and the only way to know a loss budget is right is to evaluate the agent with and without them ([post 22](../22-evaluating-harnesses/index.md)). A summary that silently drops a load-bearing fact is a bug found only by looking for it.

---

## 10. Make it run

Every snippet runs offline from the series root over the same generated transcript, with `tiktoken` (in the root environment) counting tokens; its `cl100k_base` encoding is an OpenAI tokenizer standing in for the provider's, so the counts are illustrative too:

```bash
uv run python posts/09-context-management-loop/snippets/transcript.py
uv run python posts/09-context-management-loop/snippets/offload.py
uv run python posts/09-context-management-loop/snippets/compact.py
uv run python posts/09-context-management-loop/snippets/cache_cost.py
uv run python posts/09-context-management-loop/snippets/ladder.py
```

The first four print what sections 2, 3, 5 and 7 quote or cite. The last is the whole ladder on one run, the figure at the top of the post: the policy of section 5 before every call, offload at the tool boundary, a clear at the soft trigger when it frees at least 10,000 tokens, a compaction at the hard trigger. It prints tokens before and after each rung and how much of the rewritten request that call reads from cache:

```text
window 200,000 (illustrative); soft trigger 160,000; hard trigger 190,000; calls 2 to 141
unmanaged: call 54 would send 201,343 tokens, past the window
managed: build logs offloaded at the tool boundary before calls 10, 31, 52, 73, 94, 115
call  rung       before    after  shared with the call before
  97  clear     160,617  126,229  4,465 of 126,229 (4%)
 123  clear     172,367  161,705  122,790 of 161,705 (76%)
 138  compact   190,428    8,447  773 of 8,447 (9%)
managed peak: 186,870 tokens; last call: 12,147
```

The second clear is the batching rule at work: no clear freed 10,000 tokens until call 123, and that one rewrote from a later position, so 76% of the call was still a byte-identical prefix of the one before. To run the policy over a captured transcript, replace `transcript()` with a loader that returns the same message list.

---

## 11. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A compactor that cuts by count.** The first long run fails with a 400 error about a `tool_result` with no matching `tool_use`, on a request the harness assembled itself.
- **Clearing a result that cannot be re-obtained.** The agent, told to "re-run the call if needed", queries a live metric again, gets a different number, and reasons from both as if they were one reading.
- **Clearing a few results every turn.** Window fill stays flat, but cache reads in the usage figures fall to a few per cent of input on every call and the bill rises.
- **A brief without the run fields.** After a compaction the agent re-reads files it has edited and re-runs a suite that was green, spending its first turns rediscovering what the brief dropped.
- **A trigger with no headroom.** The summary call itself overflows the window, and the run fails at the moment it was trying to save itself.

---

## Common pitfalls

1. **Dumping big tool output into the transcript.** The most common cause of a bloated window, and the cheapest to fix: offload it at the tool boundary and return an actionable pointer with head and tail (section 3).
2. **Summarising what could just be cleared.** A spent, re-issuable result can be stubbed for nothing; paraphrasing it costs a model call and risks altering it (sections 4 and 5).
3. **Compacting with no loss budget.** A brief that drops the goal, a decision or which checks were green is worse than no brief; write the summarisation prompt as a contract (section 5).
4. **Compacting little and often, or on turn count.** Trigger on fill, and make each compaction deep: a shallow one pays nearly the full cache write for almost no saving (sections 5 and 7).
5. **Resetting behind an incomplete handoff.** Reset is total loss, so test the handoff by seeding a fresh window with it alone (section 6).

---

## Further reading

- Hong, Troynikov and Huber, "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (Chroma, 14 July 2025): the 18-model evaluation behind the term.
- Anthropic, "Context editing" (Claude Platform documentation): the clearing strategy, its parameters, and its note on cache invalidation.
- Anthropic, "Managing context on the Claude Developer Platform" (29 September 2025): the reported evaluation numbers for context editing and the memory tool.
- Anthropic, "Compaction" (Claude Platform documentation): compaction at a threshold and on demand.
- Anthropic Engineering, Justin Young, "Effective harnesses for long-running agents" (26 November 2025), and Prithvi Rajasekaran, "Harness design for long-running application development" (24 March 2026): compaction not being sufficient, and the reset with a structured handoff.
- Anthropic, "Prompt caching" and "Pricing" (Claude Platform documentation): prefix matching and the multipliers.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026): compaction, tool-call offloading with head and tail, and full resets as runtime moves.
- ai-boost, "awesome-harness-engineering" (GitHub, 2026): the Context Delivery and Compaction section.
- `ctx-003` (how models read a window), `ctx-006` (the context failure modes and context rot) and `ctx-012` (compress strategies, tool-result clearing, and the 80 and 95% triggers).

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 10 - Continual learning and the ratchet: every mistake becomes a rule](../10-continual-learning-ratchet/index.md):** state that persists *across* tasks, the memory file and failures turned into durable rules.
- **[Post 18 - Long-horizon and multi-context execution: Ralph loops and context bridging](../18-long-horizon-ralph/index.md):** the reset move as an architecture, Ralph loops over a written spec.
