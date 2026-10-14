# 03 - The agent loop: ReAct, control loops, and stopping

> **TL;DR.** A harness is a loop: the model reasons, the harness runs the tools it asked for and feeds the results back, and the model is called again, **reason, act, observe**, until something stops it. The model keeps nothing between calls, so the loop carries the whole history and re-sends it on every turn, which is also why a count of turns says little about cost. The hard part is the stopping: a final answer read from the provider's `stop_reason` field, an iteration cap, a budget, and no-progress detection, numbered in that order. This post builds the loop on the wire format of the Anthropic Messages application programming interface (API), runs it offline against the companion's scripted model, and sizes each exit.
>
> **Prerequisites:** [Post 02 - The anatomy of a harness](../02-anatomy-of-a-harness/index.md).
> **Safe to skip?** Skip it if the reader can already write a tool-calling loop that answers every `tool_use` block by id, stops on a terminal `stop_reason` rather than on a missing tool call, and carries a cap, a budget and a no-progress check that does not kill an agent polling a build.
>
> **After reading, you will be able to:**
>
> - Write the minimal reason, act, observe loop over a provider API, answering every `tool_use` block by id in one user message of results.
> - Act on every `stop_reason` value, and take the final-answer exit on a terminal stop reason rather than on a missing tool call.
> - Explain why the model is stateless, what the loop must carry and re-send on every turn, and what re-sending a growing history costs in tokens.
> - Implement the four exits in order, size the cap and the budget from a run's token arithmetic, and detect no progress without killing a polling agent.
> - Choose between batch and streaming turns, and say what streaming does and does not buy a loop.

![A clockwise cycle of reason in blue, act in orange and observe in green. After each model call a purple stop check leads to four exits in order: final answer, iteration cap, budget and no progress, each with the condition that fires it and the companion's setting.](diagrams/01-agent-loop.svg)

*The loop is three steps; the engineering is in the four exits, and only the first of them means the work may be done.*

---

## 1. The question: what turns a model call into an agent?

A single call to a large language model (LLM) takes messages in and returns one response. What turns it into an agent is a **loop**: if the response asks for a tool, run the tool, hand the result back, and call the model again, until something says stop. That loop is the first of the eleven components that [post 02](../02-anatomy-of-a-harness/index.md) names, the one at the centre of the map.

The pattern is **ReAct**, *reason and act*, introduced by Yao et al. (2023): interleave the model's reasoning with actions in an environment, feeding each observation back so the next reasoning step can use it. One turn of the loop is three moves:

- **Reason.** The model reads everything so far and decides what to do next: call a tool, or give a final answer.
- **Act.** If it asked for a tool, the harness executes it: runs the command, calls the service, reads the file.
- **Observe.** The harness puts the tool's result back into the conversation, so the model can react to it on the next turn.

ReAct ran against a simple Wikipedia API on the question-answering and fact-verification benchmarks HotpotQA and FEVER, and on the interactive benchmarks ALFWorld and WebShop it beat imitation-learning and reinforcement-learning baselines by 34 and 10 absolute points of success rate, prompted with only one or two in-context examples (Yao et al., 2023). It was a *prompting format*: the model wrote `Thought:` and `Action:` as plain text; the harness parsed the action and appended the `Observation:`. The pattern survived; the mechanism did not. A modern provider API returns structured tool-call blocks, so the interleaving is now part of the wire format (section 3).

Anthropic's "Building effective agents" (19 December 2024) makes the key distinction. Workflows are "systems where LLMs and tools are orchestrated through predefined code paths"; agents are "systems where LLMs dynamically direct their own processes and tool usage". It recommends "finding the simplest solution possible, and only increasing complexity when needed", keeping agents for open-ended problems whose number of steps cannot be predicted (Anthropic, 2024); [post 16](../16-multi-agent-orchestration/index.md) applies the same default to the number of agents.

The figure at the top draws the loop and the question this post answers: once it turns, what stops it? The same article notes that "it's also common to include stopping conditions (such as a maximum number of iterations) to maintain control" (Anthropic, 2024). This post argues that those conditions are the main design surface of the loop and builds the four every real loop needs. An [animated version of the loop](diagrams/06-the-loop-turning.svg) walks one stage at a time, over a still that is the complete diagram.

---

## 2. The minimal control loop

Stripped to its essentials, the loop is sixteen lines. This is the code companion's `run()` with exits (3) and (4) removed and a plain return value, for legibility, as `snippets/minimal_loop.py` runs it against the companion's scripted model:

```python
def run(model, tools, task, *, system=None, max_iters=12):
    tool_map = {t.name: t for t in tools}
    messages = [{"role": "user", "content": task}]
    for step in range(1, max_iters + 1):
        resp = model.respond(system, messages, tools)          # REASON
        messages.append({"role": "assistant", "content": resp.content_blocks})
        if resp.is_final():                                    # exit (1): a final answer
            return resp.text, messages
        results = []
        for tu in resp.tool_uses:                              # ACT
            tool = tool_map.get(tu.name)
            output = tool.run(tu.input) if tool else f"error: unknown tool '{tu.name}'"
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": output})
        messages.append({"role": "user", "content": results})  # OBSERVE
    return "stopped: hit max_iters", messages                  # exit (2): the backstop
```

The body is trivial: call, check, execute, append. There are already two ways out, a final answer (the exit the loop is for) and the `for` running out of iterations (the backstop); section 7 adds two more. And the act step iterates `resp.tool_uses` in the plural, because one turn can ask for several tools, all of which must be answered together.

The runnable, fuller version, with a scripted model so it executes offline with no API key, is the [code companion](../../code/03-agent-loop/); section 11 says what is in it and how to run it.

---

## 3. Where the loop lives: one turn on the wire

The sentence "the harness puts the tool's result back into the conversation" hides the only part of the loop a provider actually constrains. `uv run python posts/03-the-agent-loop/snippets/minimal_loop.py` runs the companion's demo task and prints one turn as it goes over the wire: the assistant message the model returned, then the user message the harness sent back.

```text
answer: The result is 20.  (4 messages, 2 model calls)

{"role": "assistant", "content": [{"type": "text", "text": "I'll compute that."}, {"type": "tool_use", "id": "tu_1", "name": "calculator", "input": {"expression": "(2 + 3) * 4"}}]}
{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "tu_1", "content": "20"}]}
```

Two rules of the API govern that exchange, and they are the two a first loop gets wrong (Anthropic, "Handle tool calls" and "Stop reasons and fallback", 2026).

**Every tool call is answered by id.** The `tool_use` block carries an `id`; the `tool_result` that answers it repeats that id in `tool_use_id`. Pairing by position, or by tool name, breaks the moment a turn contains two calls to the same tool. The tool's *result* travels in a message with `"role": "user"`: there is no third role, and observations re-enter the conversation as though the user supplied them.

**One turn's results go back in one message.** The reply to a `tool_use` turn is a single user message with a `tool_result` for every `tool_use` block of that turn, results before any text; the stop-reasons page advises adding none, since text after the results can make the model end its turn with an empty response. Anthropic's parallel tool use page calls bad result formatting the most common issue, and for parallel calls that means one user message per result: such a history "teaches" the model to avoid parallel calls, so the loop gets slower for reasons nothing in the trace explains (Anthropic, "Parallel tool use", 2026).

A third rule is the harness's own: **a tool never raises into the loop.** If a tool throws, or the model invents a tool, the harness returns the failure *as the observation*, so the model reads the error next turn and can correct itself; an exception that propagates ends the run on one bad argument. `snippets/tool_errors.py` answers one turn this way:

```python
def call_tools(tool_uses, tool_map):
    results = []
    for tu in tool_uses:
        tool = tool_map.get(tu.name)
        if tool is None:                      # the model invented a tool
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": f"error: unknown tool '{tu.name}'", "is_error": True})
            continue
        try:
            output = tool.run(tu.input)
        except Exception as e:                # the tool failed; the run has not
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": f"error: {e}", "is_error": True})
            continue
        results.append({"type": "tool_result", "tool_use_id": tu.id, "content": output})
    return results
```

Given a turn of three calls, a good calculator call, a read of a file that does not exist, and a call to a `search` tool the harness never offered, it prints:

```text
{"type": "tool_result", "tool_use_id": "tu_1", "content": "20"}
{"type": "tool_result", "tool_use_id": "tu_2", "content": "error: [Errno 2] No such file or directory: 'no/such/file.txt'", "is_error": true}
{"type": "tool_result", "tool_use_id": "tu_3", "content": "error: unknown tool 'search'", "is_error": true}
one user message, 3 results, ids ['tu_1', 'tu_2', 'tu_3']
companion calculator on 1 / 0: 'error: division by zero'
```

The `is_error` flag, set "if the tool execution resulted in an error" in the documentation's words, marks the block as a failed call rather than as data. The companion does half of this: its calculator and its unknown-tool branch return error strings, as the last line shows, but neither sets the flag. Rejecting a malformed call before it reaches the tool is the earlier gate, schema validation, in [post 06](../06-tools-bash-code/index.md).

---

## 4. How the API signals an exit

The `is_final()` of section 2 asks whether the model requested any tools. That is the simplified form, and it is wrong in a way no error reports. A provider response carries an explicit `stop_reason` field saying *why* generation stopped, and several of its values produce a turn with no tool call that is not an answer. Anthropic's "Stop reasons and fallback" page (2026) lists seven:

| `stop_reason` | What happened | What the loop should do |
|---|---|---|
| `end_turn` | The model finished on its own. | Take exit (1): this is the answer. |
| `tool_use` | The model asked for one or more tools. | Run them, append the results, keep looping. |
| `max_tokens` | The turn was cut off at the `max_tokens` ceiling. | Truncated, not finished: raise the ceiling or continue the response; never read it as an answer. |
| `stop_sequence` | A configured stop string was emitted. | End the turn, and read `stop_sequence` to see which one fired. |
| `refusal` | The model declined to respond. | Read `stop_details` (the policy category); retry on a fallback model, or surface it and stop. |
| `pause_turn` | A server-side tool loop reached its iteration limit. | Send the assistant content back as it is to continue. |
| `model_context_window_exceeded` | The response filled the model's context window. | Treat it as truncated, and manage the context ([post 09](../09-context-management-loop/index.md)). |

The row that bites is `max_tokens`. A turn truncated at the output ceiling comes back with no `tool_use` block, so a loop whose exit (1) is "no tool call" returns a half-finished sentence as the agent's final answer, with no error anywhere and a `stop_reason` sitting unread in the response. `refusal`, `pause_turn` and `model_context_window_exceeded` fail the same test. Write exit (1) as a *terminal stop reason* rather than as an absence, and the whole class disappears. `snippets/stop_reasons.py` holds the check:

```python
TERMINAL = {"end_turn", "stop_sequence"}


def is_final(resp) -> bool:
    return resp.stop_reason in TERMINAL and not resp.tool_uses
```

Run over one response per `stop_reason`, the naive check and this one disagree four times out of seven:

```text
stop_reason                     tool call  naive: answer?  is_final():
end_turn                               no             yes          yes
tool_use                              yes              no           no
max_tokens                             no             yes           no
stop_sequence                          no             yes          yes
refusal                                no             yes           no
pause_turn                             no             yes           no
model_context_window_exceeded          no             yes           no
the naive check takes 4 non-answers as answers: max_tokens, refusal, pause_turn, model_context_window_exceeded
```

The companion's `ModelResponse.is_final()` returns `not self.tool_uses`, and its `ModelResponse` does not carry `stop_reason` at all. The scripted model never truncates, so the offline suite could not exercise the branch: the companion is the teaching version, and the four lines above the shipping one.

---

## 5. The model forgets, the loop remembers

The model has **no memory between calls**: messages in, one response out, nothing retained. The continuous conversation is manufactured by the harness, which keeps the list of messages and **re-sends all of it on every turn**. The figure below records what the companion's loop sends on each of three calls of one run.

![Three requests of one scripted run side by side, each the same head of tools and system prompt followed by the messages so far: one on call 1, three on call 2, five on call 3. The model keeps nothing; each response it returns is appended and re-sent.](diagrams/02-history-resent.svg)

*The model sees only what the harness sends; continuity is a history that grows by one call and one result per turn and is sent again in full.*

The claim is about the *model*. The API around it may hold things: a cached prefix for a few minutes, or, in a managed runtime such as Claude Managed Agents, the whole session ([post 23](../23-economics-haas/index.md)). None of that is memory the model reasons over; where a provider runs the loop, the harness has moved to the provider's side, not vanished.

Statelessness has three consequences that shape the rest of the series:

- **The history only grows.** Left unmanaged, it fills the context window and the model's quality degrades, the *context rot* that `ctx-003` and `ctx-006` describe. Managing that growing history at runtime (compaction, offloading, resets) is [post 09](../09-context-management-loop/index.md).
- **State that must survive belongs on disk, not only in the list.** If the process dies, the in-memory history is gone. Durable state (files, git, handoff artefacts) is [post 08](../08-state-filesystem-git/index.md).
- **Re-sending the same prefix every turn is what makes prompt caching matter.** Caching is a *prefix match*: the provider reuses the longest identical head of the request, rendered in the order tools, then system prompt, then messages (Anthropic, prompt caching documentation, 2025 to 2026). An append-only history keeps every earlier turn of that head identical, so each new call can reuse all of it. Anything that mutates the head, a timestamp in the system prompt or a re-sorted tool list, misses the cache on every turn after it (`ctx-005`).

The loop's own state deserves the same care. Persist the messages, the step counter and the tokens spent after each turn, and a killed run can re-enter at step $k$ with its budgets intact. That is why the companion's `Result` carries `transcript`, `iterations` and `tokens_used`: every exit returns a reason *and* a state.

The model is a stateless function, though not a deterministic one: sampling means the same messages need not produce the same response. The loop is the stateful machine wrapped around it, and harness engineering is mostly the engineering of that machine.

---

## 6. What the loop carries between turns

Because the model is stateless, everything the next turn needs must be in what the harness sends. Three things ride along:

- **The message history**: the user task and every assistant `tool_use` and user `tool_result` pair so far, sent after the tools and the system prompt. This is the backbone.
- **Tool results**, appended as observations. A large result, such as a 2,000-line build log, is better *offloaded* to disk with only a pointer left in the history; otherwise it crowds out everything else and, as section 8 shows, is billed again on every later turn. That technique is [post 09](../09-context-management-loop/index.md)'s.
- **A scratchpad, optionally**: a running plan or notes the model writes and re-reads, so its intent survives a long tool detour. Scratchpads and plan files are the *write* strategy of `ctx-008`, used here as loop state.

That gives a test for debugging: when an agent "forgot" something mid-run, check whether it was in the messages sent on the failing turn. If it was not, the fault is in what the harness carried, not in the model.

---

## 7. Stopping is the hard part

Deciding **when to stop** is where a real loop earns its keep, because an agent running on its own fails in two expensive directions: it stops too early and ships half-done work, or it never stops. A production loop carries four exits, numbered the same way throughout the series (the [notation guide](../../notation_guide.md) has the record) and checked in this order.

**(1) Final answer: the exit the loop is for.** The model has finished, signalled by a terminal `stop_reason` and no tool call, as section 4 set out. Whether the work is *actually* done is a separate question, verification, the subject of [post 11](../11-verification-loops/index.md); a model that merely *declares* victory is the first failure mode of [post 05](../05-agent-failure-modes/index.md).

**(2) Iteration cap.** A blunt integer ceiling on turns, so that a loop which never reaches (1) still ends. No loop should run without one.

**(3) Budget.** A ceiling in tokens or wall-clock seconds, because one turn can be cheap or enormous (section 8).

**(4) No progress.** The subtlest exit. An agent can stay busy, calling tools every turn, while re-running the same failing command or re-reading the same file. The detector watches for repeated tool calls across the last $N$ turns (section 9); without it, an agent spends its whole budget in a busy-looking loop.

They are not four independent switches; the order carries meaning:

| Exit | What it bounds | What it does not bound | How to set it |
|---|---|---|---|
| (1) final answer | nothing: it is the goal | whether the work is *correct* | verify it ([post 11](../11-verification-loops/index.md)) |
| (2) iteration cap | turns | tokens, seconds, money | well above the turn count the task class needs |
| (3) budget | spend | turns, thrashing | what one run of this task is worth |
| (4) no progress | repetition | slow but genuine progress | a window of $N$ identical turns |

Check (1) first, so that a run which has just succeeded is not cut off by a guard it was about to satisfy. Check the budget before making the call that would breach it, not after: the companion checks `tokens_used >= token_budget` *after* the model call it has already paid for, so its ceiling can be crossed by a full turn. Section 11's run shows it: with 50 tokens a turn and a budget of 120, the companion stops on turn 3 having spent 150, a quarter over. In a long-context run one turn is tens of thousands of tokens. [Post 19](../19-loop-engineering/index.md) sharpens this into reserve-before-spend and treats every guard exit as a resumable handoff rather than a full stop.

Why give stopping this weight? Faros AI's guide to harness engineering (22 May 2026) lists, among failure modes "inherent to AI models but solvable at the harness level" that it credits to Anthropic's research, victory declaration bias ("Agents frequently mark a task complete without verifying the outcome") and context anxiety (as the window fills, models "rush to finish") (Faros AI, 2026). Both are faults of an exit, (1) taken too early, not of reasoning, and both are fixed in the harness. Faros gives no frequencies, so the claim that stop conditions are the main design surface of the loop is this series' argument from which failures have been named, not a measurement comparing failure classes.

---

## 8. Sizing the cap and the budget

The claim that iterations are a poor proxy for cost is easy to assert and easy to check. Take the series' running example of a run, which [post 23](../23-economics-haas/index.md) sets out in full: illustrative sizes, a first request of 6,000 input tokens, and each turn appending about 3,100 more as the response and the observation join the history, so that request $n$ sends $6{,}000 + 3{,}100(n - 1)$ tokens and the twelfth sends 40,100. Because the whole history is re-sent every turn, the run is billed for the *sum* of those inputs, not the last one. `uv run python posts/03-the-agent-loop/snippets/run_cost.py` prices three runs of the task under the same cap of 12, at 3 dollars per million input tokens, the Claude Sonnet 4.6 input rate on Anthropic's pricing page (consulted October 2026; the rate moves, so re-derive it against the current page):

```text
run, max_iters=12                                 turns  input re-read  at $3/M
answers at iteration 6                                6         82,500     0.25
runs to the cap                                      12        276,600     0.83
runs to the cap, one 20,000-token log at turn 5      12        416,600     1.25
request 1: 6,000  request 12: 40,100  log re-sent on 7 turns: +140,000
row 3 / row 2: 1.51   row 3 / row 1: 5.05
```

By hand: twelve requests rising evenly from 6,000 to 40,100 tokens sum to $12 \times (6{,}000 + 40{,}100) / 2 = 276{,}600$. Six requests from 6,000 to 21,500 sum to $6 \times (6{,}000 + 21{,}500) / 2 = 82{,}500$. A 20,000-token log read at turn 5 is not read once: it joins the history with that turn's result and is re-sent on the seven requests that follow, adding $7 \times 20{,}000 = 140{,}000$ tokens to the same twelve iterations. At 3 dollars per million, 276,600 tokens cost 0.83 dollars. The chart below draws the running total of each run turn by turn.

![Dashed illustrative curves of input tokens re-read against turn for three runs under a cap of 12: answering at iteration 6 stops at 82,500; running to the cap reaches 276,600; the run with a 20,000-token log at turn 5 bends away and reaches 416,600.](diagrams/03-run-cost.svg)

*Every turn re-reads the turns before it, so the curves bend upward, and one large observation raises every later turn of the run.*

The conclusion in one line: the cap bounds turns, and turns bound nothing the run is billed for. Rows two and three have the same iteration count and bills that differ by half again (1.51 times); rows one and three differ five-fold (5.05 times) under the same cap. That is exit (3)'s whole justification, and it is why a `max_iters` set "low to be safe" is a cost control in name only.

What number belongs in `max_iters`, then? A cap is a backstop, not a schedule: set it well above the iteration count that runs of that class of task need, measured from their traces, because a cap inside the working range turns ordinary long runs into `max_iters` exits. The companion's default of 12 is a demo number. A run that hits the cap is a bug report to read: the task needed more room or was never going to converge.

---

## 9. No-progress detection without false positives

Exit (4) needs a mechanism, and the cheapest one that works is a fingerprint. Reduce each turn to a stable string built from the tool calls it asked for, keep the last $N$, and stop when that window collapses to a single distinct value. `snippets/no_progress.py` restates the companion's check (its `signature()` is asserted equal to the companion's `_signature`):

```python
def signature(tool_uses):
    """A stable fingerprint of a turn's tool calls, the companion's _signature."""
    return json.dumps([[tu.name, tu.input] for tu in tool_uses], sort_keys=True)


def no_progress(recent, window=3):
    """Exit (4): the last `window` fingerprints are all the same."""
    last = recent[-window:]
    return len(last) == window and len(set(last)) == 1
```

`sort_keys=True` does quiet work there: without it, two identical calls whose argument dictionaries serialise in a different order look like progress. The companion's window is 3, short enough to catch a tight doom loop within a few turns and long enough that a single repeat is not treated as a failure.

This is the only guard whose naive form harms a correct agent. An agent polling a build, retrying a flaky network call, or re-reading a file it has just edited emits identical fingerprints, indistinguishable from thrashing, and is stopped for making progress. Three ways to separate the cases, cheapest first:

- **Fold the observation into the fingerprint.** Identical *calls* are a stall only when the *results* are unchanged too: "running", "running", "passed" is progress; three identical failures are not.
- **Widen the window for tools that are meant to be polled.** A per-tool window costs one dictionary lookup, at the price of a longer wait before a genuine stall on that tool is caught.
- **Exempt named idempotent tools by hand.** Blunt, explicit and easy to audit.

The snippet feeds four scripted traces to three detectors: the companion's, the folded fingerprint, and the folded fingerprint with a window of 6 for the polled `build_status` tool. It prints the turn on which each fires, and the figure after it draws the same table as rows of turns:

```text
same call, keys in two orders: sorted equal True, unsorted equal False
trace                    calls only       + observation   + polled window 6
doom loop                    turn 3              turn 3              turn 3
build poll                   turn 3               never               never
long build                   turn 3              turn 3               never
healthy edits                 never               never               never
```

![Four scripted traces as rows of turns, a doom loop, a short build poll, a long build and healthy edits, with the turn on which each of three no-progress detectors fires: calls only stops the first three; folding in the observation spares the short poll; a window of 6 for the polled tool stops only the doom loop.](diagrams/04-no-progress.svg)

*Only the doom loop should stop; every other stop in the figure is a false positive, and each refinement removes some of them.*

Whatever the choice, log the fingerprint alongside the exit reason. "no progress at iteration 7, signature `[["read_file", {"path": "src/main.py"}]]`" is a diagnosis; "no progress" alone is a mystery, and the trace-reading skill it feeds is [post 21](../21-observability-traces/index.md)'s.

---

## 10. Streaming versus batch turns

One implementation choice is worth naming early. A turn can be **batch** (call the model, wait for the complete response, then act) or **streaming** (read the response as it is generated, and start executing a tool call as soon as that call is complete, even while the model is still producing the rest of the response).

"Complete" has a precise meaning. A tool's arguments do not arrive whole: they arrive as `input_json_delta` events carrying `partial_json` fragments, and Anthropic's streaming documentation says to accumulate the fragments and parse them once the block's `content_block_stop` event arrives; a per-tool `eager_input_streaming` flag enables fine-grained streaming of parameter values (Anthropic, "Streaming messages" and "Fine-grained tool streaming", 2026). That accumulating buffer, and the question of what the loop does with a call that is half received when the stream drops, is the extra state streaming costs. The figure below draws one turn scheduled both ways.

![Batch and streaming schedules of one turn whose response holds two tool calls, on one schematic time axis: batch starts both tools after the last token; streaming starts tool A when its block completes, while call B is still generated, saving the tail after that block.](diagrams/05-batch-vs-streaming.svg)

*The model takes as long either way; streaming only moves the start of a tool forward to the end of its own block.*

The model spends the same time generating either way; a streaming harness only starts a tool when its block is complete instead of after the last token. The saving is whatever the response holds after the first complete call, such as a second parallel call. Where the tool call ends the response, streaming saves nothing, which is [post 23](../23-economics-haas/index.md)'s point that a harness cannot dispatch a tool before its complete `tool_use` block has arrived.

Two benefits genuinely belong to streaming: a human watching sees output at once, and can **interrupt the run mid-turn**, which is the primitive underneath approvals and steering ([post 15](../15-human-in-the-loop/index.md)). One benefit often attributed to streaming is not its own: *interleaved thinking*, in which the model reasons between tool results within one assistant turn, is switched on by the request's thinking configuration (adaptive thinking, or a beta header on earlier Claude 4 models), not by streaming the response (Anthropic, extended thinking documentation, consulted October 2026). Streaming changes when the harness sees the tokens, not what the model does between them.

Batch is simpler and the right default for building and understanding a loop; the companion is batch, and the loop's logic is identical either way. Start batch, and reach for streaming when latency or interruptibility, not correctness, is the bottleneck.

---

## 11. Make it run: the companion and its four exits

The [code companion](../../code/03-agent-loop/) implements sections 2 to 9 in their teaching form: `run()` in `loop.py` with all four exits and a `StopReason` for each (`completed`, `max_iters`, `budget`, `no_progress`), a `ScriptedModel` for offline runs and an `AnthropicModel` adapter for real ones, and two small tools, of which the calculator evaluates through an abstract-syntax-tree walker rather than `eval`. From inside `code/03-agent-loop/`, `uv run --extra dev pytest -q` runs its seven tests with no API key (pytest may be fetched once), and `uv run python -m agent_loop` prints one reason, act, observe, answer cycle with its transcript.

The exercise the companion is built for is to make the scripted model trigger each exit in turn and read the stop reason each time. `snippets/four_exits.py` does it with the companion's `run()` unchanged, and `uv run python posts/03-the-agent-loop/snippets/four_exits.py` from the series root prints:

```text
run                               stop_reason  iterations  tokens_used
(1) answers on turn 1               completed           1            5
(2) cap of 5, never answers         max_iters           5            5
(3) budget of 120, 50 a turn           budget           3          150
(4) same call, window of 3        no_progress           3            3
```

The third row is the overshoot section 7 described: the budget fires only after the call that crossed it. Left out of the companion on purpose are streaming, the `stop_reason` refinement of section 4 and the `is_error` flag of section 3; each is a small change to try on top of it.

---

## 12. What can go wrong?

The mistakes that building this loop produces, with the symptom of each.

- **A truncated turn shipped as the answer.** Exit (1) is "no tool call", a turn hits `max_tokens`, and the user gets a reply that stops mid-sentence, with no error anywhere.
- **One message per tool result.** The history is valid enough to run, but the model learns to stop asking for calls in parallel, and runs get slower with nothing in the trace to explain why.
- **A tool exception that escapes the loop.** The first bad argument ends the run with a stack trace instead of an observation, and the transcript goes with it.
- **A cap set inside the working range.** Ordinary long tasks end as `max_iters`, and the team investigates a model failure that is really a configuration.
- **A budget checked after the call.** Runs end over budget by up to one full turn, which in a long-context run is tens of thousands of tokens.
- **A polling agent stopped as a doom loop.** A build that was about to pass is killed on turn 3 with `no_progress`, because the fingerprint saw the call and not the result.
- **A head that changes every turn.** With a timestamp in the system prompt, cache reads vanish from the usage figures and the bill rises.

---

## Common pitfalls

1. **Running a loop with no cap.** If (1) is the only exit, a model that never finishes runs until something outside the harness kills it.
2. **Using `max_iters` as a cost control.** Turns are not tokens: the same cap of 12 covers a five-fold spread in the bill. Add a real budget, (3), and check it before the call that would breach it.
3. **Assuming the model remembers.** Only what the harness re-sends exists for it; "it forgot" means "it was not in the messages".
4. **Conflating a final answer with a correct one.** Exit (1) means the model *thinks* it is done, not that it *is*; verification is a separate step ([post 11](../11-verification-loops/index.md)).
5. **Reaching for streaming to fix correctness.** Streaming changes when a tool starts and lets a human interrupt; it changes nothing about what the loop decides.

---

## Further reading

- Yao, S. *et al.*, "ReAct: Synergizing Reasoning and Acting in Language Models" (ICLR 2023; arXiv 6 October 2022). The reason, act, observe pattern, with the HotpotQA, FEVER, ALFWorld and WebShop results of section 1.
- Anthropic Engineering, "Building effective agents" (19 December 2024). Workflow against agent, the simplest-solution default, and stopping conditions.
- Anthropic, "Stop reasons and fallback", Messages API documentation (2026). Every `stop_reason` value and what a loop should do with each, and the advice to add no text after `tool_result` blocks.
- Anthropic, "Handle tool calls" and "Parallel tool use", tool use documentation (2026). The `tool_use_id` pairing, `is_error`, and why one message per result discourages parallel calls.
- Anthropic, "Streaming messages", API documentation (2026). `input_json_delta` and `partial_json`, parsing at `content_block_stop`, and `eager_input_streaming`.
- Faros AI, guide to harness engineering (22 May 2026, updated 15 July 2026). Victory declaration and context anxiety as harness-level failure modes, attributed to Anthropic's research.
- ai-boost, awesome-harness-engineering (GitHub, 2026), the Agent Loop section. Curated loop sources: lifecycle hooks, checkpointing for resumption, stop conditions.
- `ctx-005` (`context-engineering`): prompt caching and the stable prefix, which is why re-sending a growing history is affordable at all.
- `ctx-008` (`context-engineering`): the *write* strategy, scratchpads and plan files, used here as loop state.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 04 - Why the harness beats the model: the evidence](../04-harness-beats-model/index.md):** the evidence, graded, that engineering this loop moves results more than swapping the model does.
- **[Post 05 - Agent failure modes: victory declaration, context anxiety, doom loops](../05-agent-failure-modes/index.md):** the six named ways a loop goes wrong, and the component that fixes each.
