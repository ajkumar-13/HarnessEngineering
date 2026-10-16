# 21 - Observability and trace-driven repair: seeing what the harness did

> **TL;DR.** When a run of dozens of model and tool calls goes wrong, the useful question is not whether the model is bad but which component failed, on which step, and why, and the answer lives in a **trace**: a tree of timed, nested spans with the stop reason on the root and, on every tool span, the gate that decided the call. Read by its geometry, a trace localises a failure to the component that owns it; replayed against a changed harness, it becomes a regression fixture. The post builds the span, the tree, cross-process trace context, replays, sampling and retention, and a dependency-free tracer around the loop of post 03.
>
> **Prerequisites:** [post 03](../03-the-agent-loop/index.md), the agent loop and its four exits.
> **Safe to skip?** Skip it if the reader can already make every run record why it stopped, even when it raised, tell a hook block from a sandbox refusal in a trace, carry a span context into a child process, and replay a recorded run against a harness that no longer makes the same calls.
>
> **After reading, you will be able to:**
>
> - Instrument a loop so every run emits nested spans with a stop reason on the root and the deciding gate's outcome on every tool span.
> - Read the geometry of a trace tree and localise a failure to the harness component that owns its fix.
> - Carry a span context across a process boundary with a W3C traceparent, and use a span link for work that outlives its parent.
> - Replay a recorded run against a changed harness, choose what happens at the first divergence, and grow a regression set from real failures.
> - Set sampling, retention and access for traces, and keep an agent that reads traces to proposing fixes rather than applying them.

![A waterfall of nineteen spans for one run on a time axis of about 18 simulated seconds: the root agent.run with stop.reason completed, six iterations each opening with a blue model call whose input tokens climb from 6,000 to 21,500, five orange tool spans tagged ok, blocked, refused, ok and denied, the 7.8-second run_tests span edged in red as the outlier, and a purple verify.gate that passes at the end.](diagrams/01-trace-tree.svg)

*One run as a transcript is a wall of text; as a tree of spans it is a diagnosis, with the reason it ended at the top and the layer that decided each call beside it.*

---

## 1. The question: which component failed, on which step, and why?

A bare agent loop ([post 03](../03-the-agent-loop/index.md)) returns its final answer and little else. Inside one run it may have called the model forty times, run a dozen shell commands, spawned a sub-agent and met a verification gate twice; when the output is wrong none of that is visible, and the only recourse is to re-run the task and watch.

The failure-mode taxonomy of [post 05](../05-agent-failure-modes/index.md) meets the same wall. A victory declaration, a doom loop and silent drift all look identical from outside: a run that finished and a result nobody trusts. They are distinguishable only *inside* the run, at the step where its behaviour diverged, and observability is what makes that step recoverable after the fact.

A trace moves the question from "the agent is flaky" to "the loop repeated one call twelve times and nothing stopped it". The first is a complaint; the second names a component that can be fixed and then ratcheted ([post 10](../10-continual-learning-ratchet/index.md)).

Two properties make an agent run harder to instrument than an ordinary service. The run is **long and nested**, so a fault at step 14 hides under thirteen steps that look fine. And the run is **self-reported**: without instrumentation, its only account is the transcript the agent wrote, the very artefact a victory declaration corrupts. A trace is the one record of a run the agent did not author.

`ctx-022` (`context-engineering`) covers the tracing stack for one call of a language-model application: what a span carries, the dashboard numbers, replays, cost and privacy. This post assumes it and moves the unit up a level, from one call to one autonomous **run**. Observability is component 11 of [post 02](../02-anatomy-of-a-harness/index.md)'s eleven, and the only one whose job is to make the other ten inspectable.

---

## 2. What to log: the span

The unit of a trace is the **span**: one timed operation with a name, a start and an end, a parent, a status and a bag of attributes. Spans nest, so a run forms a tree. The vocabulary predates agents: the OpenTelemetry project (OTel, the vendor-neutral tracing standard) defines it, and its generative artificial intelligence (GenAI) semantic conventions extend it to model calls, tool calls and agents. Every one of those conventions is still marked Development stability, and they now live in a repository of their own (OpenTelemetry, "Semantic conventions for generative AI systems", consulted October 2026), so the attribute names can move while the shape holds.

A harness opens a span at every level of the loop and records on each the fields that let a reader reconstruct the decision rather than merely confirm that it happened. The catalogue below is the one `snippets/trace_loop.py` emits:

| Span | Opened | Attributes that earn their place | The question it answers |
|---|---|---|---|
| `agent.run` | once per run | task, `harness.version`, total input tokens, `stop.reason` | why did this run end |
| `iteration` | once per turn of the loop | `iteration.index` | what happened at step *n* |
| `model.call` | around each provider call | `gen_ai.operation.name` of `chat`, `gen_ai.usage.input_tokens`, duration | which iteration bloated the window |
| `tool.<name>` | around each dispatch | `gen_ai.tool.name`, redacted `tool.args`, `outcome`, a *path* to large output | which layer decided, and what came back |
| `subagent.run` | in the child, around a delegated run | its own task and `stop.reason`, its parent taken from the trace context | did the child finish, and why |
| `verify.gate` | around each check | `verify.check`, and `outcome` pass or fail | did anything actually confirm the work |

The entry that trips people is the tool span's output. A 2,000-line test log belongs on disk, with the span carrying its path and size, which is the same offloading move the loop already makes on its history ([post 09](../09-context-management-loop/index.md)). A trace store that inlines every tool output becomes a second copy of the problem it was meant to diagnose.

Two rules keep the trace honest. Record inputs and outputs **at the boundary**, never a paraphrase, so the trace is evidence rather than the agent's summary of itself. And **redact at the instrumentation layer**, because a trace keeps every argument to every tool, which is where credentials leak: the snippet's `redact` turns an `sk-` key inside a `curl` command into `[redacted]` before the span is written. The two rules pull against each other, since full capture is what leaks; the section on sampling and retention resolves it with an always-on skeleton and message bodies as a separate opt-in layer.

---

## 3. The stop reason and the gate outcomes

Two attributes carry more diagnostic weight than everything else on the tree, and both are easy to omit, because nothing breaks when they are missing.

The first is **`stop.reason`** on the root span. It is the first thing to read, because it separates cases that look identical from outside: a clean finish, a budget kill, and a loop that ran out of turns while thrashing. A loop that returns a reason is a loop that can be debugged, which is why [post 19](../19-loop-engineering/index.md) treats the reason as part of the exit rather than as logging. The values are the four exits in the series' spelling ([notation guide](../../notation_guide.md)) and one more:

- `completed`: exit (1), the final answer, which a gate then confirms or not.
- `max_iters`: exit (2), the iteration cap.
- `budget`: exit (3), the token or wall-clock ceiling.
- `no_progress`: exit (4), the stall detector.
- `error`: the run raised, which is not an exit at all; only a `finally` can record it.

The second is **`outcome`** on each tool span, recording *which layer decided* rather than merely whether the call ran. Four values cover the gate stack, and each says something different about the system:

| `outcome` | Which layer decided | Where it runs | What a rise in it says |
|---|---|---|---|
| `blocked` | a deny-list hook ([post 13](../13-hooks-enforcement/index.md)) | before the tool | a written rule matched: a signal about the model |
| `denied` | an approval gate ([post 15](../15-human-in-the-loop/index.md)) | out of band | a person looked and said no: a signal about policy |
| `refused` | the sandbox ([post 14](../14-permissions-sandboxes/index.md)) | inside the tool | the model tried to leave the box: the allow-list is too narrow, or the task is wrong |
| `ok` | nothing stopped it | not applicable | the call ran |

Folding any two together loses an answer an incident will eventually need, and it is easy to do by accident. A hook runs before the tool and can tag its own decision, but a sandbox refuses inside the tool and returns an ordinary string, so unless the harness inspects what came back, a refusal is filed as `ok`. [Post 14](../14-permissions-sandboxes/index.md) records that Build #2 once had exactly this shape. The tagging in `trace_loop.py` decides in the order the layers run, and the line that matters is the last one after the tool returns:

```python
            if DENY.search(str(args.get("command", ""))):        # the hook, before the tool
                outcome, observation = "blocked", "blocked by hook: destructive command"
            elif tool.name in SENSITIVE and not approver(tool.name, args):   # the approval gate, out of band
                outcome, observation = "denied", "denied by approver"
            else:
                observation = tool.run(args)                      # the sandbox refuses inside the tool
                outcome = "refused" if observation.startswith("blocked:") else "ok"
            span["outcome"] = outcome
```

**Any gate that refuses by return value rather than by exception needs the harness to inspect what came back**, or the trace silently collapses two outcomes into one, and the collapse is invisible precisely because the run still succeeds.

The error case needs the same care. Record the exception and set the span's status on failure, then set `stop.reason` in a `finally`, so a crashed run still says why it ended. A stop reason present on every run except the crashed ones is missing from exactly the runs most worth reading. In the snippet's fifth run the provider stops answering on the second call; the exception propagates out of the `run()` of post 03's companion, and the file still holds an `agent.run` span with `stop.reason=error` and an error status on the `model.call`, the `iteration` and the root.

---

## 4. The trace tree for one run

Rendered, those spans form the waterfall at the top of the post, drawn from the snippet's first run: a root `agent.run` over six iterations, each opening with a `model.call`, a tool span under each of the first five, and a `verify.gate` that passes after the final answer. The horizontal axis is time, simulated at a stated cost per operation so that the run prints the same numbers every time. Because the axis is time, the **shape** carries information before any label is read. A healthy run has iterations of similar width, model and tool calls alternating, input tokens climbing in even steps, and a gate at the end. Failures deform that shape in recognisable ways, and the figure below draws four of the snippet's six runs on one time axis:

![Four runs from trace_loop.py as span strips on one time axis of seconds. The healthy run alternates model and tool spans and ends in a purple gate that passes. The doom loop repeats one read_file call twelve times with no gate and stops at the cap, max_iters. The ungated answer stops after two iterations with a dashed empty slot where the gate should be, completed. The growing-context run widens call by call until exit (3), budget, at 107,100 tokens.](diagrams/02-trace-shapes.svg)

*Four shapes read from geometry alone; the victory declaration is the one diagnosed from an absence.*

- **A doom loop** is a long tail of near-identical iterations with no gate. The waterfall repeats the same two spans without converging; with exit (4) switched off it runs to the cap.
- **A victory declaration** is a short run that ends `completed` with no `verify.gate` span before the exit. The absence is the tell; the failure itself surfaces only when a later check runs, which is why [post 05](../05-agent-failure-modes/index.md) reads it as a join between a `completed` stop and a failed downstream check.
- **A growing context** shows as model calls that widen turn after turn as the history grows. Running into the ceiling ends it on `budget`; quality falling as the window fills is context anxiety, which the token column shows and the answers confirm.
- **A latency outlier**, such as the 7.8-second `run_tests` span in the hero, is one bar far wider than its siblings: a timeout set too generously, or a tool that is genuinely slow. It is a cost and timeout signal rather than a failure mode, handed to [post 23](../23-economics-haas/index.md).

Four shapes rather than six is deliberate. Post 05 names the six failure modes and gives each a signature readable from an ordinary run log; this is the subset visible as **geometry**, plus one shape that is not a failure mode. One-shotting, silent drift and destructive action are read from span attributes and across runs instead, and the next section tabulates all six.

**Reading the token column.** A run re-sends its whole history every turn, so input tokens grow by construction. On the series' illustrative twelve-iteration run (post 23), `snippets/token_series.py` prints a climb from 6,000 to 40,100 input tokens, 3,100 more each call. Linear growth at a steady increment is healthy, and two deviations are diagnostic:

- **A step change between adjacent iterations.** If call 5 sends 18,400 tokens and call 6 sends 66,000, that 47,600-token jump against a 3,100 increment says one tool result went into the window whole; read the preceding tool span's output path and check the file's size. The 44,500-token excess is then re-sent on each of the seven calls from 6 to 12, which the snippet sums to 311,500 more input tokens, more than the 276,600 the whole run was planned to send.
- **A slope steeper than linear.** History that should have been compacted is being re-read, or a summary is appended without the turns it summarises being retired.

One arithmetic point underlies both, and it surprises anyone who prices a run by the largest window seen: the bill is the **sum** of the per-call input tokens, not the peak. The twelve calls sum to 276,600 tokens, 6.9 times the largest single window. The trace is where that sum comes from, which is what makes it the raw material of a cost model.

---

## 5. Reading a trace to localise a failure

The diagnostic move is always the same: find the span where the run first diverged from the wanted shape, then map that span to the component that owns it.

Take the snippet's third run. Its root says `max_iters`, twelve iterations and 276,600 input tokens, and its twelve tool spans are the same `read_file` call with the same arguments, every one `ok`. The naive reading is "the model got stuck". The trace-driven reading is sharper: the signatures were identical from the second iteration on, so a stall detector would have stopped the run at the third, and nothing did, because the run had exit (4) switched off (its window was wider than its cap). That is not a weights problem. It is a missing stop condition, a named part of component 01, the loop ([post 03](../03-the-agent-loop/index.md)), and the second run proves it: the same script with exit (4) on stops at iteration 3 on `no_progress`, at 27,300 tokens.

![Three panels. Trace: run 3's twelve identical read_file spans under a root ending max_iters at 276,600 tokens. Localise: identical signatures from iteration 2, owned by component 01, the loop, exit (4); with it on, the same script stops at iteration 3 on no_progress at 27,300 tokens. Ratchet: three teeth, a memory line, a pre-tool hook refusing a third identical call, and a reviewer check in which the replay joins the regression set, the first green and the other two purple.](diagrams/03-trace-to-ratchet.svg)

*The trace localises the failure to one component; the ratchet turns the one failure into constraints that outlive it.*

The figure follows the case through. Once localised, the failure earns the ratchet's three teeth of post 10: a memory line telling the agent to change approach when a call returns what it returned before, a pre-tool hook that refuses a third identical call, and a reviewer check, here the replay of run 3 added to the regression set and required to stop by iteration 3.

The mapping generalises into a lookup, which turns the geometry of the previous section into a procedure. Post 05 names the modes; this table says how each appears in a span and who owns the fix:

| Span evidence | Failure mode | Owning component | Fixed in |
|---|---|---|---|
| a `completed` run with no `verify.gate` span, or a later check that fails | victory declaration | verification: the gate on exit (1) | [post 11](../11-verification-loops/index.md) |
| `gen_ai.usage.input_tokens` climbing while late answers get worse | context anxiety | context management: offload, clear, compact | [post 09](../09-context-management-loop/index.md) |
| identical `(tool, args)` on consecutive tool spans | doom loop | the loop: exit (4), no progress | [post 03](../03-the-agent-loop/index.md) |
| one enormous tool span with near-empty siblings | one-shotting | orchestration's planner split and sprint contract | [post 12](../12-planner-generator-evaluator/index.md) |
| the same finding recurring across many runs' traces | silent drift | memory: the ratchet's memory line, hook and check | [post 10](../10-continual-learning-ratchet/index.md) |
| a tool span with `outcome=blocked` or `refused` | destructive action, attempted and stopped | hooks and permissions | [post 13](../13-hooks-enforcement/index.md), [post 14](../14-permissions-sandboxes/index.md) |

The last row is the one people misread. A `blocked` or `refused` span is not an incident but a gate doing its job, and a burst of them is a signal about the agent or the allow-list. The incident is `outcome=ok` on a call that should have been stopped.

---

## 6. Trace context across processes and machines

The span catalogue gives `subagent.run` a parent taken "from the trace context", which states the requirement and skips the only hard part. Inside one process nesting is free: the tracer keeps a stack, and a span opened while another is current becomes its child. Every example so far relies on that.

Orchestration breaks the assumption. An orchestrator that spawns workers as separate processes ([post 16](../16-multi-agent-orchestration/index.md)), or a leaderless swarm of agents on separate machines against one repository ([post 17](../17-parallel-agents-shared-repo/index.md)), has no shared stack to nest into. The parent must **serialise its span context into the child**, and the World Wide Web Consortium (W3C) standard for that is the `traceparent` header of Trace Context (W3C Recommendation, 23 November 2021), which "has four fields": version, trace-id, parent-id and trace-flags. OTel's Python application programming interface (API) writes and reads it with `inject` and `extract` from `opentelemetry.propagate`; `snippets/trace_context.py` does both by hand, which shows how little there is to it:

```python
def make_traceparent(trace_id, span_id, sampled=True):
    """version 00, the 32-hex trace id, the 16-hex id of the parent span, flags 01 when sampled."""
    return f"00-{trace_id}-{span_id}-{'01' if sampled else '00'}"


def parse_traceparent(header):
    """Return (trace_id, parent_id, sampled), or None for a missing or invalid header."""
    m = TRACEPARENT.match(header or "")
    if not m or m[1] == "ff" or set(m[2]) == {"0"} or set(m[3]) == {"0"}:
        return None
    return m[2], m[3], int(m[4], 16) & 1 == 1
```

The snippet launches a sub-agent as a separate Python process from iteration 3, passing the header in a `TRACEPARENT` environment variable, and prints where the child's span lands:

```text
launch                       same trace  child's parent        link
header built at spawn time          yes  iteration 3           none
no header sent                       no  none, a new root      none
header built at start-up            yes  iteration 1           none
queued: link, not parent             no  none, a new root      iteration 3
```

The second and third rows are the two failure signatures worth recognising by sight, because neither raises an error. Spans arriving as a **separate root trace** mean propagation was never wired, so one run tells two disconnected stories. A sub-agent span under the **wrong iteration** means the context was captured once and reused, because the carrier was built at start-up rather than at spawn time.

The last row is the queued case. When a child is dispatched to a work queue and may outlive the parent span, a parent-child edge is wrong, because a span cannot adopt work that begins after it ended. The child opens its own root and records an OTel **span link** back to the span that enqueued it: two trees with a stated relationship, honest about the asynchrony rather than pretending the parent waited. Without any of this, an orchestrated run never reads as one tree, and Part IV is where that matters most.

---

## 7. Replays and regression detection

`ctx-022` establishes the replay corpus for single-call traffic: capture real traces, freeze a sample, re-run them against the changed configuration, and compare. What changes for a run is that the recording is a whole **trajectory**, and the harness under test is the thing deciding what happens next.

The part that carries over is the capture. Because a trace records the exact inputs at every boundary, feeding the same task and the same recorded tool outputs back through the harness makes the **environment** deterministic. The model call in the middle of the loop stays live and is not deterministic even at temperature zero, and that is the point rather than a defect: the question is whether the new harness copes with the same situation, not whether it reproduces the same bytes.

Now the objection practitioners raise first. A replay is faithful only up to the first tool call whose signature differs from the recording; after that, every recorded output answers a question nobody asked. Since the reason to replay is that the harness changed, **divergence is the expected case, not the edge case**: a fixed stall detector diverges by stopping earlier, an added gate by injecting a failure report, a new tool immediately. `snippets/replay.py` records four calls, then replays a changed harness that makes the same two reads in the other order and adds a lint call the recording never saw:

```text
continuation                    right results  per call
in order, a list                      0 of 5  wrong result, wrong result, wrong result, wrong result, no recording
stop at the first divergence          0 of 5  diverged
by signature, stop on a miss          2 of 5  replayed, replayed, diverged
by signature, live on a miss          5 of 5  replayed, replayed, live, replayed, replayed
```

The first row is the trap: a list consumed in order hands four calls results recorded for different calls, and nothing flags it. The other three are the continuations in use, each a trade-off:

| Continuation at divergence | What it gives | What it costs | Use it when |
|---|---|---|---|
| stop, and grade how far the run got | fully reproducible, cheapest | weakest signal: a run that diverges at step 1 scores nothing | the fix should change nothing before the failure point |
| look up by signature, stop on a miss | a reordered but equivalent trajectory still replays | a normalisation rule and an index to keep | most regression sets |
| look up by signature, fall through to live tools | realistic, and the run finishes | not reproducible, and unsafe for destructive tools outside the sandbox ([post 14](../14-permissions-sandboxes/index.md)) | the tools are read-only, or jailed |

The signature lookup is small: the recording becomes a dictionary keyed on the call rather than a list consumed in order, its key built as the no-progress check of post 03's companion fingerprints a turn, from the name and arguments serialised with sorted keys ([post 05](../05-agent-failure-modes/index.md)):

```python
def replay_tool(recording, name, args, live=None):
    """Look a recorded tool result up by call signature, not by position."""
    key = json.dumps([name, args], sort_keys=True)
    if key in recording:
        return recording[key], "replayed"
    if live is None:
        return None, "diverged"          # stop here; grade the progress so far
    return live(name, args), "live"      # the sandboxed fall-through of post 14
```

Because the trajectory changes, the pass criterion cannot be a diff against the recorded transcript; it has to be the **outcome**: did the task resolve, did the gate pass. That is a trajectory and outcome eval, [post 22](../22-evaluating-harnesses/index.md)'s subject, and the reason harness evaluation could not simply inherit the prompt-eval machinery.

What this buys is a regression set nobody had to invent: every trace that exposed a real failure becomes a fixture, replayed after each change to check that no fixed failure has returned. Aggregating traces catches what no single run reveals, **drift across a harness version**: mean iterations creeping up, the gate's pass rate slipping, tokens per successful run rising. Tag every root span with the harness version, as the snippet does with `harness.version`, and that comparison is a query rather than a project.

---

## 8. Sampling, retention, and who can read a trace

Followed literally, the advice so far stores every prompt and every tool argument of every run forever. That is neither affordable nor lawful, and the resolution is the split between skeleton and bodies.

**Sampling.** An agent run costs far more to store than a web request: dozens of spans and, if every call's input is kept, the whole history again on each call, 276,600 tokens for the twelve-call run of the token column, against a handful of spans and a web address. Head-based sampling decides at the root, before anything has happened, and so discards the interesting runs at random. Tail-based sampling decides after the run finishes, which is the right default because the interesting property is known only at the end. Keep every run whose `stop.reason` is not `completed`, every run carrying a `blocked`, `denied` or `refused` span, every `completed` run whose gate failed, and a fixed fraction of clean successes for the trend lines. Never sample the **skeleton** away even when the bodies go, because the geometry needs only names, timings, token counts and outcomes.

**Retention.** The OTel blog's "Inside the LLM Call: GenAI Observability with OpenTelemetry" (14 May 2026) states the default the conventions build in: "By default, no prompt content or tool arguments are captured with GenAI telemetry, as these can contain sensitive data", with capture behind an explicit opt-in. Inherit that shape. The skeleton is small, cheap and safe to keep for a long window; the bodies are large, opt-in, and what a retention policy is actually about. In `trace_loop.py` the twelve-iteration doom loop's skeleton is 37 spans and 10,172 bytes. Its distinct message content is roughly its last window, 40,100 tokens, which at an illustrative four characters a token is about 160,400 bytes (`token_series.py`), so the bodies outweigh the skeleton about sixteen to one. The windows are therefore different questions sharing one store: keep skeletons for as long as trends are wanted, and bodies only as long as an investigation needs them.

**Access.** Production traces carry customer data and every credential the redaction missed, so the trace store inherits the agent's own permission boundary ([post 14](../14-permissions-sandboxes/index.md)): anyone who may not read the underlying transcripts may not read their traces. That applies to non-human readers too, which is one more reason the analysis agent of the next section should read skeletons and attributes rather than raw bodies.

---

## 9. Agents that read their own traces

A trace is structured data, which means an agent can read it. Addy Osmani's "Agent Harness Engineering" (19 April 2026) relays Viv Trivedy's framing of the open problems of harness engineering, one of which is "agents that analyze their own traces to identify and fix harness-level failure modes". It is a direction rather than a deployed practice, and the near-term version is narrower: an **analysis agent** reads a failing trace and proposes a harness fix for a person to approve.

The pattern is a small planner and evaluator arrangement ([post 12](../12-planner-generator-evaluator/index.md)) pointed inward at the harness, and it works only if its input and its output are constrained. Its input is a trace **plus the component list**: the eleven components of [post 02](../02-anatomy-of-a-harness/index.md) are the closed vocabulary its answer must come from, which stops it proposing "improve the prompt" for every incident. Its output is a triple:

- **The span that first diverged**, named by span id, so the claim can be checked against the trace.
- **The component that owns it**, drawn from the eleven and no others.
- **The constraint that would have prevented it**, as one or more of the ratchet's three teeth: a memory line, a hook, or a reviewer check ([post 10](../10-continual-learning-ratchet/index.md)).

That output is a proposal, not an action. A person or a stricter gate still approves the change ([post 15](../15-human-in-the-loop/index.md)), because an agent grading its own output skews positive ([post 11](../11-verification-loops/index.md)), and grading its own machine invites the same bias. The analysis agent *reads* traces and *writes* proposals; it does not rewrite the harness it runs inside.

Constraining the output also makes the value at scale concrete: group a week of failed traces by owning component and sort by count, and one missing stop condition can turn out to account for more incidents than the diffuse "the model is unreliable" a pile of unread traces suggests. Pushed to its limit this is a **self-tuning harness** that ratchets its own fixes, narrowing the person to approving changes rather than finding them; closing that loop is the frontier, and the reason a gate stays between a proposal and a live harness.

---

## 10. A minimal do-it-yourself stack

No vendor is needed to start. Langfuse is open source (MIT-licensed outside its enterprise folders), self-hostable, and receives OTel traces on an OpenTelemetry Protocol (OTLP) endpoint, with a managed cloud as well; Arize Phoenix is source-available under the Elastic License 2.0, runs locally, and is built on OTel (Langfuse and Phoenix documentation, consulted October 2026). Which of them, or a store of one's own, is an operational question rather than a feature one, and it changes nothing below: the core is a thin wrapper around the loop that opens a span per run, per iteration, per model call and per tool call.

With the OTel Python API, the wrapper has this shape. The block is not run (no snippet imports `opentelemetry`); it is the API's `trace.get_tracer`, `start_as_current_span` and `set_attribute` as the opentelemetry-python documentation gives them, consulted October 2026, with `classify` standing for the tagging of the gate-outcomes section:

```python
from opentelemetry import trace

tracer = trace.get_tracer("harness")

with tracer.start_as_current_span("agent.run") as run_span:
    run_span.set_attribute("harness.version", HARNESS_VERSION)
    stop_reason = "error"
    try:
        for i in range(1, MAX_ITERS + 1):
            with tracer.start_as_current_span("iteration") as it:
                it.set_attribute("iteration.index", i)
                with tracer.start_as_current_span("model.call") as m:
                    reply = model.call(messages)
                    m.set_attribute("gen_ai.operation.name", "chat")
                    m.set_attribute("gen_ai.usage.input_tokens", reply.input_tokens)
                messages.append(reply.as_message())   # the assistant turn, before any tool result
                if reply.is_final:
                    stop_reason = "completed"
                    break
                for call in reply.tool_calls:
                    with tracer.start_as_current_span(f"tool.{call.name}") as t:
                        t.set_attribute("gen_ai.operation.name", "execute_tool")
                        t.set_attribute("tool.args", redact(call.args))
                        observation = registry.dispatch(call.name, call.args)
                        t.set_attribute("outcome", classify(observation))
                    messages.append(tool_result(call, observation))
        else:
            stop_reason = "max_iters"
    finally:
        run_span.set_attribute("stop.reason", stop_reason)
```

Three details in it are the point. The model's reply is appended before any tool result, because the Anthropic message format the companions use (post 03) requires each tool result to answer a tool call in the preceding assistant turn. `start_as_current_span` records an exception and sets an error status by default, so the crash case needs only the `finally`. And the `for ... else` sets `max_iters` only when the turns ran out, which keeps a raised exception reporting `error`.

On the span names: any OTel backend renders any span tree. What the GenAI conventions add is that a GenAI-aware backend fills its token, cost and model panels without custom parsing, which needs the conventional operation names as well as the usage attributes: `chat`, `execute_tool` or `invoke_agent` in `gen_ai.operation.name`, and a span name built from the operation and its subject, such as `chat {gen_ai.request.model}` or `execute_tool {gen_ai.tool.name}` (OpenTelemetry, consulted October 2026). The readable names in this post are the teaching version; production spans carry both, a name a person can scan and attributes a backend can key on.

`snippets/trace_loop.py` is the same wrapper with no dependency. Because `run()` in `code/03-agent-loop/` cannot be edited, the tracing sits at its call boundary: a `TracedModel` opens the `iteration` and `model.call` spans on each call, `traced_tool` wraps each tool, and `traced_run` owns the root:

```python
def traced_run(tracer, clock, model, tools, task, *, check=None, **limits):
    """One instrumented run: the root span, the loop, the gate after a final answer, stop.reason in a finally."""
    root = tracer.start("agent.run", task=task, **{"harness.version": VERSION})
    stop, status, traced = "error", "error", TracedModel(model, tracer, clock)
    try:
        result = run(traced, tools, task, **limits)
        stop, status = result.stop_reason.value, None
        tracer.close_children(root)
        if check is not None and stop == "completed":
            what, passes = check
            with tracer.span("verify.gate", **{"verify.check": what}) as gate:
                clock.advance(1.2)
                gate["outcome"] = "pass" if passes(result.answer) else "fail"
        return result
    finally:
        root["attributes"]["stop.reason"] = stop                  # set even when the run raised
        root["attributes"]["gen_ai.usage.input_tokens"] = traced.tokens
        tracer.end(root, status)
```

Build #2 carries a smaller in-memory tracer of the same shape, `code/25-harness-plus/src/harness_plus/observe.py`, wired into its harness by [post 25](../25-build-harness-plus/index.md); two of its thirteen tests assert on the trace rather than the answer, `test_tracer_records_a_nested_span_tree` and `test_sandbox_refusal_is_visible_in_the_trace`.

---

## 11. Make it run

The plan's exercise for this post is to instrument the loop of post 03, run it to each of the four exits, and read every stop reason and gate outcome back out of the exported spans. The four snippets run offline from the series root with the standard library; `trace_loop.py` imports the companion from `code/03-agent-loop/src` unchanged:

```bash
uv run python posts/21-observability-traces/snippets/trace_loop.py
uv run python posts/21-observability-traces/snippets/trace_context.py
uv run python posts/21-observability-traces/snippets/replay.py
uv run python posts/21-observability-traces/snippets/token_series.py
```

`trace_loop.py`, the exercise, drives six scripted runs, writes every span to a JSON Lines (JavaScript Object Notation, one object per line) file as it ends, and prints only what it reads back from that file, in under a second:

```text
98 spans in 6 traces exported to spans.jsonl, 26,813 bytes; everything below is read back from the file
run                        stop.reason iterations input tokens verify.gate  tool outcomes
1 gated, healthy             completed          6       82,500        pass  ok, blocked, refused, ok, denied
2 doom loop, exit (4) on   no_progress          3       27,300        none  2 ok
3 doom loop, exit (4) off    max_iters         12      276,600        none  12 ok
4 growing context               budget          7      107,100        none  6 ok
5 provider down                  error          2        6,000        none  ok
6 ungated answer             completed          2       15,100        none  ok
```

Every exit appears, and `error` with it. Runs 2 and 4 have one tool span fewer than iterations, because the companion checks exits (3) and (4) after the model call and before the tools run. Run 6 is the victory declaration: `completed`, no gate span, and a downstream check, run afterwards, prints `fail`. Below the table the snippet prints run 1 as the indented tree the hero is drawn from; the other three snippets print the tables quoted above and the token arithmetic.

To try a variation, give run 6 the gate that run 1 has, with a check that fails: the root still says `completed`, and the `verify.gate` span now says `fail`, which is the same failure caught inside the run instead of by a later stage.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **`stop.reason` set on the return path, not in a `finally`.** The stop-reason chart shows no crashed runs at all, and the runs that crashed are the ones missing from it.
- **A sandbox refusal filed as `ok`.** The refusal count reads zero for weeks while the sandbox's own log shows it refusing calls.
- **A carrier built at start-up.** Every sub-agent span sits under iteration 1, so the tree says the delegation happened before the work that prompted it.
- **A replay consumed in order.** A harness that only reordered two reads fails regression cases it should pass, or passes on results recorded for other calls.
- **Head-based sampling.** The trace of last night's incident was dropped before the run went wrong, because the decision was made when it started.
- **Pricing a run by its largest window.** The estimate comes out about seven times below the invoice, because the bill sums every call.

---

## Common pitfalls

1. **Logging outputs but not structure.** A flat log of model replies is not a trace: without nested spans and parent ids there is no telling which iteration a tool call belonged to, and localisation is impossible.
2. **Omitting the two attributes that carry the diagnosis.** `stop.reason` on the root, set in a `finally`, and a per-gate `outcome` on every tool span, read from what the tool returned as well as from the gates before it.
3. **Recording the agent's summary instead of the boundary.** A trace that stores the model's paraphrase of what it did is authored by the component under investigation, and is evidence of nothing.
4. **Traces that never become replays.** Observability that stops at a dashboard is a cost with no compounding return; every real failure becomes a fixture, replayed by signature.
5. **Letting the analysis agent act.** An agent that reads traces proposes fixes against the closed component vocabulary, and a person or a gate approves them.

---

## Further reading

- OpenTelemetry, "Semantic conventions for generative AI systems" (consulted October 2026, now in the `semantic-conventions-genai` repository): the operation names `chat`, `execute_tool` and `invoke_agent`, the span-name rule and the `gen_ai.*` attributes, all at Development stability.
- OpenTelemetry blog, "Inside the LLM Call: GenAI Observability with OpenTelemetry" (14 May 2026): the agent, model and tool span shapes in practice, and why content capture is off by default.
- W3C, "Trace Context" (Recommendation, 23 November 2021): the `traceparent` header and its four fields.
- Langfuse documentation and Arize Phoenix documentation (consulted October 2026): two self-hostable tracing backends that ingest OTel spans.
- Addy Osmani, "Agent Harness Engineering" (19 April 2026): Trivedy's open problems, among them agents that analyse their own traces to fix harness-level failure modes.
- `ctx-022` (`context-engineering`): the tracing stack one level down, for a single call, with the dashboard numbers and the replay corpus this post assumes.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 22 - Evaluating harnesses: Terminal-Bench, SWE-bench, harness A/B](../22-evaluating-harnesses/index.md):** replays and regression sets grow into trajectory and outcome evals and the harness A/B, which supply the outcome grader a replay needs.
- **[Post 25 - Build #2: add hooks, sandbox, and sub-agents](../25-build-harness-plus/index.md):** the build that wires a tracer around hooks, a sandbox, an approval gate and a sub-agent, and tests that each gate's outcome shows in the trace.
