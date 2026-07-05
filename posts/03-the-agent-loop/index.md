# 03 · The agent loop — ReAct, control loops, and stopping

> **TL;DR.** At its core, a harness is a loop: the model reasons, the harness runs the tool it asked for, feeds the result back, and calls the model again — **reason → act → observe**, repeated. The model itself is stateless; the loop is what carries the conversation forward. The hard part is not the loop body but the **stop conditions** — and most production agent bugs are stop-condition bugs, not reasoning bugs. This post builds the minimal loop, shows where it sits relative to the provider API, and lays out the four layered exits every real loop needs.
>
> **After reading this you will be able to:**
> - Write the minimal reason → act → observe loop over a provider SDK.
> - Name the four layered stop conditions and say which one is the *correct* reason to stop.
> - Explain why the model is stateless and what the loop must carry between turns.

![The agent loop: a user task enters REASON, which either calls a tool (ACT then OBSERVE, looping back) or returns a final answer; a side panel lists the four stop conditions the loop checks each turn.](diagrams/01-agent-loop.svg)
*The loop is small. The engineering is in the exits: a final answer is the goal; the other three are backstops against loops that never end.*

---

## 1. A harness is a loop

The thing that turns a text-completer into an agent is not a clever prompt — it is a **loop**. A single model call takes messages in and returns one response. An agent is what you get when you take that response, and — if it asked to use a tool — actually run the tool, hand the result back, and call the model again. Repeat until the model is done.

This is the **ReAct** pattern — *reason and act* — introduced by Yao et al. (2022): interleave the model's reasoning with actions in an environment, feeding each observation back so the next reasoning step can use it. In plain English, one turn of the loop is three moves:

- **Reason.** The model reads everything so far and decides what to do next. It either asks to call a tool, or produces a final answer.
- **Act.** If it asked for a tool, the harness executes that tool — runs the bash command, calls the API, reads the file.
- **Observe.** The harness puts the tool's result back into the conversation, so the model can react to it on the next turn.

That is the whole engine. Anthropic's "Building Effective Agents" (2024) draws the same picture and makes the key distinction: a *workflow* wires model calls together on fixed rails, whereas an *agent* lets the model drive the loop — choosing its own tools and deciding when it is finished. Everything in this series is about building the second kind well.

---

## 2. The minimal control loop

Stripped to its essentials, the loop is a dozen lines:

```python
def run(model, tools, task, *, max_iters=12):
    messages = [{"role": "user", "content": task}]
    for step in range(max_iters):
        response = model.respond(messages, tools)   # REASON
        messages.append(response.as_message())
        if response.is_final():                      # stop ①: a final answer
            return response.text
        results = [tools[c.name](c.args) for c in response.tool_calls]  # ACT
        messages.append(tool_message(results))       # OBSERVE
    return "stopped: hit max_iters"                  # stop ②: the backstop
```

Two things are worth noticing already. First, the loop body is trivial — call, check, execute, append. Second, there are *already two ways out*: the model returns a final answer (the good exit), or the `for` runs out of iterations (the backstop). A real loop adds two more exits, which §4 covers. The runnable, fuller version — with a mock model so it executes offline with no API key — lives in [`code/03-agent-loop/`](../../code/03-agent-loop/).

---

## 3. Where the loop lives: the model forgets, the loop remembers

A point that trips up newcomers: the model has **no memory between calls**. Each call to the provider API is independent — messages in, one response out, nothing retained. The illusion of a continuous conversation is manufactured entirely by the harness, which keeps the running list of messages and **re-sends the whole thing on every turn**.

![The model drawn as a stateless function on the left; on the right, the loop holds a conversation history that grows each turn, sending the full history to the model and appending the one new message it returns.](diagrams/02-stateless-model.svg)
*The provider API keeps nothing between calls. Continuity is the harness re-sending a history that grows every turn.*

This has three immediate consequences that shape the rest of the series:

- **The history only grows.** Every tool result, every reasoning step, is appended. Left unmanaged it fills the context window and the model's quality degrades — the *context rot* problem the Context Engineering series covers. Managing that growing history at runtime (compaction, offloading, resets) is [Post 09](../09-context-management-loop/index.md).
- **State that must survive belongs on disk, not just in the list.** If the process dies, the in-memory history is gone. Durable state — files, git, handoff artefacts — is [Post 08](../08-state-filesystem-git/index.md).
- **Re-sending the same prefix every turn is what makes prompt caching matter.** The stable head of the history (system prompt, tools, early turns) is identical call-to-call, which is exactly what caching is designed to exploit (Context Engineering, Post 05).

The model is a pure function. The loop is the stateful machine wrapped around it. Harness engineering is mostly the engineering of that machine.

---

## 4. Stopping is the hard part

The loop body is easy. Deciding **when to stop** is where real loops earn their keep, because an agent that runs on its own can fail in exactly two expensive directions: stop too early and ship half-done work, or never stop and burn money in circles. A production loop carries four layered stop conditions, checked every turn.

**① A final answer — the correct reason to stop.** The model returns a response with no tool call, signalling it believes the task is done. This is the exit you *want* the loop to take. (Whether the work is *actually* done — verification — is a separate concern, and the subject of [Post 11](../11-verification-loops/index.md); a model that merely *declares* victory is [Post 05](../05-agent-failure-modes/index.md)'s first failure mode.)

**② A hard maximum-iteration cap.** A blunt integer ceiling on turns. It exists so that a loop which never reaches ① still terminates. Never run a loop without one.

**③ A token or wall-clock budget.** Iterations are a poor proxy for cost; a single turn can be cheap or enormous. A budget in tokens or seconds stops the loop before it spends more than the task is worth. Budgets become a first-class design lever in [Post 19](../19-loop-engineering/index.md) and an economic one in [Post 23](../23-economics-haas/index.md).

**④ No-progress detection.** The subtlest exit. An agent can stay busy — calling tools every turn — while making no actual progress: re-running the same failing command, re-reading the same file, oscillating between two states. Detect it by watching for repeated tool calls or unchanged observations across the last *N* turns, and break. Without this, an agent can burn its entire budget in a tight, productive-looking loop.

The reason this section matters more than the loop body is empirical: teams that instrument their agents consistently find that *the loop ran too long or stopped for the wrong reason* far more often than *the model reasoned incorrectly* (Faros AI, 2026). Stop conditions are not error handling bolted on at the end — they are the primary design surface of the loop.

---

## 5. What the loop carries between turns

Because the model is stateless (§3), everything the next turn needs must be in what the harness sends. Three things ride along:

- **The message history** — system prompt, the user task, and every `assistant → tool_call` / `tool → result` pair so far. This is the backbone.
- **Tool results** — appended as observations. Large results (a 2,000-line log) should be *offloaded* to disk with only a pointer left in the history, or they crowd out everything else; that technique is [Post 09](../09-context-management-loop/index.md).
- **A scratchpad, optionally** — a running plan or notes the model writes to and re-reads, so its intent survives a long tool detour. Scratchpads and plan files are a *Write* strategy (Context Engineering, Post 08), used here as loop state.

A useful test when debugging: if the agent "forgot" something mid-run, ask whether that something was actually in the messages sent on the failing turn. Usually it was not.

---

## 6. Streaming vs batch turns

One implementation choice worth naming early. A turn can be **batch** — call the model, wait for the complete response, then act — or **streaming** — read the response as it is generated, and begin executing a tool call the moment it is fully formed, even before the model finishes speaking.

Batch is simpler and is the right default for building and understanding a loop; the code companion is batch. Streaming lowers latency and enables interleaved thinking-and-acting (relevant to reasoning models, Context Engineering Post 18), at the cost of more intricate parsing and error handling. The loop's *logic* — reason, act, observe, and the four exits — is identical either way. Start batch; reach for streaming when latency, not correctness, is the bottleneck.

---

## 7. Putting it together

The loop is the core of the harness map from [Post 02](../02-anatomy-of-a-harness/index.md): every other component either feeds this loop (tools, state, context, memory) or governs it (verification, hooks, permissions, observability). Get the loop and its exits right and the rest of the series has a spine to attach to.

The [code companion](../../code/03-agent-loop/) implements everything above — a ReAct loop with all four stop conditions and a scripted mock model — and its test suite runs offline. Read it alongside this post; it is the shortest path from "I understand the diagram" to "I can build one."

---

## Common pitfalls

- **Running a loop with no cap.** If ① is the only exit, a model that never says "done" runs forever. Always ship ② as well (§4).
- **Using `max_iters` as a cost control.** Turns are not a proxy for tokens; one turn can be huge. Add a real budget, ③ (§4).
- **Ignoring no-progress.** An agent thrashing on the same failing command looks busy and passes the iteration and budget checks until the budget is gone. Watch for repetition, ④ (§4).
- **Assuming the model remembers.** It does not; only what the harness re-sends exists. "It forgot" almost always means "it was not in the messages" (§3, §5).
- **Letting a giant tool result sit in history.** One huge observation can crowd out the task. Offload it and keep a pointer (§5; Post 09).
- **Reaching for streaming too early.** It complicates the loop without changing its logic. Get a batch loop correct first (§6).
- **Conflating "final answer" with "correct answer."** Stopping on ① means the model *thinks* it is done, not that it *is*. Verification is a separate step (Post 11).

---

## Further reading

- Yao, S. *et al.* "ReAct: Synergizing Reasoning and Acting in Language Models" (2022) — the reason → act → observe pattern.
- Anthropic Engineering, "Building Effective Agents" (December 2024) — workflow vs agent; the model-plus-loop framing.
- awesome-harness-engineering (2026) — the "Agent Loop" section: lifecycle hooks, state persistence, stopping.
- Faros AI, "Harness Engineering" (2026) — evidence that agent failures are dominated by loop and stop-condition issues.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 04 — Why the harness beats the model](../04-harness-beats-model/index.md)**: the evidence that engineering this loop matters more than swapping the model.
- **[Post 05 — Agent failure modes](../05-agent-failure-modes/index.md)**: the named ways a loop goes wrong — victory declaration, doom loops — and the exit that fixes each.
- **[Post 06 — Tools as the agent's hands](../06-tools-bash-code/index.md)**: the ACT step in depth — what the model reaches for inside the loop.
