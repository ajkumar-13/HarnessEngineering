# 21 · Observability & trace-driven repair — seeing what the harness did

> **TL;DR.** You cannot improve a harness you cannot see. A production run takes dozens of model calls and tool calls, and when one goes wrong the useful question is never "is the model bad". It is which component failed, on which step, and why. The answer lives in a **trace**: a tree of timed, nested spans covering every iteration, model call, tool call, and sub-agent. This post covers what a span must carry, how to read a trace tree's geometry, how a replay survives a diverging harness, and a minimal OpenTelemetry stack you can build yourself.
>
> **After reading this you will be able to:**
> - Instrument an agent loop so every run emits a readable trace tree with a stop reason and a per-gate outcome.
> - Read a trace to localise a failure to one harness component rather than blaming the model.
> - Turn a failing trace into a replay that survives divergence, and a ratcheted fix that cannot silently regress.

![A waterfall of nested spans for one agent run: a root agent.run span over three iterations, each with a model call and a tool call, a slow bash span flagged in iteration two, a sub-agent span in iteration three, and a passing verify gate that ends the run with the stop reason verified. Below the waterfall, a table of what each span has to carry, from the run span's stop reason to the tool span's redacted arguments and outcome, with a note that tool output belongs on disk with the span carrying its path. A panel names the two attributes that carry the most diagnostic weight: stop.reason on the root span, with its five values, and outcome on each tool span, recording which layer decided rather than whether the call ran.](diagrams/01-trace-tree.svg)
*One run as prose is a wall of text; as a tree of spans it is a diagnosis.*

The Context Engineering series covered the tracing stack for a language-model application: what a span carries, the four numbers a dashboard needs, replays, cost engineering, privacy, and the tool landscape (Context Engineering, Post 22). This post assumes that and moves the unit up a level, from one turn to one autonomous **run**: spans nest dozens deep, the faults are stop-condition bugs rather than prompt bugs, and a replay has to survive the harness diverging from its recording. Observability is the eleventh component of the anatomy ([Post 02](../02-anatomy-of-a-harness/index.md)), and the only one whose job is to make the other ten inspectable.

---

## 1. Why a harness is opaque by default

A bare agent loop ([Post 03](../03-the-agent-loop/index.md)) prints its final answer and little else. Inside a single run it may have called the model forty times, executed a dozen shell commands, spawned a sub-agent, hit a verification gate twice, and consumed 200,000 tokens. When the output is wrong, none of that is visible. You are left re-running the task and hoping to catch the failure by eye.

This is the same trap the failure-mode taxonomy warned about ([Post 05](../05-agent-failure-modes/index.md)). A victory declaration, a doom loop, and a slow drift from conventions all look identical from outside: a run that finished and a result you do not trust. They are only distinguishable *inside* the run, at the step where the behaviour diverged. Observability is what makes that step recoverable after the fact, instead of a story you reconstruct from memory.

The point of a trace is to move the question from a vague "the agent is flaky" to a precise "iteration 14's sub-agent looped without a stop condition". The first is a complaint. The second is a bug you can fix and, more importantly, ratchet ([Post 10](../10-continual-learning-ratchet/index.md)).

Two properties of an agent run make this harder than instrumenting an ordinary service. The run is **long and nested**, so a fault at step 14 hides under thirteen successful steps that look exactly like the ones you wanted. And the run is **self-reported**: absent instrumentation, the only account of it is the transcript the agent wrote, which is the artefact a victory declaration corrupts. A trace is the one record of a run the agent did not author.

---

## 2. What to log: the span

The unit of a trace is the **span**: one timed operation with a name, a start and end, a parent, and a bag of attributes. Spans nest, so the whole run forms a tree. The vocabulary predates agents: the [OpenTelemetry](https://opentelemetry.io) (OTel, the vendor-neutral tracing standard) project defines it, and its generative-AI (GenAI) semantic conventions extend it to model, tool, and agent calls, though those conventions are still at Development stability and the attribute names can still move (OpenTelemetry, 2025).

For an agent harness, open a span at every level of the loop, and record on each the fields that let you reconstruct the decision rather than merely confirm it happened.

| Span | Opened | Attributes that earn their place | The question it answers |
|---|---|---|---|
| `agent.run` | once per run | task, harness version, total tokens, wall-clock, `stop.reason` | why did this run end |
| `iteration` | once per loop turn | index, and the decision taken that turn | what did the agent choose at step *n* |
| `model.call` | around each provider call | model id, input and output token counts, latency, temperature | which iteration bloated the window |
| `tool.<name>` | around each dispatch | redacted arguments, `outcome`, exit status, latency, a *path* to the output | which layer decided, and what came back |
| `subagent.run` | around each delegated run | the child's task and its own stop reason, linked to the parent (§6) | did the child finish, and why |
| `verify.gate` | around each check | what was checked, and whether it passed | did anything actually confirm the work |

The entry that trips people is the tool span's output. A 2,000-line build log belongs on disk with the span carrying its path, the same offloading move the loop already makes on its message history ([Post 09](../09-context-management-loop/index.md)). A trace store that inlines every tool output becomes a second copy of the problem it was meant to diagnose.

Two rules keep the trace honest. Record inputs and outputs **at the boundary**, not a paraphrase, so the trace is evidence rather than the agent's summary of itself. And **redact at the instrumentation layer**, because a trace captures every argument to every tool, which is where credentials leak. The two pull against each other, since full capture is what leaks; §8 shows how the conventions resolve it, with an always-on span skeleton and message bodies as a separate opt-in layer.

---

## 3. The stop reason and the gate outcomes

Two attributes carry more diagnostic weight than everything else on the tree, and both are easy to omit because nothing breaks when you do.

The first is **`stop.reason`** on the root span. Look at it first, because it separates three cases that are indistinguishable from outside the run: a clean finish, a budget kill, and a loop that ran out of iterations while thrashing. A loop that returns a reason is a loop you can debug, which is why loop engineering treats the reason as part of the exit rather than as logging ([Post 19](../19-loop-engineering/index.md)). Use the enumeration the code companions already emit:

- `completed`: the intended exit, a final answer that passed the gate.
- `max_iters`: the hard iteration cap was reached.
- `budget`: a token or wall-clock ceiling stopped the run.
- `no_progress`: the stall detector fired.
- `error`: the run raised, and only a `finally` block can record this one.

Post 19 names the same four internal exits *done*, *over-budget*, *no-progress* and *max-iters*, and this post's own hero figure labels its successful exit `verified`, after the gate that produced it. That is three spellings of one enumeration, which is why it is worth settling once: pick a set, and make the code, the tests and the dashboard use it.

The second is **`outcome`** on each tool span, recording *which layer decided* rather than merely whether the call ran. Four values cover the gate stack, and each means something different about the system rather than about the call.

| `outcome` | Which layer decided | Where it runs | What a rise in it tells you |
|---|---|---|---|
| `blocked` | a deny-list hook ([Post 13](../13-hooks-enforcement/index.md)) | before the tool | a rule you wrote matched: a signal about the model |
| `refused` | the sandbox ([Post 14](../14-permissions-sandboxes/index.md)) | inside the tool | the model tried to leave the box: the allow-list is too narrow, or the task is wrong |
| `denied` | a human approval gate ([Post 15](../15-human-in-the-loop/index.md)) | out of band | a reviewer looked and said no: a signal about policy |
| `ok` | nothing stopped it | not applicable | the call ran |

Fold any two together and you lose the answer to a question you will eventually be asked, and that is easier to do by accident than it sounds. Build #2 in this repository tagged spans `blocked`, `denied` and `ok`, which sounds complete. But a hook runs *before* the tool and tags its own decision, while the sandbox refuses *inside* the tool and returns an ordinary string. Nothing looked at what came back, so every sandbox refusal landed in `ok`: the one gate of four you could not see fire, in the layer whose whole purpose is containment. The fix is one line.

```python
# The tool call: tag which layer decided, then let the observation flow on.
with tracer.start_as_current_span(f"tool.{tc.name}") as span:
    span.set_attribute("tool.args", redact(tc.args))
    observation = registry.dispatch(tc.name, tc.args)
    span.set_attribute(
        "outcome", "refused" if observation.startswith("blocked:") else "ok")
```

**Any gate that refuses by return value rather than by exception needs the harness to inspect what came back**, or the trace silently collapses two outcomes into one. A gate you cannot see fire is a gate you cannot trust ([Post 14](../14-permissions-sandboxes/index.md) §5), and the collapse is invisible precisely because the run still succeeds.

The error case needs the same care. Record the exception and set the span's status on failure, which most OTel context managers already do, and set `stop.reason` in a `finally` so a crashed run still says why it ended. A stop reason present on every run except the crashed ones is missing from exactly the runs you most want to read.

---

## 4. The trace tree for one run

Rendered, those spans form the waterfall in the hero diagram: a root `agent.run` over three iterations, each opening with a `model.call`, a tool span under each of the first two, a sub-agent nested under iteration three, and a final `verify.gate` that passes. The horizontal axis is time, so the *shape* carries information before you read a label. A healthy run has iterations of roughly even width, model and tool calls alternating, token counts climbing gently, and a gate at the end. Failures deform that shape in characteristic ways:

![A healthy waterfall across the top, then four deformed ones: a doom loop of identical repeating spans with no gate, context anxiety as steeply widening bars ending in a rushed short one, a victory declaration as a short run with a dashed empty slot where the gate should be, and a latency outlier as one bar far wider than its siblings.](diagrams/03-trace-shapes.svg)
*Four deformations of the healthy shape, read from geometry alone. The victory declaration is the one you diagnose from an absence.*

- **A doom loop** is a long tail of near-identical iterations with no gate and rising token counts. The waterfall shows the same two spans repeating without converging.
- **Context anxiety** shows as steeply climbing per-call token counts, then a rushed final iteration as the window nears its limit.
- **A victory declaration** is a short run with no `verify.gate` span before exit. The absence is the tell.
- **A latency outlier**, such as iteration two's flagged `bash` span in the hero, is one bar far wider than its siblings. That is where a timeout is too generous or a tool is genuinely slow.

Four shapes rather than six is deliberate. [Post 05](../05-agent-failure-modes/index.md) §2 names the six failure modes and its §6 gives each a *signature* readable from an ordinary run log; this is the smaller set visible as **geometry**, plus one shape that is not a failure mode at all. A latency outlier is a cost and timeout signal, handed to [Post 23](../23-economics-haas/index.md). One-shotting, silent drift and destructive action are read from span attributes instead, and §5 tabulates all six.

**Reading the token series.** The useful skill is knowing what a healthy climb looks like. A run re-sends its whole message history every turn, so input tokens grow monotonically by construction: this series' worked twelve-iteration run starts at about 6,000 input tokens and reaches about 40,000, an increment of roughly 3,100 a turn ([Post 23](../23-economics-haas/index.md) §1, §5). Linear growth at a stable increment is healthy. Two deviations are diagnostic, and both are visible in a column of numbers rather than in a picture:

- **A step change between adjacent iterations.** If iteration five sends 18,400 tokens and iteration six sends 66,000, that 47,600-token jump against a 3,100 baseline says one tool result went into the window whole; read the preceding `tool.*` span's output path and check the file's size. The un-offloaded read is then re-sent on every turn from six to twelve, adding roughly 315,000 input tokens, more than the run's entire planned spend ([Post 09](../09-context-management-loop/index.md)).
- **A slope steeper than linear.** History that should have been compacted is being re-read, or a summary is being appended without the turns it summarises being retired.

One arithmetic point underlies both, and it surprises anyone who prices a run by the largest window they saw: the bill is the **sum** of the per-call input tokens, not the peak. Twelve iterations climbing 6,000 to 40,000 in even steps sum to 276,600 input tokens, seven times the largest single window. The trace is where that sum comes from, which is what makes it the raw material of a cost model.

---

## 5. Reading a trace to localise a failure

The diagnostic move is always the same: find the span where the run first diverged from the shape you wanted, then map that span to the harness component that owns it.

![Three panels: a Trace whose sub-agent span is flagged for running thirty iterations with no new files; a Localise panel naming the fault as missing no-progress detection inside the sub-agent, a stop-condition bug rather than a model bug; and a Ratchet panel converting it into three constraints: a rule capping sub-agent iterations, a no-progress hook, and a replay added to the regression set. Below them, the same run described two ways: without a trace it is "the agent is flaky", a complaint that names no component and so cannot be fixed or ratcheted; with a trace it is a named sub-agent that looped without a stop condition, a bug that earns a rule, a hook and a replay.](diagrams/02-trace-to-ratchet.svg)
*Localise the failing component, then turn the one failure into constraints that outlive it.*

Consider the run in the trace-to-ratchet figure. The sub-agent span ran thirty iterations, produced no new files, and never exited on its own; the outer budget ceiling ([Post 19](../19-loop-engineering/index.md)) eventually killed it. The naive reading is "the model got stuck". The trace-driven reading is sharper: the sub-agent's loop had **no no-progress detection**, so nothing inside it could recognise the stall and stop. That is not a weights problem. It is a missing stop condition ([Post 03](../03-the-agent-loop/index.md)), a named component you can add.

The mapping generalises into a lookup, which is what turns §4's geometry into a procedure. Post 05 names the modes; this table says how each *appears in a span*, and who owns the fix.

| Span evidence | Failure mode | Owning component | Fixed in |
|---|---|---|---|
| the run exits with no `verify.gate` span at all | victory declaration | the verification gate on the loop's exit | [Post 11](../11-verification-loops/index.md) |
| `gen_ai.usage.input_tokens` climbing while late-run answers get worse | context anxiety | context management: offload, clear, compact | [Post 09](../09-context-management-loop/index.md) |
| identical `(tool, args)` on consecutive `tool.*` spans | doom loop | no-progress detection, exit ④ | [Post 03](../03-the-agent-loop/index.md) |
| one enormous tool span with near-empty siblings | one-shotting | the planner split and its sprint contract | [Post 12](../12-planner-generator-evaluator/index.md) |
| the same finding recurring across many runs' traces | silent drift | the ratchet: a rule, a hook, a check | [Post 10](../10-continual-learning-ratchet/index.md) |
| a `tool.*` span with `outcome=blocked` or `refused` | destructive action, attempted and stopped | hooks and the sandbox | [Post 13](../13-hooks-enforcement/index.md), [Post 14](../14-permissions-sandboxes/index.md) |

The last row is the one people misread. A `blocked` or `refused` span is not an incident but a gate doing its job; a burst of them is a signal about the agent or the allow-list. The incident is `outcome=ok` on a call that should have been stopped.

This is why the trace is the connective tissue of the series. Without it you tune the prompt and hope. With it you change one part of the machine and confirm, on the next trace, that the shape corrected.

---

## 6. Trace context across processes and machines

The span catalogue in §2 asks for a `subagent.run` span "linked to the parent", which states the requirement and skips the only hard part. Inside one process, nesting is free: the tracer keeps a stack, and opening a span while another is current makes it a child. Every example so far relies on that.

Orchestration breaks the assumption. An orchestrator that spawns workers as separate processes ([Post 16](../16-multi-agent-orchestration/index.md)), or a leaderless swarm whose agents run on separate machines against one repository ([Post 17](../17-parallel-agents-shared-repo/index.md)), has no shared in-process stack to nest into. The parent must **serialise its span context into the child**, and the standard for that is the W3C `traceparent` header, carrying a version, a trace id, the parent span id and trace flags in one string (W3C, 2021). OTel exposes it as a pair of calls:

```python
from opentelemetry.propagate import inject, extract

# Parent, immediately before it launches the child:
carrier = {}
inject(carrier)                       # writes a W3C traceparent into carrier
env = {**os.environ, "TRACEPARENT": carrier["traceparent"]}
subprocess.run(["python", "-m", "worker", subtask], env=env)

# Child, as the first thing it does:
parent = extract({"traceparent": os.environ["TRACEPARENT"]})
with tracer.start_as_current_span("subagent.run", context=parent) as span:
    span.set_attribute("subagent.task", subtask)
```

Two failure signatures are worth recognising by sight, because both are common and neither raises an error. Spans arriving as a **separate root trace** mean propagation was never wired, so you have two disconnected stories about one run. A sub-agent span sitting under the **wrong iteration** means the context was captured once and reused, usually because the carrier was built at start-up rather than at spawn time.

The queued case needs a different answer. When a child is dispatched to a work queue and outlives the parent span, a parent-child edge is wrong, because a span cannot adopt work that begins after it ended. Use an OTel **span link** instead: the child opens its own root span and links back to the span that enqueued it. Two trees with a stated relationship is honest about the asynchrony rather than pretending the parent waited. Without any of this, §2's promise that an orchestrated run reads as one tree is exactly the outcome you will not get, and Part IV is where it matters most.

---

## 7. Replays and regression detection

Context Engineering, Post 22 established the replay corpus for single-turn traffic: capture real traces, freeze a sample, re-run them against the changed configuration, and diff. What changes for a run is that the recording is a whole **trajectory**, and the harness under test is the thing deciding what happens next.

The part that carries over is the capture. Because a trace records the exact inputs at every boundary, feeding the same task and the same recorded tool outputs back through the harness makes the **environment** deterministic. The model call in the middle of the loop stays live and is not deterministic even at temperature zero, and that is the point rather than a defect: you are asking whether the new harness copes with the same situation, not whether it reproduces the same bytes.

Now the objection every practitioner raises first. A replay is faithful only up to the first tool call whose signature differs from the recording; after that, every recorded output answers a question nobody asked. And since the reason to replay is that the harness changed, **divergence is the expected case, not the edge case**. A fixed no-progress detector diverges by stopping earlier; an added gate diverges by injecting a failure report; a new tool diverges immediately. Three continuations are in use, and each is a trade-off:

| Continuation at divergence | What you get | What it costs | Use it when |
|---|---|---|---|
| stop, and grade how far the run got | fully reproducible, cheapest to run | weakest signal: a run that diverges at step two scores almost nothing | the fix should change nothing before the failure point |
| fall through to live tool execution | realistic, and the run finishes | not reproducible, and unsafe for destructive tools without the sandbox ([Post 14](../14-permissions-sandboxes/index.md)) | the tools are read-only, or jailed |
| key the recording by call *signature* | a reordered but equivalent trajectory still replays | a normalisation rule and an index to maintain | most regression sets; it degrades to the first option on a real miss |

The third is usually the one to build, and it is small: the recording becomes a dictionary keyed on the tool call rather than a list consumed in order, using the fingerprint the no-progress detector already computes ([Post 05](../05-agent-failure-modes/index.md) §6).

```python
def replay_tool(recording, name, args, live=None):
    """Look a recorded tool result up by call signature, not by position."""
    key = json.dumps([name, args], sort_keys=True)
    if key in recording:
        return recording[key], "replayed"
    if live is None:
        return None, "diverged"          # stop here; grade the progress so far
    return live(name, args), "live"      # sandboxed fall-through, Post 14
```

Because the trajectory changes, the pass criterion cannot be a diff against the recorded transcript. It has to be the **outcome**: did the task resolve, do the tests pass, did the gate fire. That is a trajectory and outcome eval, [Post 22](../22-evaluating-harnesses/index.md)'s subject, and the reason harness evaluation could not simply inherit the prompt-eval machinery.

What this buys is a regression set you did not have to invent. Every trace that exposed a real failure becomes a fixture; change the loop, a stop condition or a tool, replay the set, and check that no fixed failure has returned. The agent found the failing cases for you, which is the most valuable kind.

Aggregating them catches the failure no single run reveals: **drift across a harness version**. Mean iterations per run creeping up, gate-pass rate slipping, tokens per successful run rising: each is a regression a single trace cannot show, and each is visible the moment you compare this week's traces to last week's. Tag every run span with the harness version and that comparison is a query rather than a project.

---

## 8. Sampling, retention, and who can read a trace

Followed literally, the advice so far tells you to store every prompt and every tool argument of every run forever. That is neither affordable nor lawful, and the resolution is the split §2 promised.

**Sampling.** An agent run is orders of magnitude more expensive to store than a web request: forty-odd spans and a few hundred thousand tokens of message bodies, against a handful of spans and a URL. Head-based sampling decides at the root and so discards the interesting runs at random. Tail-based sampling decides after the run finishes, which is the right default because the interesting property is known only at the end. Keep every run whose `stop.reason` is not `completed`, every run carrying a `blocked`, `refused` or `denied` span, and a fixed fraction of clean successes for the trend lines. Never sample the **skeleton** away even when you drop the bodies, because §4's geometry needs only names, timings, token counts and outcomes.

**Retention.** The GenAI conventions capture no prompt or tool-call content by default, precisely because it routinely carries names, addresses and account numbers; capture is an opt-in layer on top of the ordinary telemetry (OpenTelemetry, 2026). Inherit that shape. The span skeleton is small, cheap, and safe to keep for a long window; the bodies are large, opt-in, and what a retention policy is actually about. A run's skeleton is a few kilobytes of names and numbers, while its distinct message content at roughly four characters to the token runs to a couple of hundred kilobytes. Keeping skeletons for a year and bodies for thirty days is not a compromise: it is two different questions sharing a store.

**Access.** Production traces carry customer data and every credential the redaction missed, so the trace store inherits the agent's own permission boundary ([Post 14](../14-permissions-sandboxes/index.md)): anyone who may not read the underlying transcripts may not read the traces of them. That applies to non-human readers too, which is one more reason the analysis agent of §9 should read skeletons and attributes rather than raw bodies.

---

## 9. Agents that read their own traces

The trace is structured data, which means an agent can read it. Osmani names this among the open problems of harness engineering: agents that analyse their own traces to identify and fix harness-level failure modes (Osmani, 2026). It is a direction rather than a deployed practice, and the near-term version is narrower. An **analysis agent** ingests a failing trace and proposes a harness fix for a human to approve.

The pattern is a small planner/evaluator arrangement ([Post 12](../12-planner-generator-evaluator/index.md)) pointed inward at the harness, and it works only if its input and output are constrained. Its input is a trace **plus the component list**: the eleven components of the anatomy ([Post 02](../02-anatomy-of-a-harness/index.md)) are the closed vocabulary its answer must come from, which is what stops it proposing "improve the prompt" for every incident. Its output is a triple:

- **The span that first diverged**, named by span id, so the claim is checkable against the trace.
- **The component that owns it**, drawn from the eleven and no others.
- **The constraint that would have prevented it**, in one of the ratchet's three durable forms: a memory-file rule, a hook, or a check ([Post 10](../10-continual-learning-ratchet/index.md)).

That output is a proposal, not an action. A human or a stricter gate still approves the change ([Post 15](../15-human-in-the-loop/index.md)), because an agent grading its own machine skews positive exactly as it does grading its own output ([Post 11](../11-verification-loops/index.md)). The analysis agent *reads* traces and *writes* proposals; it does not silently rewrite the harness it runs inside.

Constraining the output also makes the value at scale concrete: group a week of failed traces by owning component and sort by count. That ranking is trivial to compute and frequently surprising. It is how a team learns that a third of its incidents are one missing stop condition in one sub-agent, rather than the diffuse "the model is unreliable" a thousand unread traces would have left them with.

Pushed to its limit this is a **self-tuning harness** that reads its own traces and ratchets its own fixes ([Post 10](../10-continual-learning-ratchet/index.md)), narrowing the human to approving changes rather than finding them. Every building block is already in this series; closing them into a loop is the frontier, and the reason a gate stays between a proposal and a live harness.

---

## 10. A minimal do-it-yourself stack

You do not need a vendor to start. Langfuse and Phoenix are both self-hostable at no licence fee, Langfuse as an open-source project and Phoenix as a local install under the Elastic Licence 2.0, and both ingest OTel spans and offer paid cloud tiers (Langfuse, 2025; Arize, 2025). Which of them, which tier, or your own store is an operational question rather than a feature one, and it changes nothing below: the core is a thin OTel wrapper around the loop, opening a span per run, per iteration, per model call, and per tool call.

```python
from opentelemetry import trace

tracer = trace.get_tracer("harness")
MAX_ITERS = 20


def run(task, harness_version, model, registry):
    """One instrumented run. Budget and no-progress exits elided; see Post 19."""
    messages, stop_reason = [user(task)], None
    with tracer.start_as_current_span("agent.run") as run_span:
        run_span.set_attribute("task", task)
        run_span.set_attribute("harness.version", harness_version)
        try:
            for i in range(MAX_ITERS):
                with tracer.start_as_current_span("iteration") as it:
                    it.set_attribute("iteration.index", i)

                    with tracer.start_as_current_span("model.call") as m:
                        reply = model.call(messages)
                        m.set_attribute("gen_ai.operation.name", "chat")
                        m.set_attribute("gen_ai.usage.input_tokens", reply.in_tokens)
                        m.set_attribute("gen_ai.usage.output_tokens", reply.out_tokens)
                    messages.append(reply.as_message())   # the turn results answer

                    if not reply.tool_calls:
                        stop_reason = "completed"
                        break

                    for tc in reply.tool_calls:
                        with tracer.start_as_current_span(f"tool.{tc.name}") as t:
                            t.set_attribute("gen_ai.operation.name", "execute_tool")
                            t.set_attribute("gen_ai.tool.name", tc.name)
                            t.set_attribute("tool.args", redact(tc.args))
                            observation = registry.dispatch(tc.name, tc.args)
                            t.set_attribute("outcome", classify(observation))
                            t.set_attribute("tool.output_path", offload(observation))
                        messages.append(tool_result(tc, observation))
        except Exception:
            stop_reason = "error"
            raise
        finally:
            run_span.set_attribute("stop.reason", stop_reason or "max_iters")
    return messages, stop_reason
```

Five details in that snippet are the whole point. The model's reply is appended to `messages` before any tool result, because a tool result with no preceding assistant turn is rejected by every major message format, and omitting it is the commonest way a hand-rolled loop breaks on its second iteration. Tool arguments pass through `redact` (§2), large tool output is offloaded with only its path on the span (§2), the tool span carries an `outcome` (§3), and `stop.reason` is set in a `finally` so a run that raises still says `error` rather than nothing (§3). Five helpers stay yours to supply: `user`, `redact`, `offload`, `classify` and `tool_result`.

A word on the span names. Any OTel backend renders any span tree, because a span is a span; that is not what the GenAI conventions buy you. What they add is that a GenAI-**aware** backend fills its token, cost and model panels without custom parsing, and that needs the conventional operation names as well as the usage attributes: a `gen_ai.operation.name` of `chat`, `execute_tool` or `invoke_agent`, with the span name built from the operation plus its subject (OpenTelemetry, 2025). The readable names used in this post are the teaching version; production spans carry both, a name a human can scan and the attributes a backend can key on.

**The companion you can read.** The OTel version above is what you ship. [`code/25-harness-plus/`](../../code/25-harness-plus/) has the same shape with no dependency at all: `observe.py` is a 66-line `Span` and `Tracer` pair, where a span is a name, an attribute bag and a list of children, and the tracer is a stack plus a `render` method. It is wired into `harness.py`, and two of that suite's 13 tests assert on the trace rather than the answer: `test_tracer_records_a_nested_span_tree` checks one `agent.run`, two `iteration` spans, two `model.call` spans, one `tool.bash` span and a `stop.reason` of `completed`, and `test_sandbox_refusal_is_visible_in_the_trace` guards the collapsed-outcome bug in §3. Run `python -m pytest -q` there: the suite is offline, driven by a scripted model, and finishes in a few hundredths of a second.

Running the demo prints the artefact this post is about, for one guarded run:

```
agent.run  [task=Do the guarded task. stop.reason=completed]
  iteration  [index=1]
    model.call  [tokens=10]
    tool.bash  [args={'command': 'rm -rf /'} outcome=blocked]
  iteration  [index=2]
    model.call  [tokens=10]
    tool.bash  [args={'command': 'curl http://example.com'} outcome=refused]
  iteration  [index=3]
    model.call  [tokens=10]
    tool.delegate  [args={'subtask': 'what is 2 + 2?'} outcome=ok]
      subagent.run  [task=what is 2 + 2? stop.reason=completed]
        iteration  [index=1]
          model.call  [tokens=6]
  iteration  [index=4]
    model.call  [tokens=10]
    tool.write_file  [args={'path': 'notes.md', 'content': 'done'} outcome=ok]
  iteration  [index=5]
    model.call  [tokens=6]
```

Read it the way §4 and §5 ask. The run completed; the hook block and the sandbox refusal are distinguishable from each other and from an ordinary `ok`; the sub-agent nests under the iteration that spawned it, because parent and child share a process (§6). Everything downstream reads from spans like these: the trees, the replays, the regression set, the analysis agent. Instrument once at the loop boundary and the rest of the stack has something to stand on.

---

## Common pitfalls

- **Logging outputs but not structure.** A flat log of model replies is not a trace. Without nested spans and a parent link you cannot tell which iteration a tool call belonged to, and localisation is impossible (§2, §5).
- **Missing the two attributes that carry the diagnosis.** `stop.reason` separates a clean finish from a budget kill from a doom loop, and set outside a `finally` it vanishes on the runs you most need. A per-gate `outcome` separates a hook block from a sandbox refusal from an approval denial, and a sandbox that refuses by return value looks like a success unless the harness inspects what came back (§3).
- **Recording the agent's summary instead of the boundary.** A trace that stores the model's paraphrase of what it did is evidence of nothing, and it is authored by the component under investigation (§2).
- **In-process nesting across a process boundary.** Sub-agent spans arriving as their own root trace mean nobody propagated a `traceparent`, and the orchestrated run is several disconnected logs after all (§6).
- **Traces that never become replays.** Observability that stops at a dashboard is a cost with no compounding return. Every real failure should become a regression fixture, and every replay needs an answer for divergence (§7).
- **Storing every body forever.** Keep the skeleton long and the content briefly, sample on the tail rather than the head, and give the trace store the agent's own permission boundary (§8).
- **Letting the analysis agent act.** An agent that reads traces should propose fixes against a closed component vocabulary, not apply them to its own harness unreviewed (§9).

---

## Further reading

- OpenTelemetry, "Semantic conventions for generative AI systems" (2025): the standard operation names and `gen_ai.*` attributes, still at Development stability, so treat the names as moving and the shape as settled.
- OpenTelemetry, "Inside the LLM call: GenAI observability with OpenTelemetry" (2026): the `invoke_agent`, `chat` and `execute_tool` span shapes in practice, and why content capture is off by default.
- W3C, "Trace Context" (2021): the `traceparent` header that carries a span context across a process or machine boundary.
- Langfuse documentation (2025): open-source tracing for model and agent runs, session grouping, and dataset-backed re-runs of captured traffic.
- Arize Phoenix documentation (2025): OpenTelemetry-native tracing and evaluation for agents, installable and runnable locally.
- Osmani, A., "Agent harness engineering" (2026): agents that analyse their own traces to propose harness fixes, listed as an open problem rather than a shipped pattern.
- [Post 14 — Permissions & sandboxes](../14-permissions-sandboxes/index.md) §5: the security-side argument for why a distinguishable outcome per gate is not optional.
- Context Engineering, Post 22: the tracing stack one level down, for a single application turn, with the dashboard numbers this post assumes.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 22 — Evaluating harnesses](../22-evaluating-harnesses/index.md)**: replays and regression sets grow into trajectory evals and harness A/B tests, and supply the outcome grader §7 hands forward.
- **[Post 23 — The economics of a harness & HaaS](../23-economics-haas/index.md)**: the token sums and latency outliers a trace exposes are the raw material of a cost model.
- **[Post 20 — The SDK & framework landscape](../20-sdk-landscape/index.md)**: every SDK in Part IV ships some of this instrumentation, so the question there is what its spans already give you before you write your own.
- **[Post 10 — Continual learning & the ratchet](../10-continual-learning-ratchet/index.md)**: where a localised trace becomes a durable rule, hook, and check.
