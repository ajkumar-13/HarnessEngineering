# 03 · The agent loop — ReAct, control loops, and stopping

> **TL;DR.** At its core, a harness is a loop: the model reasons, the harness runs the tool it asked for, feeds the result back, and calls the model again: **reason → act → observe**, repeated. The model itself is stateless; the loop is what carries the conversation forward. The hard part is not the loop body but the **stop conditions**, and the agent failures practitioners name most often are exits gone wrong rather than reasoning gone wrong. This post builds the minimal loop, shows exactly what one turn looks like on the wire of a provider application programming interface (API), and lays out the four layered exits every real loop needs.
>
> **After reading this you will be able to:**
> - Write the minimal reason → act → observe loop over a provider software development kit (SDK), and answer every tool call the way the API requires.
> - Read the loop's exit from the provider's `stop_reason` field rather than from the absence of a tool call.
> - Name the four layered stop conditions, check them in the right order, and size the cap and the budget with numbers.

![The agent loop: a user task enters REASON, which either calls a tool (ACT then OBSERVE, looping back) or returns a final answer, with a strip noting that exit 1 is a terminal stop_reason rather than an absent tool call; a panel shows one turn on the wire, pairing a tool_use id with the tool_result that answers it; and four cards below give the stop conditions with what fires each and the code companion's default.](diagrams/01-agent-loop.svg)
*The loop is small. The engineering is in the exits: a final answer is the goal; the other three are guards, against a loop that never ends, one that costs too much, and one that has stopped getting anywhere.*

> An [animated version of this loop](../../assets/animations/01-the-loop-turning.svg) walks one stage at a time, which is worth a look if the exits read as a list here rather than as four things checked on every turn. It falls back to a still, so nothing is lost if your reader does not animate it.

---

## 1. A harness is a loop

The thing that turns a text-completer into an agent is not a clever prompt: it is a **loop**. A single model call takes messages in and returns one response. An agent is what you get when you take that response, and, if it asked to use a tool, actually run the tool, hand the result back, and call the model again. Repeat until the model is done.

This is the **ReAct** pattern, *reason and act*, introduced by Yao et al. (2022): interleave the model's reasoning with actions in an environment, feeding each observation back so the next reasoning step can use it. In plain English, one turn of the loop is three moves:

- **Reason.** The model reads everything so far and decides what to do next. It either asks to call a tool, or produces a final answer.
- **Act.** If it asked for a tool, the harness executes that tool: runs the bash command, calls the API, reads the file.
- **Observe.** The harness puts the tool's result back into the conversation, so the model can react to it on the next turn.

The paper is worth more than its name. ReAct ran reasoning traces interleaved with actions against a Wikipedia search API on the question-answering benchmarks HotpotQA and FEVER, and on the two interactive benchmarks, ALFWorld and WebShop, it beat imitation-learning and reinforcement-learning baselines by 34 and 10 absolute points of success rate while being prompted with only one or two in-context examples (Yao et al., 2022). That last clause is the one to notice. ReAct was a *prompting format*: the model wrote `Thought:`, `Action:` and `Observation:` as plain text and the harness parsed them back out again. The pattern survived; the mechanism did not. A modern provider API emits structured tool-call blocks instead, so the interleaving the paper had to coax out of a text completion is now part of the wire format (§3).

Those three moves are the whole engine. Anthropic's "Building Effective Agents" (2024) draws the same picture and makes the key distinction: a *workflow* wires model calls together on fixed rails, whereas an *agent* lets the model drive the loop, choosing its own tools and deciding when it is finished. This series is about building the second kind well, with the caveat that the same piece attaches: it recommends "finding the simplest solution possible, and only increasing complexity when needed", and reserves the agent shape for open-ended problems where the number of steps cannot be predicted and no fixed path can be hardcoded (Anthropic, 2024). [Post 16](../16-multi-agent-orchestration/index.md) carries that default one level up, to the number of agents.

---

## 2. The minimal control loop

Stripped to its essentials, the loop is a dozen lines. This is the code companion's `run()` with two of its four exits removed for legibility:

```python
def run(model, tools, task, *, system=None, max_iters=12):
    tool_map = {t.name: t for t in tools}
    messages = [{"role": "user", "content": task}]
    for step in range(1, max_iters + 1):
        resp = model.respond(system, messages, tools)          # REASON
        messages.append({"role": "assistant", "content": resp.content_blocks})
        if resp.is_final():                                    # stop ①: a final answer
            return resp.text
        results = []
        for tu in resp.tool_uses:                              # ACT
            tool = tool_map.get(tu.name)
            output = tool.run(tu.input) if tool else f"error: unknown tool '{tu.name}'"
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": output})
        messages.append({"role": "user", "content": results})  # OBSERVE
    return "stopped: hit max_iters"                            # stop ②: the backstop
```

Three things are worth noticing already. First, the loop body is trivial: call, check, execute, append. Second, there are *already two ways out*: the model returns a final answer (the good exit), or the `for` runs out of iterations (the backstop). A real loop adds two more exits, which §7 covers. Third, the ACT step iterates `resp.tool_uses` in the plural, because one turn can ask for several tools at once; §3 explains what that obliges the harness to do.

The runnable, fuller version (with a scripted model so it executes offline with no API key) lives in [`code/03-agent-loop/`](../../code/03-agent-loop/), and §11 names what is in it.

---

## 3. Where the loop lives: one turn on the wire

The sentence "the harness puts the tool's result back into the conversation" hides the only part of the loop a provider actually constrains. Here is one turn of the companion's demo as it goes over the wire, narration elided: the assistant message the model returned, then the user message the harness sends back.

```python
{"role": "assistant", "content": [
    {"type": "text", "text": "..."},                    # the model's narration
    {"type": "tool_use", "id": "tu_1", "name": "calculator",
     "input": {"expression": "(2 + 3) * 4"}}]}

{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "tu_1", "content": "20"}]}
```

Two rules of the API govern that exchange, and they are the two a first loop gets wrong (Anthropic, 2024–26).

**Every tool call is answered by id.** The `tool_use` block carries an `id`; the `tool_result` that answers it must repeat that id in `tool_use_id`. Pairing by position, or by tool name, breaks the moment a turn contains two calls to the same tool. Note also that the tool's *result* travels in a message with `"role": "user"`. It is not a third role; observations re-enter the conversation as though the user supplied them.

**One turn's results go back in one message.** When a turn contains several `tool_use` blocks, run them, then return *all* of their results in a **single** user message that contains nothing but `tool_result` blocks. Splitting them across several messages is not a syntax error and no exception is raised; it simply trains the model to stop asking for calls in parallel, and the loop gets slower for reasons nothing in the trace explains.

The third rule is not the API's but yours, and it decides whether the loop is robust: **a tool never raises into the loop.** If the tool throws, or the model invents a tool that does not exist, the harness catches it and returns the failure *as the observation*, so the model reads the error on the next turn and can correct itself. Let the exception propagate and one bad argument ends the run and takes the transcript with it.

```python
try:
    output = tool.run(tu.input)
except Exception as e:                    # the tool failed; the run has not
    results.append({"type": "tool_result", "tool_use_id": tu.id,
                    "content": f"error: {e}", "is_error": True})
```

The `is_error: true` flag marks the block as a failed call rather than as data, which is what stops the model treating the string `"error: division by zero"` as an answer worth reporting. The companion does the first half of this and not the second: its calculator catches everything and returns `f"error: {e}"`, and its unknown-tool branch returns `f"error: unknown tool '{tu.name}'"`, but neither sets the flag. Add it in production code. Rejecting a malformed call before it ever reaches the tool is the earlier gate, and that is schema validation ([Post 06](../06-tools-bash-code/index.md)).

---

## 4. How the API signals an exit

The `is_final()` in §2 asks whether the model requested any tools. That is the simplified form, and it is wrong in a way that costs real money. A provider response carries an explicit `stop_reason` field saying *why* generation stopped, and several of its values produce a turn with no tool call that is emphatically not an answer (Anthropic, 2026).

| `stop_reason` | What happened | What the loop should do |
|---|---|---|
| `end_turn` | The model finished on its own. | Take exit ①: this is the answer. |
| `tool_use` | The model asked for one or more tools. | Run them, append the results, keep looping. |
| `max_tokens` | The turn was cut off at the output ceiling. | Truncated, not finished. Continue the response or fail loudly; never read it as an answer. |
| `stop_sequence` | A configured stop string was emitted. | End the turn, and check which sequence fired. |
| `refusal` | The model declined on safety grounds. | Surface it and stop; read `stop_details` for the category. |
| `pause_turn` | A long-running server-side tool hit its own limit. | Send the turn back unchanged to continue it. |
| `model_context_window_exceeded` | The response filled the window. | Treat as truncated, and manage the context ([Post 09](../09-context-management-loop/index.md)). |

The row that bites is `max_tokens`. A turn truncated at the output ceiling comes back with no `tool_use` block, so a loop whose exit ① is "no tool call" returns a half-finished sentence as the agent's final answer, with no error anywhere and a `stop_reason` sitting unread in the response object. `refusal` and `pause_turn` fail the same test. Write exit ① as a *terminal stop reason* rather than as an absence, and the whole class disappears:

```python
TERMINAL = {"end_turn", "stop_sequence"}

def is_final(resp) -> bool:
    return resp.stop_reason in TERMINAL and not resp.tool_uses
```

The companion's `ModelResponse.is_final()` returns `not self.tool_uses`, which collapses the first two rows of the table and ignores the rest. That is deliberate: the scripted model it drives never truncates, so the offline suite cannot exercise the branch. Treat it as the teaching version and the four lines above as the shipping one.

---

## 5. The model forgets, the loop remembers

A point that trips up newcomers: the model has **no memory between calls**. Each call is independent from its point of view: messages in, one response out, nothing retained. The illusion of a continuous conversation is manufactured entirely by the harness, which keeps the running list of messages and **re-sends the whole thing on every turn**.

![The model drawn as a stateless function on the left, listing what goes in on every call in cache prefix order and the single response that comes out; on the right, the loop holds a conversation history that grows each turn, sending the full history to the model and appending the one new message it returns; a table below gives what re-sending that history is billed across three runs under the same iteration cap.](diagrams/02-stateless-model.svg)
*The model retains nothing between calls. Continuity is the harness re-sending a history that grows every turn.*

Be precise about which layer the claim applies to. The *model* retains nothing. The API around it often does: a cached prefix is held server-side for a short lifetime, server-side compaction returns blocks the next request reuses, and a managed agent runtime may run the loop and hold the session on the provider's side entirely. None of that is memory the model can reason over; it is transport optimisation, and where a provider runs the loop for you the harness has not vanished, it has moved to their side of the boundary ([Post 23](../23-economics-haas/index.md)).

Statelessness has three consequences that shape the rest of the series:

- **The history only grows.** Every tool result, every reasoning step, is appended. Left unmanaged it fills the context window and the model's quality degrades, the *context rot* problem (Context Engineering, Posts 03, 06). Managing that growing history at runtime (compaction, offloading, resets) is [Post 09](../09-context-management-loop/index.md).
- **State that must survive belongs on disk, not just in the list.** If the process dies, the in-memory history is gone. Durable state (files, git, handoff artefacts) is [Post 08](../08-state-filesystem-git/index.md).
- **Re-sending the same prefix every turn is what makes prompt caching matter.** Caching is a *prefix match*: the provider reuses the longest identical head of the request, rendered in the order tools, then system prompt, then messages (Anthropic, 2025). An append-only history is therefore not merely compatible with caching, it is the only history discipline that gets a hit at all. The corollary is the practical one: anything that mutates the head, a timestamp in the system prompt or a re-sorted tool list, invalidates every turn after it, and the loop quietly pays full price for the rest of the run (Context Engineering, Post 05).

The loop's own state deserves the same treatment. Persist the messages list, the step counter and the tokens spent after each turn, and a killed run can re-enter the loop at step *k* with its budgets intact instead of paying for the first *k* turns twice. This is why the companion's `Result` carries `transcript`, `iterations` and `tokens_used` rather than only an answer string: every exit returns a reason *and* a state, which is what makes resumption possible at all.

The model is a stateless function, though not a deterministic one: sampling means the same messages need not produce the same response. The loop is the stateful machine wrapped around it. Harness engineering is mostly the engineering of that machine.

---

## 6. What the loop carries between turns

Because the model is stateless (§5), everything the next turn needs must be in what the harness sends. Three things ride along:

- **The message history**: system prompt, the user task, and every `assistant → tool_use` / `user → tool_result` pair so far. This is the backbone.
- **Tool results**: appended as observations. Large results (a 2,000-line log) should be *offloaded* to disk with only a pointer left in the history, or they crowd out everything else and, as §8 shows, they are billed again on every subsequent turn; that technique is [Post 09](../09-context-management-loop/index.md).
- **A scratchpad, optionally**: a running plan or notes the model writes to and re-reads, so its intent survives a long tool detour. Scratchpads and plan files are a *Write* strategy (Context Engineering, Post 08), used here as loop state.

A useful test when debugging: if the agent "forgot" something mid-run, ask whether that something was actually in the messages sent on the failing turn. Usually it was not.

---

## 7. Stopping is the hard part

The loop body is easy. Deciding **when to stop** is where real loops earn their keep, because an agent that runs on its own can fail in exactly two expensive directions: stop too early and ship half-done work, or never stop and burn money in circles. A production loop carries four layered stop conditions, checked every turn.

**① A final answer: the correct reason to stop.** The model has finished, signalled by a terminal `stop_reason` and no tool call (§4). This is the exit you *want* the loop to take. Whether the work is *actually* done is a separate concern: verification, the subject of [Post 11](../11-verification-loops/index.md); a model that merely *declares* victory is [Post 05](../05-agent-failure-modes/index.md)'s first failure mode.

**② A hard maximum-iteration cap.** A blunt integer ceiling on turns. It exists so that a loop which never reaches ① still terminates. Never run a loop without one.

**③ A token or wall-clock budget.** Iterations are a poor proxy for cost; a single turn can be cheap or enormous (§8). A budget in tokens or seconds stops the loop once it has spent more than the task is worth.

**④ No-progress detection.** The subtlest exit. An agent can stay busy, calling tools every turn, while making no actual progress: re-running the same failing command, re-reading the same file, oscillating between two states. Detect it by watching for repeated tool calls across the last *N* turns and break (§9). Without this, an agent can burn its entire budget in a tight, productive-looking loop.

They are not four independent switches; they are checked in an order, and the order carries meaning:

| Exit | What it bounds | What it does not bound | How to set it |
|---|---|---|---|
| ① final answer | nothing: it is the goal | whether the work is *correct* | verify it ([Post 11](../11-verification-loops/index.md)) |
| ② iteration cap | turns | tokens, seconds, money | well above the observed p95 turn count |
| ③ token/time budget | spend | turns, thrashing | what one run of this task is worth |
| ④ no-progress | repetition | slow but genuine progress | a window of *N* identical turns |

Check ① first, so a run that has just succeeded is not cut off by a guard it was about to satisfy. Check the budget before making the call that would breach it, rather than after: the companion checks `tokens_used >= token_budget` *after* the model call it has already paid for, so its ceiling can be crossed by a full iteration, which in a long-context run is not a rounding error. [Post 19](../19-loop-engineering/index.md) sharpens exactly this into reserve-before-spend, and treats every guard exit as a resumable handoff rather than a full stop.

The reason this section matters more than the loop body is visible in where the field's attention has settled. The agent failure modes practitioners name most often are exits gone wrong: declaring victory without verifying the outcome, and rushing as the context window fills (Faros AI, 2026). Both are stop-condition faults, not reasoning faults, and both are fixed in the harness. That is the ground for this post's headline claim, and it is worth being clear about its status: it follows from which failures have proven worth naming, not from a published measurement comparing failure classes. Stop conditions are not error handling bolted on at the end. They are the primary design surface of the loop.

---

## 8. Sizing the cap and the budget

The claim that iterations are a poor proxy for cost is easy to assert and easy to check. Take the run-cost model from [Post 23](../23-economics-haas/index.md): a twelve-iteration task whose first turn sends about 6,000 tokens and whose twelfth sends about 40,000, growing by roughly 3,100 tokens a turn as each response and each observation is appended. Because the whole history is re-sent every turn (§5), what the run is billed for is the *sum* of those inputs, not the last one.

| Run (all with `max_iters=12`) | Iterations used | Input tokens re-read | At $3 per million input |
|---|---|---|---|
| Answers at iteration 6 | 6 | ~83,000 | ~$0.25 |
| Runs to the cap | 12 | ~277,000 | ~$0.83 |
| Runs to the cap, one 20,000-token log read at turn 5 | 12 | ~417,000 | ~$1.25 |

The arithmetic is worth doing once by hand. Twelve iterations averaging 23,000 tokens of input is 12 × 23,000 ≈ 277,000 tokens. Stopping at six averages 13,750, so 6 × 13,750 ≈ 83,000. And a single 20,000-token log read at turn 5 is not read once: it sits in the history for the seven turns that follow, adding 7 × 20,000 = 140,000 tokens to the same twelve iterations. Token counts and the per-million rate here are illustrative, at the mid-tier rate used in the sibling series (Context Engineering, Post 05); the shape is what transfers.

The conclusion in one line: the cap bounds turns, and turns bound nothing you are billed for. Rows two and three have identical iteration counts and a bill that differs by half again; rows one and three differ five-fold under the same cap. That is exit ③'s whole justification, and it is why a `max_iters` set "low to be safe" is a cost control in name only.

Which leaves the question the snippet in §2 quietly begs: what number belongs in `max_iters`? A cap is a backstop, not a schedule. Set it well above the p95 iteration count you actually observe for that class of task, because a cap set inside the working range converts ordinary long runs into `MAX_ITERS` exits and sends you debugging a failure that is really a configuration. For coding agents the sibling series puts a typical task at 5 to 50 iterations and a complex one in the hundreds (Context Engineering, Post 26), so the companion's `max_iters=12` is a demo number and nothing more. And when a run does hit the cap, treat it as a bug report to read rather than an outcome to accept: something either needed more room or was never going to converge.

---

## 9. No-progress detection without false positives

Exit ④ needs a mechanism, and the cheapest one that works is a fingerprint. Reduce each turn to a stable string built from the tool calls it asked for, keep the last *N*, and stop when that window collapses to a single distinct value:

```python
def _signature(tool_uses: list[ToolUse]) -> str:
    """A stable fingerprint of a turn's tool calls, for no-progress detection."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)

recent.append(_signature(resp.tool_uses))
window = recent[-no_progress_window:]
if len(window) == no_progress_window and len(set(window)) == 1:
    return Result(None, StopReason.NO_PROGRESS, step, tokens_used, messages)
```

`sort_keys=True` is doing quiet work there: without it, two identical calls whose argument dictionaries serialise in a different order look like progress. The companion's window is 3, which is short enough to catch a tight doom loop within a few turns and long enough that a single repeat is not treated as a failure.

The mechanism has a real cost, and it is the reason this exit is the last one to add: it is the only guard whose naive form actively harms correct agents. An agent polling a build until it finishes, retrying a flaky network call with backoff, or re-reading a file it has just edited emits a stream of identical fingerprints that is indistinguishable from thrashing, and gets killed for making progress. Three ways to separate the cases, cheapest first:

- **Fold the observation into the fingerprint.** Identical *calls* are only evidence of a stall when the *results* are unchanged too. A build poll that returns "running", "running", "passed" is progress; three identical failures are not.
- **Widen the window for tools that are legitimately polled.** A per-tool window costs one dictionary lookup and removes most false positives on its own.
- **Exempt named idempotent tools by hand.** Blunt, explicit, and easy to audit; use it for the handful of tools that are genuinely meant to be called repeatedly.

Whatever you choose, log the fingerprint alongside the exit reason. "no-progress at iteration 7, signature `[[read_file, {path: src/main.py}]]`" is a diagnosis; "no-progress" alone is a mystery, and the trace-reading skill it feeds is [Post 21](../21-observability-traces/index.md).

---

## 10. Streaming versus batch turns

One implementation choice worth naming early. A turn can be **batch** (call the model, wait for the complete response, then act) or **streaming** (read the response as it is generated, and begin executing a tool call the moment it is fully formed, even before the model finishes speaking).

![Two timelines for one agent turn on the same scale: in the batch row the harness cannot start the tool until the model bar ends, while in the streaming row a dashed marker part-way through the model bar shows where the tool call becomes fully formed and the tool bar starts there, so the next call begins earlier; a bracket between the two next-call positions is labelled latency saved. A side panel gives the fine print, how partial-JSON deltas decide when a call is fully formed and which benefits are genuinely streaming's, and three cards close by contrasting what each schedule costs the harness.](diagrams/03-batch-vs-streaming.svg)
*The same turn, two schedules. The bracket is what streaming buys: the tail of a response you no longer wait through.*

Drawn on one time axis, the difference is easy to state and easy to over-value. The model spends the same time generating either way; what changes is that a streaming harness may start the tool the moment its arguments are complete, instead of after the last token. The saving is the tail of the response, which is real but bounded.

"Fully formed" has a precise meaning worth knowing before you rely on it. A tool's arguments do not arrive whole: they arrive as a series of partial-JSON deltas (`input_json_delta` events carrying a `partial_json` fragment), which the harness concatenates until the accumulated string parses as valid JSON. Providers also expose a per-tool flag, `eager_input_streaming`, that makes those fragments start arriving sooner (Anthropic, 2026). That accumulating buffer, and the question of what the loop does with a tool call that is 80% received when the stream drops, is the extra state streaming costs you.

Two benefits genuinely belong to streaming. A human watching sees output immediately rather than after a long pause, and a run can be **interrupted mid-turn** by that human, which is the primitive underneath approvals and steering ([Post 15](../15-human-in-the-loop/index.md)). One benefit often attributed to streaming is not its own: *interleaved thinking*, where the model reasons between tool results rather than only at the front of a turn, is a property of the model and the API, and it works identically on a non-streaming call (Context Engineering, Post 18). Streaming changes when you observe the tokens, not what the model does between them.

Batch is simpler and is the right default for building and understanding a loop; the code companion is batch. The loop's *logic* (reason, act, observe, and the four exits) is identical either way. Start batch; reach for streaming when latency or interruptibility, not correctness, is the bottleneck.

---

## 11. Putting it together

The loop is the core of the harness map from [Post 02](../02-anatomy-of-a-harness/index.md): every other component either feeds this loop (tools, state, context management, memory), governs it (verification, hooks, permissions, observability), or works at a larger scale around it (orchestration, long-horizon patterns). Get the loop and its exits right and the rest of the series has a spine to attach to.

The [code companion](../../code/03-agent-loop/) implements §§1 to 9 in their teaching form: `run()` in `loop.py` with all four exits and a `StopReason` for each, `ScriptedModel` for offline runs and `AnthropicModel` for real ones, and two small tools of which the calculator evaluates through an abstract-syntax-tree walker rather than `eval`. Seven tests cover the exits and the failure paths (`python -m pytest -q`, no API key needed), and `python -m agent_loop` prints one reason → act → observe → answer cycle with its transcript. Streaming (§10) is deliberately left out, and so is the `stop_reason` refinement from §4. Read it alongside this post; it is the shortest path from understanding the diagram to building one.

---

## Common pitfalls

- **Running a loop with no cap.** If ① is the only exit, a model that never says "done" runs forever. Always ship ② as well (§7).
- **Treating "no tool call" as a final answer.** A turn truncated at `max_tokens`, a refusal, and a paused server tool all arrive with no tool call and none of them is an answer. Read `stop_reason` (§4).
- **Using `max_iters` as a cost control.** Turns are not a proxy for tokens; the same twelve-iteration cap covers a five-fold spread in the bill. Add a real budget, ③, and check it before the call that would breach it (§7, §8).
- **Killing an agent that is legitimately repeating.** A build poll and a doom loop have the same call signature. Fold the observation into the fingerprint before you trust ④ (§9).
- **Letting a tool exception escape into the loop.** One bad argument then ends the run instead of teaching the model something. Catch it, return it as the observation, and flag it with `is_error` (§3).
- **Assuming the model remembers.** It does not; only what the harness re-sends exists. "It forgot" almost always means "it was not in the messages" (§5, §6).
- **Conflating "final answer" with "correct answer."** Stopping on ① means the model *thinks* it is done, not that it *is*. Verification is a separate step ([Post 11](../11-verification-loops/index.md)).

---

## Further reading

- Yao, S. *et al.* "ReAct: Synergizing Reasoning and Acting in Language Models" (ICLR 2023, arXiv 2022): the reason → act → observe pattern, with the HotpotQA, FEVER, ALFWorld and WebShop results behind it.
- Anthropic Engineering, "Building Effective Agents" (December 2024): workflow versus agent; the model-plus-loop framing, and the argument for the simplest pattern that works.
- Anthropic, "Handling stop reasons", Messages API documentation (2026): every `stop_reason` value and what a loop should do with each.
- Anthropic, "Tool use" documentation (2024–26): the `tool_use` / `tool_result` id pairing, the single-message rule for parallel calls, and `is_error`.
- awesome-harness-engineering (2026), the "Agent Loop" section: lifecycle hooks, mid-loop state persistence for resumption, stopping.
- Faros AI, "Harness Engineering" (2026): the harness-level failure modes, victory declaration and context anxiety, that this post's stop conditions are aimed at.
- Context Engineering, Post 05: prompt caching and the stable prefix, which is why re-sending a growing history is affordable at all.
- Context Engineering, Post 08, the *Write* primitive: scratchpads and plan files, used here as loop state.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 04 — Why the harness beats the model](../04-harness-beats-model/index.md)**: the evidence that engineering this loop matters more than swapping the model.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: the named ways a loop goes wrong (victory declaration, doom loops) and the exit that fixes each.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the ACT step in depth, including the schema validation that rejects a bad call before §3's error path ever runs.
- **[Post 19 — Loop engineering](../19-loop-engineering/index.md)**: these four exits again, checked in priority order, with the budget enforced before the call that would breach it.
- **[Post 02 — The anatomy of a harness](../02-anatomy-of-a-harness/index.md)**: where this loop sits in the eleven-component map, if you skipped it.
