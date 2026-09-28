# 09 · Context management inside the loop — compaction, offloading, resets

> **TL;DR.** A running agent fills its own window: every turn appends the model's output and the tool results, so left alone the window swells until quality degrades (*context rot*, now happening dynamically as the loop runs). A harness that means to run for more than a few turns must **actively manage its own context**. The corrective moves form a ladder of increasing aggressiveness: **offload** a big output to disk (lossless), **clear** tool results that have been acted on (nearly lossless), **compact** older turns into a summary (lossy), and **reset** the window entirely behind a handoff file (total). Reach for the cheapest rung that works, and price every rung against the prompt cache before trusting the word "cheap".
>
> **After reading this you will be able to:**
> - Recognise context rot from a live trace rather than in principle, and tell which rung the run needs.
> - Implement the three everyday moves: tool-output offloading, spent-result clearing, and rolling-summary compaction.
> - Choose between offload, clear, compact, and reset, including the one case where the cheaper rung is the wrong answer.
> - Trigger on window fill rather than turn count, and cost a compaction against the cache it invalidates.

![A bar chart of window fill on each of eight calls, as a percentage of the model limit, with a soft trigger at 80 % and a hard trigger at 95 % across a shaded rot zone: an offload and a clear after t4, a deep compaction after t7, a dashed unmanaged line that exhausts the window by t5, and five cards giving the signals to log on every call.](diagrams/01-window-timeline.svg)
*The window is a budget you spend down every turn. Unmanaged, it overflows into the rot zone; managed, it stays low and the model stays sharp.*

> The hardest of the three moves to picture is the reset, because the point of it is what is *not* carried over. [An animated version](../../assets/animations/02-context-reset.svg) fills a window, clears it on one frame, and leaves the handoff file standing.

---

## 1. Context rot happens while the loop runs

The Context Engineering series established that a context window is not a bucket but a sequence the model attends to non-uniformly: information in the deep middle is used less well than information at the ends (lost-in-the-middle), and as a window fills with tools, retrieved chunks, and history, accuracy falls (Context Engineering, Posts 03, 06). The name for that decay is *context rot*, and it is measured rather than asserted: Chroma evaluated eighteen large language models (LLMs) and found recall and reasoning sagging steadily as input length grew, on tasks the same model handled easily when they were short (Hong et al., 2025). Degradation starts well inside the advertised window. That series studied the phenomenon in a *single* assembled prompt.

In a harness, it is worse, because the rot is **dynamic**. The loop appends to the window every turn (the model's reasoning, each tool's output, every observation), so a window that started lean is bloated later whether you did anything or not, and how fast depends on what the tools return rather than on how many turns have passed. This is the dynamic behind *context anxiety*, the reported failure mode from [Post 05](../05-agent-failure-modes/index.md) where the model rushes as the window fills, and behind the slow quality slide of a long session. The window fills itself; the harness's job is to push back.

Pushing back is possible only because [Post 08](../08-state-filesystem-git/index.md) gave the loop somewhere to put things: the filesystem. Every move in this post is, at bottom, *moving state out of the window and onto disk.* The window is the model's desk; disk is the filing cabinet. Context management is keeping the desk clear.

---

## 2. Reading the window: telling rot from a live run

Every threshold in this post is a number somebody has to measure. A harness that cannot report its own window fill cannot trigger on it, and the decision list in §9 assumes a diagnosis the reader has already made. Five signals, all of them ordinary trace attributes ([Post 21](../21-observability-traces/index.md)), separate the cases.

| Signal | What to log | What it tells you |
|---|---|---|
| **Window fill** | input tokens divided by the model's limit, on every call | The number every trigger below depends on. Log it per call, not per run. |
| **Tool-result share** | tool-result tokens as a fraction of input tokens per call | Above roughly a half you are in the offload or clear case (§3, §4); below it, history itself is the weight and you are in the compact case (§5). |
| **Re-read rate** | repeat reads of a path already read this run | The direct symptom of a lost decision: the agent no longer trusts, or no longer sees, what it already learned. |
| **Turn length against fill** | output tokens per assistant turn, plotted against fill | Turns getting shorter as fill climbs is the shape context anxiety makes in a trace ([Post 05](../05-agent-failure-modes/index.md) §6). |
| **Edits applied** | cleared tool uses and tokens freed, as reported by the provider | Whether your policy fired at all, and what it bought. Anthropic's context-editing responses carry exactly this (Anthropic, 2025). |

The tool-result share is the one worth instrumenting first, because it decides the branch. A run whose window is 70 % stale tool output has a cheap fix; a run whose window is 70 % genuine history does not.

---

## 3. Offload: move a big output out (lossless)

The cheapest and safest move handles the most common cause of a sudden spike: a single tool that returns a wall of text. A build log, a large file, a database dump: two thousand lines that, dropped into the transcript, crowd out everything the model actually needs and ride along on every subsequent call.

The fix is **tool-output offloading**: if an output is large, write it to disk and return a *pointer*, a short note plus a way to get the rest (ai-boost, 2026). The full output is one read or grep away when the model wants it; until then it costs nothing.

```python
import re
from pathlib import Path

SAFE = re.compile(r"[^A-Za-z0-9._-]")

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

Three details in that function are the whole technique, and each is a place hand-rolled offloaders go wrong. **The threshold is a break-even, not a taste**: an output is worth offloading once carrying it costs more than the pointer plus the one re-read it will probably provoke, and a 4,000-character limit is roughly a thousand tokens against a replacement of a few hundred once its head and tail are counted. **Return the head *and* the tail**, because the example this section leads with is a build log and a failing build's error is at the end; a head-only pointer is the wrong default for the case it most exists to serve. And **a pointer must be actionable**: path, size, and the shape of the query that gets the rest (a grep pattern for a log, a line range for a file). A pointer that says only "output truncated" teaches the model that its tools are unreliable.

The path handling is not decoration either. If `name` derives from a tool call or a model-supplied identifier, an unguarded join lets `../` write outside the scratch directory, which is the blast-radius problem [Post 14](../14-permissions-sandboxes/index.md) treats in full.

This move is **lossless**: nothing is thrown away, only relocated. It is the one to reach for first, and for many agents it alone keeps the window healthy, because tool output, not reasoning, is usually what bloats a loop.

---

## 4. Clear: retire spent tool results (nearly lossless)

The second rung is the one most hand-rolled loops skip, and the one providers have started shipping on your behalf.

A tool result has a short useful life. The agent calls a file reader, reasons about the contents, makes an edit, and moves on. After that, those two hundred lines sit in the transcript forever, re-sent on every subsequent call, contributing nothing but cost and noise. The *decision* the agent made from them matters; the raw bytes do not.

So: once a tool result has been acted on, replace it with a stub. `[read src/parser.py, 240 lines, cleared; re-read if needed]`. The agent keeps its own reasoning about the file, which is the part that carried the meaning, and the file is one call away if it turns out to be needed again. Context Engineering Post 12 §4 treats the same move from the token side, with reduction ranges and the safety rule below; this section is the runtime half.

### The provider's version is the reference policy

Anthropic's context-editing feature implements this rung server-side, behind the beta header `context-management-2025-06-27`, as a strategy named `clear_tool_uses_20250919` (Anthropic, 2025). Its parameters are worth reading even if you never call that application programming interface (API), because the parameter set *is* the policy this section has been gesturing at, and its defaults make a defensible starting point.

| Parameter | Default | What it decides |
|---|---|---|
| `trigger` | 100,000 input tokens | When clearing fires. An absolute token count, not a fraction of the window. |
| `keep` | 3 most recent tool use/result pairs | The "never clear the most recent" rule, as a number. The agent may still be mid-way through reasoning about them. |
| `clear_at_least` | none | A floor on tokens freed per activation. The strategy declines to fire if it cannot meet it. |
| `exclude_tools` | none | Tools whose results are never cleared. This is the safety rule below, as configuration. |
| `clear_tool_inputs` | `false` | By default the tool *call* stays visible and only its result is replaced, so the transcript still reads coherently. |

One of those rows is a correction to the naive version. `clear_at_least` exists for a reason the documentation states outright: clearing "invalidates cached prompt prefixes when content is cleared", so you should "clear enough tokens to make the cache invalidation worthwhile" (Anthropic, 2025). Clearing is not free of cache damage; §7 prices it. Batch the clears, and the parameter enforces the batching for you.

```python
from anthropic import Anthropic

client = Anthropic()

response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=4096,
    betas=["context-management-2025-06-27"],
    context_management={"edits": [{
        "type": "clear_tool_uses_20250919",
        "trigger": {"type": "input_tokens", "value": 60000},
        "keep": {"type": "tool_uses", "value": 5},
        "clear_at_least": {"type": "input_tokens", "value": 10000},
        "exclude_tools": ["create_ticket", "charge_card"],
    }]},
    tools=TOOLS,
    messages=messages,
)
for edit in response.context_management.applied_edits:
    log(edit.type, edit.cleared_tool_uses, edit.cleared_input_tokens)
```

The measurement behind the rung is the strongest number in this post. On Anthropic's internal agentic-search evaluation, context editing alone improved task performance by 29 % over the baseline, and 39 % when combined with a memory tool; on a 100-turn web-search evaluation it cut token consumption by 84 % while letting runs finish that would otherwise have exhausted the window (Anthropic, 2025). That 84 % is also about as direct a measurement as exists of the claim this rung rests on: in a long agentic run, stale tool output is the bulk of the window, larger than reasoning or instructions.

### The rule that decides whether clearing is safe at all

`keep` and oldest-first govern *when* to clear. Neither governs *what* is safe to clear, and a stub that reads "re-read if needed" is a lie for any result that cannot be cheaply re-obtained.

Only clear results that are **deterministic and cheap to re-issue**. A file read, a grep, a directory listing, a test run: clear those freely. A non-deterministic query, a timestamped snapshot, a metered API call, or anything with a side effect (a payment confirmation, a created ticket identifier, the response to a write) must not be cleared, because the stub promises a recovery path that does not exist and the agent will act on that promise. Those get **summarised**, not cleared: a deliberate downgrade to the more expensive rung, and the one case in this post where the cheaper rung is the wrong answer (Context Engineering, Post 12 §4). `exclude_tools` is that rule expressed as an allow-list, which is why it belongs in the table above rather than in a footnote.

---

## 5. Compact: summarise the older turns (lossy)

Offloading and clearing both handle *observations*. Sometimes the window fills with **history itself**: dozens of ordinary turns whose sheer number, not any single message, is the problem. The move here is **compaction**: replace the older turns with a summary of them.

The keyword is **lossy**. A summary is smaller than what it summarises *because it discards detail*, and the discarded detail might have mattered. So compaction is governed by an **information-loss budget**: decide, in advance, what must survive a summary and what may be dropped. This is the runtime edge of the *Compress* primitive the Context Engineering series treats in full (Post 12); the harness concerns are *when* it fires, *what* the summary is contractually required to keep, and *where* it is safe to cut.

### The contract is the prompt

An information-loss budget with no text is not a contract. Prefer a **structured** brief over free prose, because a structure you control is a structure you can trust to retain the load-bearing facts.

```
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

Fields three and four are what make this a *run* brief rather than a *conversation* brief. A chat summariser that preserves decisions and open questions is doing its job; an agent resumed from that summary still does not know which files it has already edited or whether the suite was green when it stopped, and it will rediscover both at the cost of several turns.

### Cutting the history without breaking the request

The obvious implementation slices the message list by count, and it produces an invalid request on its first real run. `messages[-keep_last:]` cuts wherever arithmetic lands, and in an agentic transcript that is usually between an assistant turn carrying a `tool_use` block and the user turn carrying its matching `tool_result`. Providers reject an orphaned `tool_result`, so the harness gets a 400 and no obvious reason for it. Injecting the brief as a fresh message immediately before another user turn is the second hazard in the same three lines.

The fix is a policy and a loop: walk the cut backwards until it lands where no tool call is left open and the next message is a plain user turn, then fold the brief into that turn rather than adding a message of its own.

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
    """Fold the head into one brief, cutting only where no tool call is open."""
    cut = max(1, len(messages) - keep_last)
    while cut > 1 and (open_tool_uses(messages[:cut])
                       or messages[cut]["role"] != "user"):
        cut -= 1
    head, tail = messages[:cut], list(messages[cut:])
    if len(head) < 2:
        return messages                       # nothing worth folding yet
    brief = {"type": "text", "text": "[brief of earlier turns]\n" + summarise(head)}
    body = tail[0]["content"]
    tail[0] = {"role": "user", "content": [brief] + (
        body if isinstance(body, list) else [{"type": "text", "text": body}])}
    return tail
```

The summariser is an injected callable rather than a method invented on some object, so the prompt above is what you swap when the loss budget changes; and the system prompt is pinned outside the message list entirely, so a compactor can never fold an instruction into the summary it is meant to obey.

Pair integrity and message sequencing are also exactly what a server-side compactor handles for you. Anthropic ships one behind the beta header `compact-2026-01-12`: it summarises earlier context into a compaction block once input tokens reach a trigger that defaults to 150,000, and the caller's obligation reduces to appending the whole response content back, compaction block included (Anthropic, 2026). If your provider ships compaction, the boundary bug above is a good reason to use theirs rather than roll your own.

### When to fire it

"At a fill threshold" needs a number. The sibling series offers two as illustrative defaults rather than a measured law: a **soft trigger at 80 %** of the window, where the cheap moves run (clear results that have been acted on, drop low-priority material), and a **hard trigger at 95 %**, where older turns are summarised into a brief (Context Engineering, Post 12 §9). Tune both to your own token-usage variance, and move them down when tool outputs are large and variable. The gap between them exists so the expensive, lossy move is not the first thing that happens when a window gets busy.

There is also a mechanical reason the hard trigger cannot sit as high as it reads: 95 % of a 200,000-token window leaves 10,000 tokens, which is not room enough for the summarisation to run inside the loop. The compaction has to be a separate request against the head, and the trigger has to leave headroom for it. Shipped systems, tellingly, use **absolute** token triggers as often as percentages: 100,000 input tokens for context editing, 150,000 for server-side compaction (Anthropic, 2025; Anthropic, 2026). An absolute trigger is easier to reason about when one policy runs against several models with different window sizes.

Finally, trigger on *fill*, not on turn count. Twenty terse turns and five turns carrying a build log each are not the same situation, and a policy that counts turns will compact the first and miss the second.

---

## 6. Reset: wipe the window behind a handoff (total)

When the window is *fundamentally* too full (the task has outgrown a single context, or rot has already set in and a summary cannot rescue it), the most aggressive move is a **full reset**: write a handoff file, discard the window entirely, and resume in a fresh one. That such a rung is needed at all is a reported finding rather than an inference: Anthropic's account of building a long-running coding agent records that compaction on its own was not sufficient at that length, and that the run depended on state written to disk and read back into each fresh context (Anthropic, 2025).

This is the [Post 08](../08-state-filesystem-git/index.md) handoff file doing context-management duty. The current state is distilled to disk; the window is thrown away; a new window is seeded with only the handoff and continues. The loss is **total**: everything not written to the handoff is gone. That is exactly why it is the last resort, and exactly why "the handoff must be complete" needs a definition rather than an adjective.

**The handoff contract.** Six fields, and a run that cannot fill one of them is not ready to reset:

- a pointer to the spec or issue the work serves, not a paraphrase of it;
- what is done, in terms a fresh session can verify (commits, passing checks);
- what is next, as one concrete action rather than a theme;
- decisions taken and the reason for each, so they are not relitigated;
- open questions, including anything the run was blocked on;
- the paths that matter, absolute, including the scratch files earlier rungs wrote.

**The completeness test.** Seed a fresh window with only the handoff and check that it can name the next concrete action without asking a question. That is cheap to run, and it is the only test that matters.

**The failure signature.** An incomplete handoff shows up in a trace as repeated work at the start of every fresh window: the resumed session re-derives a decision the previous one had already settled. If each reset costs three turns of rediscovery, the handoff is short a field.

The reset is what makes truly long-horizon work possible: running across dozens of wiped windows without unbounded context growth. Done over and over against a written spec, it *is* the **Ralph loop** of [Post 18](../18-long-horizon-ralph/index.md). Here it is one move among several; there it becomes the whole architecture.

![Three cards escalating from offload (lossless) to compact (lossy) to reset (total), each with what it does, when to use it, what it costs and the numbers the post gives for it, over a band splitting the preventative moves from the corrective ones.](diagrams/02-three-moves.svg)
*The three headline moves at a glance. §4's clear rung slots between the first two, and §7 adds the column none of the three cards carries.*

---

## 7. What each move costs the prompt cache

Every rung above has been priced in tokens saved. None has been priced against the **prompt cache**, and that is the line item most harnesses fail to budget for.

Prompt caching works on an exact **prefix** match: the key is the exact bytes of the rendered prompt up to each breakpoint, and any change at position *N* invalidates every breakpoint at or after *N*. The render order is tools, then system, then messages (Anthropic, 2025). Two consequences follow, and both are more precise than "compaction is a cache miss".

**A rewrite of the message list is not a *full* miss.** Tools and system render before messages, so a breakpoint on the last system block survives a compaction untouched. Anthropic's compaction guidance says so directly: place a breakpoint at the end of the system prompt and, when compaction occurs, "the system prompt cache remains valid and is read from cache; only the compaction summary needs to be written as a new cache entry" (Anthropic, 2026). What you lose is the message history's cache, from the rewrite onward.

**The bill is a cache write on the new prefix, not full price on the old one.** The pre-compaction window no longer exists, so nobody pays for it. What you pay is the write premium on the *post*-compaction prefix: 1.25× base input on the default five-minute time-to-live (TTL), 2× on the one-hour TTL, plus the loss of the roughly 0.1× reads you had been enjoying over the old prefix (Anthropic, 2025).

### The arithmetic

Take a 200,000-token window, a session sitting at 160,000 tokens, and two candidate compactions. Costs are in *token-equivalents*: tokens multiplied by their price relative to base input, so a 0.1× read of 160,000 tokens costs 16,000 equivalents.

| Line item | Deep: 160K → 25K | Shallow: 160K → 130K |
|---|---|---|
| Summary call over the head, read warm at 0.1× | 13,500 | 3,500 |
| Cache write on the new prefix at 1.25× | 31,300 | 162,500 |
| **The compaction event** | **44,800** | **166,000** |
| Saved on each later turn (0.1× of the tokens removed) | 13,500 | 3,000 |
| **Turns to break even** | **about 3** | **about 55** |

That table is the whole argument for **compact rarely and deeply**, and the reason is not the one usually given. The write premium is charged on the entire surviving prefix, not on the part you removed, so a shallow compaction pays almost the full write price to buy almost no read saving. Ten small compactions are not ten times as expensive as one large one; they are worse than that, because each of the ten pays a write on a prefix that is still nearly full.

The table also contains a trick worth taking. The summary call there is read *warm*: issue the summarisation request against the still-cached prefix with a trailing "summarise the above" instruction rather than pasting the head into a fresh request, and the head is read at roughly 0.1× instead of 1×. On the deep column that turns a 135,000-equivalent summarisation into a 13,500-equivalent one, and drops break-even from about twelve turns to about three. The run-level economics of that stable prefix are [Post 23](../23-economics-haas/index.md); this section is one specific way a harness destroys it.

Clearing pays a version of the same bill. The rule in §4 is oldest-first, so the rewrite lands near the front of the message list and invalidates nearly as much of the prefix as a compaction does. It is still the better rung, because it costs no model call and paraphrases nothing, but it is not free, and dribbling out a few cleared results per turn buys a fraction of the headroom for the same invalidation. Batch the clears.

---

## 8. Prevention: keeping bytes out of the prefix

One move you have already met belongs alongside these: **progressive disclosure** ([Post 07](../07-skills-mcp-runtime/index.md), which pairs it with the Model Context Protocol, MCP). Loading a skill's tools only when a turn needs them is context management applied to *tool schemas* rather than to history or output.

The useful axis is not which move you use but *when* it acts. **Preventative** moves act before bytes enter the prefix: progressive disclosure keeps schemas out, and offloading at the tool boundary keeps large outputs out. **Corrective** moves act on bytes already there: clearing, compaction, and reset all rewrite a prefix that has been built and cached. Offloading sits on both sides of that line depending on where it runs. Offload inside the tool wrapper and it is preventative, costing nothing in cache terms; offload after the output has already been appended and you are performing a clear, with a clear's cache bill.

That is the second, independent reason to build the preventative moves first. They are not merely cheaper: they are the only moves that leave the cached prefix untouched, and they reduce how often the corrective rungs have to run at all. Progressive disclosure earns that description on one condition: a newly triggered schema must be *appended* to the conversation rather than swapped into the tool block, which renders before system and messages alike, so swapping it invalidates the whole prefix and costs more than the schemas it keeps out ([Post 07](../07-skills-mcp-runtime/index.md) §6).

---

## 9. Choosing between them

The corrective moves form an escalation ladder, and the rule is to take the cheapest rung that solves the problem.

- **A single big output spiked the window?** Offload it. Lossless, cheap, no cache cost if it runs at the tool boundary (§3).
- **Old tool results nobody needs any more?** Clear them to stubs, in batches. No model call, nothing paraphrased (§4).
- **Many ordinary turns are the weight?** Compact the old head deeply, keep recent turns verbatim (§5).
- **The window is unrecoverable, or the task spans more than one window?** Reset behind a complete handoff (§6).
- **The result cannot be re-obtained?** Break the ladder and summarise it, even though clearing looks cheaper (§4).

![Four stacked rungs, cheapest first: offload, clear, compact, and reset, each with what it does, when to use it, what is lost, and what happens to the cached message history (untouched, broken from there on, rewritten from the cut, and starts over), over a table pricing a deep compaction against a shallow one in token-equivalents.](diagrams/03-escalation-ladder.svg)
*The same ladder with the column that is rarely budgeted for. Only offloading leaves the prefix intact; clearing breaks it from the cleared position, which is why clears should be batched. The cache column describes the message history: a breakpoint at the end of the system prompt survives all four rungs (§7).*

Set out with the cache column attached, the ladder reads differently from the way it is usually taught. Offloading is cheap in three separate senses (no model call, nothing paraphrased, no cache damage), clearing in two of the three, and compaction and reset in none. So "take the cheapest rung that works" survives, but the instruction underneath it is the interesting one: when you do reach for a rung that rewrites the prefix, make the rewrite large enough to be worth the invalidation.

Two meta-rules sit above the ladder. First, **prefer prevention** (§8): progressive disclosure and tool-boundary offloading keep the window from filling, so the corrective rungs run less often. Second, **measure before you trust**: compaction and resets are lossy, and the only way to know your loss budget is right is to evaluate the agent with and without them ([Post 22](../22-evaluating-harnesses/index.md) §7). A summary that silently drops a load-bearing fact is a bug you can only catch by looking for it.

---

## Common pitfalls

- **Dumping big tool output into the transcript.** The single most common cause of a bloated window, and the cheapest to fix. Offload it at the tool boundary and return an actionable pointer with head and tail (§3).
- **Summarising what could just be cleared.** A spent, re-issuable tool result can be stubbed for nothing; paraphrasing it costs a model call and risks altering it (§4, §5).
- **Clearing a result that cannot be cheaply re-obtained.** A stub promising "re-read if needed" is a lie for a payment confirmation or a timestamped snapshot, and the agent will believe it. Exclude those tools and summarise them instead (§4).
- **Compacting with no loss budget.** A brief that drops the goal, a decision, or which checks were green is worse than no brief. Write the summarisation prompt as a contract and pin the system prompt outside the head (§5).
- **Compacting on turn count, and compacting little and often.** Five turns carrying build logs and twenty terse turns are not the same window, so trigger on fill; and a shallow compaction pays nearly the full cache-write premium to buy almost no read saving (§5, §7).
- **Resetting behind an incomplete handoff.** Reset is total loss, so the handoff is the only thing that survives. Test it by seeding a fresh window with the handoff alone and checking that it can name the next action (§6).
- **Trusting a lossy move without evaluating it.** Compaction and resets degrade an agent silently, which means the degradation is invisible until it is measured with and without them (§9).

---

## Further reading

- Hong, K., Troynikov, A., & Huber, J., "Context Rot: How Increasing Input Tokens Impacts LLM Performance" (2025): the eighteen-model evaluation behind the term, and evidence that degradation begins well inside the advertised window.
- Anthropic, "Context editing" (2025-26): the `clear_tool_uses_20250919` strategy and its `trigger` / `keep` / `clear_at_least` / `exclude_tools` / `clear_tool_inputs` parameters, plus the documented note that clearing invalidates the cached prefix.
- Anthropic, "Managing context on the Claude Developer Platform" (2025): the evaluation numbers for context editing, alone and combined with a memory tool, and the 84 % token reduction on a 100-turn web-search run.
- Anthropic, "Compaction" (2026): server-side compaction, its absolute default trigger, its handling of tool-call pairing, and how to keep the system-prompt cache alive across a compaction.
- Anthropic, "Effective harnesses for long-running agents" (2025): the report that compaction alone was not sufficient on a long-running build, and the on-disk artefacts each fresh context resumed from.
- Anthropic, "Prompt caching" (2025): prefix matching, the tools/system/messages render order, and the read and write multipliers the arithmetic in §7 uses.
- ai-boost, "awesome-harness-engineering" (2026): the "Context Delivery & Compaction" section (offloading, summarisation, resets).
- Addy Osmani, "Agent Harness Engineering" (2026): compaction, tool-call offloading, and full resets as the runtime moves.
- Context Engineering, Post 03: lost-in-the-middle and how models read a window; Post 06: the context failure modes and the context-rot findings; Post 12: the *Compress* primitive, tool-result clearing, and information loss.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 10 — Continual learning & the ratchet](../10-continual-learning-ratchet/index.md)**: state that persists *across* tasks (the memory file, and turning failures into durable rules).
- **[Post 18 — Long-horizon & multi-context execution](../18-long-horizon-ralph/index.md)**: the reset move as an architecture: Ralph loops over a written spec.
- **[Post 08 — State & the filesystem](../08-state-filesystem-git/index.md)**: the disk every move in this post writes to, and the handoff file the reset rung depends on.
- **[Post 07 — Skills & MCP in the runtime](../07-skills-mcp-runtime/index.md)**: progressive disclosure, the preventative context move that keeps tool schemas out of the window.
