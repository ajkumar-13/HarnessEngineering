# 15 · Human-in-the-loop — approvals, interventions, async feedback

> **TL;DR.** Full autonomy is rarely the goal; the useful question is *where* on the autonomy spectrum each action belongs. The harness decides which actions a human must approve (the irreversible and the publicly visible ones), how a human can interrupt a run in flight, and how feedback re-enters the loop without making the human a bottleneck. Approval is best made **asynchronous** and reserved for what a checkpoint cannot undo, because attention decays measurably with every prompt already seen, and a gate that fires on everything is read by someone who has stopped reading.
>
> **After reading this you will be able to:**
> - Place each action on the suggest → approve → act spectrum instead of choosing one autonomy level per agent.
> - Gate irreversible actions behind an approval primitive that pauses and resumes on a decision.
> - Design oversight that survives reviewer fatigue: few requests, rich context, asynchronous replies.
> - Decide what happens when no reviewer answers, and keep an auditable record of who decided what.

![Four stops along an axis from less to more autonomy: suggest, approve, act and notify, and autonomous. Each card names what the human becomes at that stop, from operator to approver to supervisor to observer, and what the stop costs. Below, a table showing that the row is chosen per action rather than per agent: reading logs, running tests and editing the working tree run autonomously because they are reversible, while opening a pull request and deploying to production need approval. Beside it, the measured cost of asking: 97% of permission prompts in Claude Code are approved, the human block rate decays from 17% to 5% after about 50 prompts, and testers caught a planted command 13.6% of the time against a classifier's 89%.](diagrams/01-autonomy-spectrum.svg)
*The same agent belongs at different stops for different actions; the mistake is picking one stop for all of them.*

---

## 1. The autonomy spectrum

Oversight is not a single switch between "manual" and "autonomous." Kief Morris frames the choice as three positions rather than two: humans **outside** the loop, who set a goal and let the agent work; humans **in** the loop, who inspect and approve each artefact; and humans **on** the loop, who build and tune the harness that guides the agent instead of reviewing its output one piece at a time (Morris, 2026). His argument against the middle position is throughput, not taste: agents generate code faster than humans can manually inspect it, so a reviewer placed in front of every artefact becomes the system's slowest component. The third position is this series' own thesis stated by someone else, and "on the loop" is what harness engineering means.

Feng, McDonald and Zhang add the move that makes this operational. An agent's autonomy, they argue, should be treated as "a deliberate design decision, separate from its capability and operational environment", and their five levels are indexed not by what the agent can do but by what the human becomes: operator, collaborator, consultant, approver, observer (Feng et al., 2025). Autonomy is chosen and built, not inherited from how good the model happens to be this quarter.

Restated for a harness, four stops are enough to design against:

| Stop | What the agent does | What the human becomes | What it costs |
| --- | --- | --- | --- |
| **Suggest** | Proposes an action; does not take it | The operator, doing the work | Maximum control, minimum throughput |
| **Approve** | Acts, but only after a decision on each action | The approver, in front of every artefact | The bottleneck Morris names |
| **Act and notify** | Acts on its own; only the irreversible is gated | The supervisor, watching and able to interrupt | A small number of real decisions |
| **Autonomous** | Acts; the work is reviewed afterwards | The observer, reading the result | Fastest, and unrecoverable if the run is wrong |

The insight that makes the table usable is to choose the row **per action, not per agent**. The same coding agent should run tests, edit files, and read logs at the *autonomous* row, because those are reversible, and drop to *approve* only at the deploy, because that is not. An agent pinned to one row either wastes a human's attention on safe actions or gives away oversight of dangerous ones.

---

## 2. What earns a gate

The sibling series reached the same primitive from the security side. Context Engineering, Post 23 §3 argues that the model is not the permission system: a tool that performs a real-world action enforces its permission in application code, and consequential actions need an out-of-band confirmation an attacker cannot forge, with *"modify production"* named as the case requiring a human. This post is about building that confirmation without spending more human attention than it saves.

Two properties earn a gate, and they are different axes.

**Reversibility.** If an action can be undone by the checkpoint-and-rollback of [Post 08](../08-state-filesystem-git/index.md), let the agent take it and fix it if it is wrong. A deploy, a delete against production data, spending money, or sending an external email cannot be undone by a rollback, so a human decides.

**Visibility.** The second axis is whether other people see the action before you can undo it. Opening a pull request is trivially reversible in the technical sense; you close it. It still earns a gate, because closing it costs nothing mechanically and something socially, and because a pull request is where an agent's work enters other people's queues. Anthropic's own recipe for keeping a checkpoint under an otherwise-automatic policy gates exactly these two: an *ask* rule on `git push` and one on `gh pr create` (Anthropic, 2026). Name the axis when you use it, because a gate list that quietly mixes "cannot be undone" with "other people will see it" is a list nobody can extend correctly.

An approval gate is a small primitive: pause on a flagged action, resume on a decision. The companion is [`code/25-harness-plus/`](../../code/25-harness-plus/), and the teaching shape is this:

```python
# A decision carries .approved (bool) and .reason (str). The companion
# collapses it to a plain (approved, message) tuple; the shape is the same.

def with_approval(needs_approval, request_approval):
    """Wrap a tool executor so flagged actions pause for a decision before running."""
    def gated(tool, args, execute):
        if needs_approval(tool, args):
            decision = request_approval(tool, args)    # may return now, or later (§7)
            if not decision.approved:
                return f"declined: {decision.reason}"  # a corrigible observation
        return execute(tool, args)
    return gated
```

Two properties matter. A rejection returns a *reason* the agent can act on, not a dead end, so "declined: deploy only from main" sends the agent to fix the branch rather than to give up. And `request_approval` need not answer immediately, which is what §7 depends on.

### The gate runs last, not first

It is tempting to describe approval as a pre-tool hook ([Post 13](../13-hooks-enforcement/index.md)) whose check happens to be a person. It sits at the same lifecycle point, but it should run *after* every deterministic check, not instead of them. In the Claude Agent software development kit (SDK), a tool call is evaluated in six steps: hooks, then deny rules, then ask rules, then the permission mode, then allow rules, and only then the human callback (Anthropic, 2026). A call a deny-list already refuses must never reach a person, because a request a rule could have answered is attention spent for nothing. That ordering is not a detail; under the argument of §10, it is the part that keeps the gate working.

---

## 3. The policy and the decider are different things

![Two halves of an approval gate, a needs_approval policy and a request_approval decider, above four outcomes (not gated, approved, denied, no answer) and a record listing the call, why it was gated, who decided, what they decided, and how long it sat.](diagrams/03-anatomy-of-a-gate.svg)
*Two halves, four outcomes, one record. The fourth outcome is the one asynchronous approval introduces and synchronous approval never had (§8); the record is what makes a decision auditable afterwards (§10).*

The gate has two halves, and they belong to different people. `needs_approval` is a **policy**: code that decides which calls are gated. `request_approval` is a **decider**: a human, or something standing in for one. Keeping them separate is not tidiness. It is what makes the gate testable at all.

A policy is ordinary code, so you can assert against it: *this call is gated, that one is not*. A human is not testable, but the decider is a seam, so a test substitutes an auto-approve or auto-deny function and exercises the whole flow with no prompt. That is exactly what the Build #2 companion does, and it is why its approval tests run offline:

```python
# code/25-harness-plus/src/harness_plus/approval.py
Decider = Callable[[str, dict, str], bool]

@dataclass
class ApprovalGate:
    decide: Decider = always_approve

    def needs_approval(self, tool_name: str, sensitive: bool, args: dict) -> bool:
        return sensitive

    def review(self, tool_name: str, args: dict,
               reason: str = "sensitive tool call") -> "tuple[bool, str]":
        approved = self.decide(tool_name, args, reason)
        if approved:
            return True, "approved"
        return False, f"denied by approver: {reason}"
```

Conflate the two and you get a gate nobody can test, which becomes a gate nobody trusts, which becomes a gate somebody disables.

### What counts as sensitive, and who decides

The simplest policy reads a flag on the tool. Build #2 puts `sensitive: bool = False` on its `Tool` dataclass in `tools.py`, and the gate's `needs_approval` returns that flag unchanged, so a call is gated exactly when whoever registered the tool said it should be. The demo registers `write_file` with `sensitive=True` and the sandboxed `bash` tool without. Note what that means: gating is opt-in, not a default, and a tool added later is unguarded until somebody marks it.

It is also coarse. Deploying to staging and deploying to production are the same tool with different arguments, and gating both trains the reviewer to approve deploys without reading which one it is: the fatigue problem of §10, manufactured by your own policy. A policy that inspects arguments gates the second and lets the first run. The cost is that the policy is now logic that can have bugs, which is the argument for testing it.

The rule of thumb: start at tool granularity, and move to argument granularity for exactly those tools where the coarse version is firing on things nobody needs to see.

### A denial is not a run failure

When the reviewer says no, the run should not crash. In the companion, a denied call returns its reason as an ordinary observation, the denial is appended to the run result, and the loop keeps going, so the run completes normally on the next turn. The agent finds out it may not do that thing and reasons about what to do instead.

```python
# code/25-harness-plus/tests/test_harness_plus.py
gate = ApprovalGate(decide=always_deny)      # the human, stubbed
res = run(model, reg, "write a file", approval=gate)
assert res.denied and res.denied[0][0] == "write_file"
assert ws.files == {}                        # the denied call never executed
```

This matters more than it sounds. If a denial terminates the run, every "no" costs a full restart, and reviewers learn that saying no is expensive. Make refusal cheap and it gets used honestly.

---

## 4. Yes, no, and the answers in between

The four outcomes of §3 are the minimum an asynchronous gate needs. Shipped deciders offer more between yes and no, and the extra ones do most of the work. In the Claude Agent SDK the approval callback returns one of two shapes, an allow carrying the input the tool will actually run with, or a deny carrying a message the model reads, and those two shapes cover five useful answers (Anthropic, 2026):

| Answer | What the decider returns | Use it when | What the agent sees |
| --- | --- | --- | --- |
| **Approve** | Allow, with the input unchanged | The call is what it looked like | Nothing; the tool runs |
| **Approve with changes** | Allow, with the arguments amended | The intent is right, the scope is not | The result only; it is **not** told the input changed |
| **Approve and remember** | Allow, plus a persisted rule | This class of call should stop asking | Nothing; later matching calls skip the gate |
| **Refuse** | Deny, with a reason | The action should not happen | The reason, as an observation to reason over |
| **Refuse and redirect** | Deny, with an alternative | The goal is fine, the method is not | *"The user does not want files deleted. They asked whether you could archive them instead."* |

Two of these rows change the design. **Approve with changes** is what lets a coarse policy survive: a reviewer looking at a deploy can narrow it to staging rather than choosing between approving production and blocking the run. It carries a hazard the documentation states plainly, so state it too: the agent is not told its input was amended, so a harness that silently rewrites arguments is a harness whose transcript no longer describes what happened. Log the amendment even though the model does not see it.

**Approve and remember** is the missing half of the prescription §10 arrives at. The only remedy the two criteria of §2 offer for a gate that fires too often is "gate less", a design-time decision somebody must make again every time the policy turns out to be wrong. A decider that returns a rule alongside its verdict lets the queue drain itself: the reviewer answering the same question for the fourth time converts it into a policy, and it stops being a question.

---

## 5. The decider does not have to be a person

The seam that lets a test pass an auto-deny function lets production pass a model. This is the same substitution, and it is now the mainstream answer to the fatigue problem rather than an exotic one.

Anthropic's implementation is a two-stage classifier: a fast single-token filter, then chain-of-thought reasoning applied only to what the first filter flags. The staging is what buys the accuracy. Stage one alone runs at an 8.5% false-positive rate on 10,000 real internal tool calls; the full pipeline brings that to 0.4%. The trade is visible in the other direction: on 52 curated real overeager actions, stage one alone missed 6.6% and the full pipeline missed 17% (Anthropic, 2026).

The honest condition is the interesting part. A 17% miss rate is not good in the abstract; it is defensible only against the human baseline it replaces, which §10 shows was worse. A machine decider is justified by a comparison, never by an absolute, and the comparison is against the reviewer you actually have on a Friday afternoon rather than the one you imagine.

Keep the floor intact. A classifier is a decider, not a policy, and it belongs behind the same deterministic layers as a person. In the shipped configuration the hard-deny tier blocks unconditionally, and neither an allow exception nor a user's explicitly stated intent clears it (Anthropic, 2026). Some actions are hard denies that no mode auto-approves, and those belong in code, not in anyone's judgement call.

---

## 6. Interruption and steering mid-run

Approval gates catch the actions you anticipated. A running agent also needs to be **steerable** for the ones you did not, because the human watching the stream can see it heading down a wrong path before it reaches any gate. The harness must let a person interrupt the loop and inject a steering message ("stop, you are editing the wrong module"), which becomes the next observation the agent reasons over.

Steerability is not a feature you bolt onto a loop. It is a property of how the loop reads input. A streaming session holds a persistent connection and supports queued messages "with ability to interrupt"; single-message input explicitly does not support "dynamic message queueing" or "real-time interruption" (Anthropic, 2026). A request/response harness cannot be steered, and no amount of harness code above it will change that, because the interruption has nowhere to land.

[Post 03](../03-the-agent-loop/index.md) §10 named mid-turn interruption as one of the two benefits that genuinely belong to streaming, and still recommended batch as the default for building and understanding a loop. That is right for correctness and it has a consequence for oversight worth spelling out: the choice of input mode is the choice of whether the agent can be steered at all. A harness that ships batch has decided, whether or not anyone noticed, that its only intervention is a kill.

Three constraints keep a steering message honest:

- **It lands as the next observation, not a restart.** The transcript stays append-only, the agent keeps everything it has learned, and the redirection is one message rather than a fresh run.
- **A tool call already in flight either completes or is cancelled explicitly.** Never leave it ambiguous. A half-executed write that nobody recorded is worse than either outcome.
- **It is distinguishable in the trace from a model-generated turn** ([Post 21](../21-observability-traces/index.md)). Otherwise the question asked after an incident, "did the agent decide that, or did somebody tell it to?", has no answer.

Steering converts "watch the agent waste ten minutes, then start over" into "redirect it in one sentence". An agent you can only stop by killing the process, never steer, is missing half of human oversight.

---

## 7. Asynchronous feedback, and what the reviewer is shown

A human approving every action *synchronously* is the approve row of §1 with the suggest row's throughput: the agent blocks on a person for each move, and the reviewer becomes the bottleneck Morris named. The fix is to make oversight **asynchronous**.

![Two lanes, agent and human reviewer, over three phases. The agent reaches a flagged action and requests approval; the request arrives out of band; the run does not block but checkpoints and exits; the human reads the diff and decides; the agent resumes, re-checks that the arguments still match what was approved, and only then executes. Side panels list the six steps a call passes before it reaches a person, and the five answers a reviewer can give rather than two. A further panel covers the case asynchronous approval introduces, when nobody answers: a timeout defaulting to deny for anything irreversible. A worked budget shows a run of 180 tool calls with 34 writes costing 8.5 minutes of reading at tool granularity, or 204 prompts across six runs, against 3 requests and about 45 seconds once the policy reads arguments.](diagrams/02-approval-gate.svg)
*Only the flagged action pauses; the reply can arrive later, so the human is not a bottleneck on everything else.*

The agent streams its progress so a human can follow along, flags an action for approval, and where possible continues other independent work while that approval is pending. The decision arrives when the reviewer gets to it, and the flagged action resumes then. Oversight becomes a queue a human drains on their own schedule, rather than an interrupt that stalls the run and the reviewer at once. The notification is a separate concern from the gate itself, and shipped harnesses expose a hook for exactly that: a permission-request event you can wire to Slack, email or a push notification while the run waits (Anthropic, 2026).

### The request is part of the attack surface

A reviewer never decides on a call. They decide on a *representation* of a call, and the representation is code you wrote. [Post 14](../14-permissions-sandboxes/index.md) §4 establishes that tool output is untrusted text re-entering the window, and that a hostile server can plant an instruction in a tool description. An approval summary assembled from model-authored text, or carrying content from a fetched page, lands that untrusted text in the one control this post calls the last line of defence.

Two rules follow, and both are cheap:

- **Render the request from the executor's actual arguments**, never from the model's description of what it is about to do. A summary the model writes is a summary the model can get wrong, or be induced to get wrong.
- **Re-check at execution time that the arguments about to run are the arguments that were approved.** An asynchronous gate opens a window between the decision and the execution, and approve-then-mutate is the time-of-check/time-of-use bug of approval gates.

Both rules instantiate the defence §2 opened with (Context Engineering, Post 23): a consequential action needs a confirmation the attacker cannot forge, and a confirmation the attacker wrote is not one.

---

## 8. When nobody answers

Asynchronous approval introduces a case synchronous approval never had: the reviewer does not reply. They are asleep, the run started on a Friday evening, the notification went to a channel nobody watches. The harness needs an answer anyway, and "wait forever" is an answer, usually a bad one. It is also the *default* answer in at least one shipped SDK, which documents that the approval callback "can stay pending indefinitely" and that execution remains paused until it returns (Anthropic, 2026). A run holding a lock and a budget for sixteen hours is its own kind of incident.

Three decisions make this tractable, and all three should be explicit rather than emergent:

- **A timeout, and a default.** Decide how long a request waits and what happens when it expires. For anything irreversible the default is **deny**: the whole reason the action was gated is that doing it wrongly cannot be undone, and no answer is not consent. Fail closed here for the same reason a safety hook fails closed ([Post 13](../13-hooks-enforcement/index.md) §6). This is worth shipping as a *mode* rather than hand-rolling per gate, which is what the SDK's don't-ask mode is: it converts any permission prompt into a denial, so a headless run has a fixed, explicit tool surface and everything else is refused (Anthropic, 2026).
- **What the run does while it waits.** Blocking the whole agent on one pending approval throws away the point of asynchrony. Where the remaining work is independent, continue it and come back. Where it is not, checkpoint the run to disk ([Post 08](../08-state-filesystem-git/index.md)) and let it resume later rather than holding a process open. The documented form of this is a pre-tool hook that returns a *defer* decision instead of waiting in the callback, so the process can exit and the run resumes later from the persisted session (Anthropic, 2026).
- **Who gets asked, and who gets asked next.** A request routed to one person is a single point of failure. An escalation path (this reviewer, then their team, then the on-call) is what stops a queue from silently becoming a dead letter.

The number to watch is **queue depth over time**. A queue that drains within minutes means the gate is well-placed. A queue that grows means either the gate fires too often, or nobody owns it, and both problems get worse the longer they are left. The approve-and-remember outcome of §4 is what lets a well-owned queue shrink on its own instead of needing a policy rewrite.

---

## 9. Escalation triggers

If the human should not approve everything, the harness needs to decide *when* to pull one in. Mechanically this is the policy half of §3 widened until it can see the run, rather than only the call:

```python
# The companion's policy sees one call: needs_approval(tool_name, sensitive, args).
# Escalation is the same function, given the run.

def needs_approval(tool_name, sensitive, args, run_state):
    if sensitive:
        return True
    if run_state.verifier_confidence < 0.6:              # Post 11
        return True
    if run_state.repeat_count(tool_name, args) >= 3:     # Post 05, the doom loop
        return True
    if run_state.tokens_used > 0.8 * run_state.token_budget:
        return True
    return run_state.permission_flagged(tool_name, args)  # Post 14
```

Each branch is a signal that the agent is out of its depth or out of policy. What the escalation should *ask for* differs by signal, and so does what happens when nobody answers:

| Signal | How the harness detects it | What the request should ask | If nobody answers |
| --- | --- | --- | --- |
| Low verifier confidence | A check passed weakly ([Post 11](../11-verification-loops/index.md)) or an evaluator was unsure ([Post 12](../12-planner-generator-evaluator/index.md)) | "Is this good enough to build on?" with the artefact attached | Proceed and flag, if the action is reversible |
| Repeated failure | The same call signature three times running: a doom loop ([Post 05](../05-agent-failure-modes/index.md)) | "Here is what it keeps trying; what should it try instead?" | Stop the run; burning budget is the failure |
| Out-of-policy action | A permission rule ([Post 14](../14-permissions-sandboxes/index.md)) flags without forbidding | The exact call, the rule it brushed, the blast radius | Deny |
| Budget threshold | Tokens or wall-clock past a ceiling ([Post 03](../03-the-agent-loop/index.md) §7, stop condition ③) | "It has spent 80% of the budget and is not done. Continue?" | Deny and stop |

The last column is the one teams get wrong by making it uniform. §8's fail-closed default applies to the irreversible, not to everything; a low-confidence check on a reversible edit that times out to "deny" turns an overnight run into nothing. Escalating on signal, rather than on every action, is what keeps the human's involvement rare and therefore valuable.

---

## 10. Designing for reviewer trust and fatigue

Every approval request spends human attention, and attention is finite. That used to be a plausible argument. It is now a measurement.

Anthropic hired 1,053 paid testers for a coding study and swapped one permission prompt part-way through each session for a clearly dangerous command. The testers caught it 13.6% of the time (143 of 1,053); an automated classifier caught 89% (937 of 1,053). Because the two sets overlap by at most 143, arithmetic alone puts at least 794 of those commands in the category "stopped only because something other than a person was looking". The baseline explains why: users approve 97% of permission prompts in Claude Code. And the decay is the mechanism behind the outcome. Human block rates ran at about 17% early in a session and fell to about 5% after fifty or more prior prompts, while the classifier's rate stayed flat regardless of session length (Anthropic, 2026).

Read that as a cost model: **the cost of gate N is paid by gate N+1**. Every request you add spends down the attention available to every request after it. A 13.6% catch rate is not a metaphor about theatre; it is theatre.

The production figure closes the argument. At the higher severity levels, 6.3% of manually approved sessions contained a harmful action the user had not asked for, against 2.4% of sessions where the classifier made the call (Anthropic, 2026). The human gate was the worse of the two, not because reviewers are careless but because there were too many prompts for care to survive. Note what the number does *not* say: it compares a human gate against an automated one, not against no gate at all. Nothing here licences removing oversight; it licences spending it better.

### The arithmetic of a gate budget

Work an example. Take a run that makes 180 tool calls, 34 of them writes. A gate at tool granularity fires 34 times. Fifteen seconds of genuine reading per request is 8.5 minutes of one reviewer's attention for one run, and six such runs in a session is 204 prompts and nearly an hour. Everything past the fiftieth prompt sits where the measured block rate is about 5% rather than about 17%, so roughly three-quarters of those requests are answered by a person whose attention the earlier requests already spent.

Now narrow the policy to argument granularity: gate only writes outside the working tree. That is 3 requests instead of 34, forty-five seconds instead of nearly an hour, all of it inside the part of the session where attention is measurably intact. The gate did not get weaker. It got 31 fewer chances to teach the reviewer that the answer is always yes.

The design goal follows: *few, well-supported* requests. Gate only what §2's two criteria select, batch related approvals, and give the reviewer what they need to decide in seconds: the exact diff, the reason, the blast radius if it goes wrong. The narrower claim about review load is independently supported, that reviewing convincing generated output is cognitively taxing and fatigue sets in (Faros AI, 2026); the permission-prompt numbers turn that into a design constraint.

### Keep the record of who decided what

An approval that leaves no trace is an approval you cannot audit, and the audit is half of why the gate exists. Every decision should record the call and its arguments, the reason it was gated, who decided, what they decided, and how long the request sat before they did.

Build #2 keeps two of those five, and only for the calls that were refused: `Result.denied` is a list of tool-and-reason pairs, with no arguments, no decider identity and no timing. That is a fair picture of most first implementations, and the gap is worth seeing rather than papering over. Denials get recorded because they are the interesting case; approvals, which are the ones you need in order to count anything, do not. A production gate writes both to the same trace store as everything else ([Post 21](../21-observability-traces/index.md)).

With the full record, the **rubber-stamp rate** becomes measurable rather than a suspicion. Response latency is the obvious proxy (an approval returned in two seconds on a request carrying a diff nobody could read that fast), but it is a heuristic; the measured predictor is prompts already seen in the session, and it is just as easy to log. Log both, and treat a session's prompt count as a fatigue budget you are spending. And when a bad action does get through, "was this approved, by whom, and what were they shown?" has an answer, which is the difference between an incident review and an argument.

### The gate stops at the loop you passed it to

One boundary to carry into Part IV. An approval gate is an argument to one `run()` call, not a property of the system, so every loop a delegation spawns needs it passed again. In the Build #2 demo the child agent starts with an empty tool registry and no gate, which is safe only because a child with no tools cannot do anything worth gating; the moment that child gets a write tool, the gate has a hole no test covers. Shipped systems lean the other way: sub-agents inherit the parent session's permission mode, and the permissive modes cannot be overridden per sub-agent, so a permissive parent hands its permissiveness down silently (Anthropic, 2026). One design forgets to propagate the gate, the other propagates the absence of one. [Post 16](../16-multi-agent-orchestration/index.md) picks up the other side of it, counting isolation, a sub-agent given a sandbox and a permission set of its own, as one of the four cases where a second agent genuinely pays.

---

## Common pitfalls

- **Gating everything.** Too many requests spend the attention the next request needs, and the measured catch rate collapses (§10).
- **Gating nothing irreversible, or nothing visible.** If the deploy, the delete or the pull request has no human on it, one bad run is either unrecoverable or public before anyone looked (§2).
- **Synchronous approval on the hot path.** Blocking the agent on a person per action collapses throughput. Make it asynchronous (§7).
- **No way to interrupt.** Steerability is decided by the input mode, so a request/response harness cannot be steered no matter what you build above it (§6).
- **Rejecting without a reason, and never redirecting.** "Declined" with no reason is a dead end; a refusal that names the alternative is a hint rather than a wall (§3, §4).
- **No timeout on a pending approval.** A callback that waits indefinitely holds a run, a budget, and often a lock. Set an expiry, deny for anything irreversible, and defer rather than block when the reviewer may outlast the process (§8).
- **A gate with no test, and no record.** Separate the policy from the decider and the policy becomes ordinary testable code; record only denials and the rubber-stamp rate stays a suspicion (§3, §10).

---

## Further reading

- Kief Morris, "Humans and Agents in Software Engineering Loops" (martinfowler.com, 2026): humans outside, in and on the loop, why in-the-loop review is a bottleneck, and score-based auto-approval.
- K. J. Kevin Feng, David W. McDonald, Amy X. Zhang, "Levels of Autonomy for AI Agents" (arXiv:2506.12469, 2025): autonomy as a deliberate design decision, and five levels indexed by the human's role.
- Anthropic, "Auto mode is now the default in Claude Code" (2026): the 1,053-tester study, the 13.6% human catch rate, the within-session decay from 17% to 5%, and the production severity comparison.
- Anthropic, "How we built Claude Code auto mode" (2026): the two-stage classifier, its false-positive and false-negative rates, and the evaluation sets behind them.
- Anthropic, Claude Agent SDK documentation on permissions, approvals and streaming input (2026): the six-step evaluation order, the five approval response shapes, don't-ask mode, deferred approvals, and what single-message input cannot do.
- Faros AI, "Harness Engineering" (2026): review fatigue as a cost of convincing generated output.
- awesome-harness-engineering (2026): the Human-in-the-Loop section.
- Context Engineering, Post 23, "Security and prompt injection": the out-of-band confirmation this post's gate is one implementation of, and why the model is never the permission system.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 16 — Multi-agent orchestration](../16-multi-agent-orchestration/index.md)**: Part IV opens by moving from one agent under oversight to many agents coordinated, and counts a sub-agent inside its own sandbox and permission set among the few cases where a second agent earns its coordination cost.
- **[Post 25 — Build #2](../25-build-harness-plus/index.md)**: the approval gate of this post, assembled with hooks, a sandbox and a sub-agent into one runnable harness.
- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: the permission gate that an approval decision opens.
- **[Post 13 — Hooks & deterministic enforcement](../13-hooks-enforcement/index.md)**: the deterministic checks that must run before any request reaches a person.
