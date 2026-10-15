# 15 - Human-in-the-loop: approvals, interventions, async feedback

> **TL;DR.** Full autonomy is rarely the goal; the useful question is where on the autonomy spectrum each action belongs, decided per action rather than per agent. A harness gates what a checkpoint cannot undo and what other people will see first, keeps the policy that picks those calls apart from the decider that answers them, and lets a human interrupt and steer a run in flight. Approval works best asynchronous, bounded by a timeout with an explicit default, and rare, because measured human attention falls as a session's prompts accumulate.
>
> **Prerequisites:** [post 13](../13-hooks-enforcement/index.md), deterministic pre-tool hooks and the order in which a call is checked before it runs.
> **Safe to skip?** Skip it if the reader can already say which actions earn a human approval and why, test an approval gate without a human, and decide what a gate does when nobody answers.
>
> **After reading, you will be able to:**
>
> - Place each action on the autonomy spectrum by reversibility and visibility, and gate only what a checkpoint cannot undo or others see first.
> - Build an approval gate whose policy and decider are separate, test it with a stubbed decider, and return a denial as an observation.
> - Choose among the answers between yes and no, and decide what a gate does when nobody answers: wait, deny, proceed with a note, or defer.
> - Write escalation triggers from run signals, and keep a run open to interruption and steering while it is in flight.
> - Size an approval budget against measured reviewer fatigue, and keep the record that makes a rubber-stamp rate measurable.

![Four stops from less to more autonomy, each naming what the human becomes: suggest, operator; approve, approver; act and notify, supervisor; autonomous, observer. Below, one coding agent's actions placed one by one: reading logs, running tests and editing the working tree run on their own, while opening a pull request and deploying to production stop for approval.](diagrams/01-autonomy-spectrum.svg)

*The same agent belongs at different stops for different actions; the mistake is choosing one stop for all of them.*

---

## 1. The autonomy spectrum

Where on the autonomy spectrum does each action belong, and how does a human enter the loop without becoming its bottleneck? Oversight is not a switch between "manual" and "autonomous". Kief Morris frames three positions: humans **outside** the loop, who own the outcome and let the agent run the implementation; humans **in** the loop, gatekeepers who inspect what the model produces; and humans **on** the loop, who change "the harness that produced the artefact so it produces the results we want" (Morris, martinfowler.com, 4 March 2026). His argument against the middle position is throughput: "Agents can generate code faster than humans can manually inspect it", so a reviewer in front of every artefact becomes the system's slowest component. "On the loop" is what harness engineering means.

Feng, McDonald and Zhang make this operational. An agent's autonomy, they argue, is "a deliberate design decision, separate from its capability and operational environment", and their five levels are indexed by the role the user takes: operator, collaborator, consultant, approver, observer (Feng et al., "Levels of Autonomy for AI Agents", Knight First Amendment Institute, 2025). Autonomy is chosen and built, not inherited from how good the model happens to be this quarter.

Restated for a harness, four stops are enough to design against, and the figure at the top draws them:

| Stop | What the agent does | What the human becomes | What it costs |
| --- | --- | --- | --- |
| **Suggest** | Proposes an action; does not take it | The operator, doing the work | Maximum control, minimum throughput |
| **Approve** | Acts, but only after a decision on each action | The approver, in front of every artefact | The bottleneck Morris names |
| **Act and notify** | Acts on its own; only the irreversible is gated | The supervisor, watching and able to interrupt | A small number of real decisions |
| **Autonomous** | Acts; the work is reviewed afterwards | The observer, reading the result | Fastest, and unrecoverable if the run is wrong |

The insight that makes the table usable is to choose the row **per action, not per agent**. The same coding agent runs tests, edits files and reads logs at the autonomous row, because those are reversible, and drops to approve only at the deploy and the pull request. An agent pinned to one row either wastes a human's attention on safe actions or gives away oversight of dangerous ones. Approval is a policy on component 08, permissions ([post 02](../02-anatomy-of-a-harness/index.md)), whose bounds [post 14](../14-permissions-sandboxes/index.md) sets.

---

## 2. What earns a gate

`ctx-023` reached the same primitive from the security side: the model is not the permission system, and consequential actions need an out-of-band confirmation an attacker cannot forge, with "modify production" named as the case requiring a human. The question here is how to build that confirmation without spending more attention than it saves. Two properties earn a gate, and they are different axes.

**Reversibility.** If the checkpoint and rollback of [post 08](../08-state-filesystem-git/index.md) can undo an action, the agent takes it and fixes it if it is wrong. A deploy, a delete against production data, spending money or sending an external email cannot be rolled back, so a human decides.

**Visibility.** The second axis is whether other people see the action before it can be undone. Opening a pull request (PR) is technically reversible: it can be closed. It still earns a gate, because a pull request is where an agent's work enters other people's queues. Anthropic's own recipe for a human checkpoint under auto mode gates pushes and pull requests, with ask rules on `Bash(git push *)` and `Bash(gh pr create *)`, and notes their limit: a push spelled `git -C <dir> push` does not match the rule, so a pre-tool hook that reads the whole command is the firmer check (Anthropic, "Configure auto mode", Claude Code documentation, consulted October 2026). Name the axis when gating: a list that quietly mixes "cannot be undone" with "other people will see it" is a list nobody can extend correctly.

An approval gate is a small primitive: pause on a flagged action, resume on a decision. The companion of [post 25](../25-build-harness-plus/index.md), [`code/25-harness-plus/`](../../code/25-harness-plus/), carries one, and its dispatch function in `harness.py` calls it after the pre-tool hook and before the tool runs:

```python
        tool = registry.get(tu.name)
        if approval is not None and tool is not None:
            if approval.needs_approval(tu.name, tool.sensitive, tu.input):
                ok, message = approval.review(tu.name, tu.input)
                if not ok:
                    denied.append((tu.name, message))
                    span.set("outcome", "denied")
                    return message
```

A refusal returns a message the agent reads as its observation, not a dead end. And the gate cannot tell how long the decider took to answer, which is the seam the asynchronous reply and the timeout of later sections use.

### The gate runs last, not first

Approval sits at the same lifecycle point as a pre-tool hook ([post 13](../13-hooks-enforcement/index.md)), but it runs *after* every deterministic check, not instead of them; the companion already orders it so. In the Claude Agent software development kit (SDK), a tool call is evaluated in six steps: hooks, deny rules, ask rules, the permission mode, allow rules, and only then the `canUseTool` callback that asks a person (Anthropic, "Configure permissions", Claude Agent SDK documentation, consulted October 2026). A call a deny rule already refuses must never reach a person, because a request a rule could have answered is attention spent for nothing. Under the fatigue measurements of the last section, that ordering is the part that keeps the gate working.

---

## 3. The policy and the decider are different things

The gate has two halves, and they belong to different people. `needs_approval` is a **policy**: code that decides which calls are gated. The **decider** returns the verdict: a human, or something standing in for one. Keeping them separate is what makes the gate testable at all. The figure below draws the two halves, the four outcomes a gate can end in, and the record each decision should leave.

![A tool call meets the policy, which lets it run ungated or passes it to the decider: a human, a classifier or a test stub. Four outcomes follow: not gated, it runs; approved, it runs; denied, the reason returns as an observation; no answer, denied if irreversible, run with a note if reversible. Below, the record: the call, why it was gated, who decided, the verdict, how long it waited.](diagrams/03-anatomy-of-a-gate.svg)

*Two halves, four outcomes, one record. The fourth outcome is the one an asynchronous gate introduces; the record is what makes a decision auditable afterwards.*

A policy is ordinary code, so a test asserts against it: this call is gated, that one is not. A human is not testable, but the decider is a seam. In the companion's `approval.py` it is a plain callable, `Decider = Callable[[str, dict, str], bool]`, with `always_approve` and `always_deny` beside it, so a test stubs the human and exercises the whole flow with no prompt:

```python
@dataclass
class ApprovalGate:
    """Pauses a flagged call and resumes on the decider's verdict.

    ``needs_approval`` decides which calls are gated. By default a call is gated
    when its tool is marked ``sensitive`` (see :class:`~harness_plus.tools.Tool`).
    """
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

The decider answers with a bare bool, and `review` turns it into an `(approved, message)` tuple. On a denial the message carries the gate's own `reason`, `"sensitive tool call"` by default, not anything the reviewer said: a reviewer's reason for refusing has no way back to the model in this shape. Conflate policy and decider and the result is a gate nobody can test, which becomes a gate nobody trusts, which becomes a gate somebody disables.

### What counts as sensitive, and who decides

The simplest policy reads a flag on the tool. The companion puts `sensitive: bool = False` on its `Tool` dataclass, and `needs_approval` returns that flag unchanged, so a call is gated exactly when whoever registered the tool said so. Its demo registers `write_file` with `sensitive=True` and the sandboxed `bash` tool without. Gating is opt-in, and a tool added later is unguarded until somebody marks it.

It is also coarse. Deploying to staging and to production are the same tool with different arguments, and gating both trains the reviewer to approve deploys without reading which one it is: the fatigue problem, manufactured by the policy. A policy that inspects arguments gates the second and lets the first run, at the price of being logic that can have bugs, which is the argument for testing it. The rule of thumb: start at tool granularity, and move to argument granularity for exactly those tools where the coarse version fires on things nobody needs to see.

### A denial is not a run failure

When the reviewer says no, the run should not crash. In the companion a denied call returns its message as an ordinary observation, the denial is appended to `Result.denied`, and the loop keeps going, so the run ends normally on a later turn. Its test `test_approval_denies_sensitive_call` passes `ApprovalGate(decide=always_deny)`, a stubbed human, and asserts both that the denial was recorded and that the workspace is still empty: the denied call never executed. If a denial terminated the run, every "no" would cost a restart, and reviewers would learn that saying no is expensive.

---

## 4. Yes, no, and the answers in between

Shipped deciders offer more between yes and no, and the extra answers do most of the work. In the Claude Agent SDK the `canUseTool` callback returns one of two shapes, an allow carrying the input the tool will run with, or a deny carrying a message the model reads; the documentation builds five answers on them, plus a sixth, a complete change of direction, sent through streaming input (Anthropic, "Handle approvals and user input", Claude Agent SDK documentation, consulted October 2026):

| Answer | What the decider returns | Use it when | What the agent sees |
| --- | --- | --- | --- |
| **Approve** | Allow, input unchanged | The call is what it looked like | Nothing; the tool runs |
| **Approve with changes** | Allow, input amended | The intent is right, the scope is not | The result only; it is **not** told the input changed |
| **Approve and remember** | Allow, plus a persisted permission rule | This class of call should stop asking | Nothing; later matching calls skip the prompt |
| **Reject** | Deny, with a message saying why | The action should not happen | The message, as an observation |
| **Suggest an alternative** | Deny, with a message naming what is wanted | The goal is fine, the method is not | The documentation's example: `User doesn't want to delete files. They asked if you could compress them into an archive instead.` |

Two rows change the design. **Approve with changes** lets a coarse policy survive: a reviewer can narrow a deploy to staging rather than choose between approving production and blocking the run. Its hazard is stated plainly, "Claude sees the result but isn't told you changed anything", so a harness that silently rewrites arguments has a transcript that no longer describes what happened; the amendment belongs in the log.

**Approve and remember** is the missing half of the fatigue remedy. Reversibility and visibility alone can only say "gate less", a design-time decision that must be remade every time the policy proves wrong. A decider that returns a rule with its verdict lets the queue drain itself: the reviewer answering the same question for the fourth time converts it into a policy.

The companion's bare-bool decider can express only approve and reject, and reject without its message.

---

## 5. The decider does not have to be a person

The seam that lets a test pass an auto-deny function lets production pass a model, and this is now a mainstream answer to the fatigue problem.

Claude Code's auto mode uses a two-stage classifier: "a fast single-token (yes/no) filter instructed to err toward blocking", then a stage that "re-evaluates the same input with chain-of-thought reasoning to reduce false positives" (John Hughes, "How we built Claude Code auto mode", Anthropic, 25 March 2026). The article's numbers, cited from its own evaluation sets and graded controlled, show what the staging buys. Stage one alone runs at an 8.5% false-positive rate on 10,000 real internal tool calls; the full pipeline brings that to 0.4%. The trade runs the other way on misses: on 52 curated real overeager actions, stage one alone missed 6.6% and the full pipeline 17%, which the article calls "the honest number".

A 17% miss rate is defensible only against the human baseline it replaces, which the last section's study, on a different set of planted commands, found far worse: a machine decider is justified by a comparison, never by an absolute.

Keep the floor intact. A classifier is a decider, not a policy, and it belongs behind the same deterministic layers as a person. Inside the shipped classifier, `hard_deny` rules "block unconditionally. User intent and `allow` exceptions don't apply", and a `permissions.deny` rule blocks before the classifier is consulted at all (Anthropic, "Configure auto mode", consulted October 2026). Some actions nobody should approve; they belong in a deny rule, which holds even in `bypassPermissions` mode, not in anyone's judgement.

---

## 6. Interruption and steering mid-run

Approval gates catch the actions somebody anticipated. A running agent also needs to be **steerable** for the rest, because a human watching the stream can see it heading down a wrong path before it reaches any gate. The harness lets a person interrupt the loop and inject a steering message ("stop, that is the wrong module"), which becomes the next observation the agent reasons over.

Steerability is a property of how the loop reads input, and it comes in two strengths. Between turns, any loop the harness drives itself can be steered: before each model call it checks an inbox and appends what it finds as a user message, because the harness owns the message list ([post 03](../03-the-agent-loop/index.md)). Inside a turn, interruption needs streaming, the second of the two benefits post 03 found genuinely belong to it. The Claude Agent SDK draws the line in its input modes: streaming input supports "Queued messages: send multiple messages that process sequentially, with ability to interrupt", while single-message input does not support "Dynamic message queueing" or "Real-time interruption" (Anthropic, "Streaming Input", Claude Agent SDK documentation, consulted October 2026). An embedded run in single-message mode cannot be steered from above until its query returns, so a harness that ships one has decided, noticed or not, that its only intervention is a kill.

Three constraints keep a steering message honest:

- **It lands as the next observation, not a restart.** The transcript stays append-only and the agent keeps what it has learned.
- **A tool call already in flight completes or is cancelled explicitly.** A half-executed write nobody recorded is worse than either.
- **It is distinguishable in the trace from a model-generated turn** ([post 21](../21-observability-traces/index.md)), or "did the agent decide that, or did somebody tell it to?" has no answer after an incident.

---

## 7. Asynchronous feedback, and what the reviewer is shown

A human approving every action *synchronously* is the approve row with the suggest row's throughput: the agent blocks on a person for each move. The fix is to make oversight **asynchronous**. The agent streams its progress, flags an action for approval, and, where the harness allows it, continues independent work while the approval is pending; the decision arrives when the reviewer gets to it. Oversight becomes a queue a human drains on their own schedule. Notification is a separate concern; the Agent SDK's `PermissionRequest` hook exists to "send external notifications (Slack, email, push) when Claude is waiting for approval" (Anthropic, "Handle approvals and user input", consulted October 2026).

### The request is part of the attack surface

A reviewer never decides on a call; they decide on a *representation* of it, and the representation is the harness's code. [Post 14](../14-permissions-sandboxes/index.md) establishes that tool output is untrusted text re-entering the window. An approval summary assembled from model-authored text, or carrying content from a fetched page, lands that untrusted text in the last line of defence. Two cheap rules follow:

- **Render the request from the executor's actual arguments**, never from the model's description of what it is about to do, which the model can get wrong or be induced to get wrong.
- **Re-check at execution time that the arguments about to run are the arguments approved.** An asynchronous gate opens a window between decision and execution, and approve-then-mutate is the time-of-check to time-of-use bug of approval gates. The reply, too, must name the request it answers, or a late reply to one request is read as consent to the next.

Both rules instantiate the defence of `ctx-023`: a confirmation the attacker wrote is not a confirmation.

---

## 8. When nobody answers

Asynchronous approval introduces a case synchronous approval never had: the reviewer does not reply. They are asleep, or the notification went to a channel nobody watches. "Wait forever" is an answer, usually a bad one, and it is the default in at least one shipped SDK, whose documentation says "The callback can stay pending indefinitely. Execution remains paused until your callback returns" (Anthropic, "Handle approvals and user input", consulted October 2026). A run holding a lock and a budget for sixteen hours is its own kind of incident. Three decisions should be explicit rather than emergent:

- **A timeout, and a default.** For anything irreversible the default on expiry is **deny**: the action was gated because doing it wrongly cannot be undone, and no answer is not consent. Fail closed here for the same reason a safety hook fails closed ([post 13](../13-hooks-enforcement/index.md)). For a reversible action the default can be to proceed and note that nobody looked, because the checkpoint is the safety net. The SDK ships the deny-everything version as a mode: `dontAsk` "Converts any permission prompt into a denial", for "a fixed, explicit tool surface for a headless agent" (Anthropic, "Configure permissions", consulted October 2026).
- **What the run does while it waits.** Where the remaining work is independent, continue it and come back. Where it is not, checkpoint the run to disk ([post 08](../08-state-filesystem-git/index.md)) rather than hold a process open; the SDK's documented form is a `PreToolUse` hook that returns a `defer` decision instead of waiting in the callback, "so the process can exit and resume later from the persisted session" (Anthropic, "Handle approvals and user input", consulted October 2026).
- **Who gets asked next.** A request routed to one person is a single point of failure. An escalation path (this reviewer, then their team, then the on-call) stops a queue from silently becoming a dead letter.

The companion has neither an asynchronous reply nor a timeout: `review` calls the decider and waits for its bool. Both can be added from outside, because the decider is a plain callable. `snippets/async_approval.py` runs the companion's own `run()` and `ApprovalGate` unchanged and passes them this decider, which puts each request on a queue that a reviewer thread drains and waits on a reply channel of its own:

```python
def queued_decider(outbox, record, timeout=TIMEOUT):
    """A Decider for ApprovalGate: send the request out of band, then wait for its reply or the timeout."""
    ids = iter(range(1, 10_000))

    def decide(tool, args, reason):
        request = Request(next(ids), tool, dict(args), reason)
        outbox.put(request)
        started = time.monotonic()
        try:
            who, approved, answered_id = request.reply.get(timeout=timeout)
            if answered_id != request.id:          # a reply to some other request is not consent
                who, approved = "mismatched reply", False
        except queue.Empty:
            who = "timeout"
            approved = tool not in IRREVERSIBLE    # no answer: deny the irreversible, proceed otherwise
        record.append(dict(id=request.id, tool=tool, args=dict(args), reason=reason, who=who,
                           approved=approved, waited=time.monotonic() - started))
        return approved

    return decide
```

The scripted agent reads a log, writes two files and deploys twice; the reviewer, answering 0.1 seconds after a request arrives, approves the first write, refuses the production deploy and never sees the other two:

```text
reviewer answers after 0.1 s when they answer; a request waits at most 0.5 s
call                  gated  decided by  outcome
read_log build.log    no     -           ran
write_file notes.md   yes    reviewer    approved, ran
deploy production     yes    reviewer    denied
write_file draft.md   yes    timeout     no answer, reversible: ran, noted
deploy staging        yes    timeout     no answer, irreversible: denied
stop_reason: completed
Result.denied: [('deploy', 'denied by approver: sensitive tool call'), ('deploy', 'denied by approver: sensitive tool call')]
workspace: ['draft.md', 'notes.md']; deployed: []
```

All four outcomes fire, and the run still ends on exit (1), `completed`. The figure below draws the time each call spent at the gate. Two limits stay visible. The reply is asynchronous, but the loop still waits on that one call, up to the timeout, because the companion's loop has nowhere to park a call. And `Result.denied` cannot tell the reviewer's "no" from the timeout: both read `denied by approver: sensitive tool call`, which is why the snippet keeps a record of its own.

![The five calls of the scripted run on an axis of seconds spent at the gate, 0 to 0.5. Reading the log is not gated. The first write and the production deploy wait 0.1 seconds for the reviewer, who approves the write and denies the deploy. The second write and the staging deploy wait the full 0.5 seconds; at the timeout the write runs with a note and the deploy is denied.](diagrams/02-approval-gate.svg)

*Only the flagged calls wait, never past the timeout, and the default on expiry depends on whether a checkpoint can undo the call.*

The number to watch in production is **queue depth over time**. A queue that drains within minutes means the gate is well placed; one that grows means the gate fires too often or nobody owns it.

---

## 9. Escalation triggers

If the human should not approve everything, the harness decides *when* to pull one in: the policy half of the gate, widened until it sees the run as well as the call. `snippets/escalation.py` widens the companion's `needs_approval(tool_name, sensitive, args)` that way, and returns the reason a human is needed rather than `True`, because what the request should ask differs by signal (the thresholds are illustrative):

```python
def needs_approval(tool_name, sensitive, args, run_state):
    """The reason this call needs a human, or None when the run may go on alone."""
    if sensitive:
        return "sensitive tool"
    if run_state.verifier_confidence < 0.6:              # post 11: a check passed weakly
        return "low verifier confidence"
    if run_state.repeat_count(tool_name, args) >= 1:     # post 05: twice running, before exit (4)
        return "repeated call"
    if run_state.tokens_used > 0.8 * run_state.token_budget:
        return "budget threshold"
    if run_state.permission_flagged(tool_name, args):    # post 14: flagged, not forbidden
        return "out-of-policy action"
    return None
```

The repeat trigger fires on the second identical call in a row. The companion's exit (4), no progress, compares the last three tool-call signatures and ends the run at the third ([post 03](../03-the-agent-loop/index.md)), so a trigger set at three would never see a call. The snippet runs the function over six small run states, one per signal and one with nothing unusual. What the escalation asks for differs by signal, and so does what happens when nobody answers:

| Signal | How the harness detects it | What the request asks | If nobody answers |
| --- | --- | --- | --- |
| Low verifier confidence | A check passed weakly ([post 11](../11-verification-loops/index.md)) or an evaluator was unsure ([post 12](../12-planner-generator-evaluator/index.md)) | "Is this good enough to build on?" with the artefact | Proceed and flag, if reversible |
| Repeated call | The same call twice running, the start of a doom loop ([post 05](../05-agent-failure-modes/index.md)) | "Here is what it keeps trying; what instead?" | Stop the run; burning budget is the failure |
| Out-of-policy action | A permission rule ([post 14](../14-permissions-sandboxes/index.md)) flags without forbidding | The exact call, the rule it brushed, the blast radius | Deny |
| Budget threshold | Tokens or wall-clock past a ceiling set below exit (3), budget | "80% of the budget is spent and the task is not done. Continue?" | Deny and stop |

The last column is the one teams get wrong by making it uniform. Fail closed applies to the irreversible, not to everything: a low-confidence check on a reversible edit that times out to "deny" turns an overnight run into nothing. Escalating on signal, rather than on every action, keeps the human's involvement rare and therefore valuable.

---

## 10. Designing for reviewer trust and fatigue

Every approval request spends human attention, and attention is finite. That used to be a plausible argument; it is now a measurement, from Anthropic's study of its own product, graded controlled and cited as the vendor reports it (Conner Phillippi, "Auto mode is now the default in Claude Code for Pro, Max, and Team plans", Anthropic, 7 August 2026).

Anthropic "hired 1,053 paid testers through a research vendor for a coding study", and each met one dangerous command in place of a permission prompt. "The testers caught the dangerous command just 13.6% of the time (143 of 1,053), while auto mode blocked 89% of the same commands (937 of 1,053)". Head to head, the classifier blocked 800 commands that a human approved, while humans blocked only 6 that the classifier allowed. The baseline explains why: "users approve 97% of permission prompts in Claude Code" (the March engineering article gives 93%; this series cites the later figure). And the decay is the mechanism: humans "blocked about 17% of dangerous commands early in a session, dropping to about 5% after 50 or more prior prompts, while auto mode's block rate stayed flat regardless of session length". The figure below draws those cited numbers.

![Two cited panels. Left: of the same 1,053 planted dangerous commands, human testers caught 13.6 percent, 143, and the classifier 89 percent, 937. Right: the human block rate fell from about 17 percent early in a session to about 5 percent after 50 or more prior prompts, while the classifier's stayed flat.](diagrams/04-cost-of-asking.svg)

*Measured on the same commands: a person asked often enough stops catching what the prompt was there to catch.*

Read that as a cost model: **the cost of gate N is paid by gate N+1**. Every request added spends down the attention available to every request after it.

The production figure closes the argument. Anthropic had a model re-grade the sessions its safety pipeline flagged from May to June 2026: "At production-level severity (7+), 6.3% of manually approved sessions contained a harmful action the user hadn't explicitly asked for, compared to 2.4% of auto mode sessions". The human gate was the worse of the two; Anthropic's own reading is that manual review "can become habitual". The number compares a human gate with an automated one, not with no gate, and it is observational, over sessions already flagged: it licenses spending oversight better, not removing it.

### The arithmetic of a gate budget

`snippets/gate_budget.py` works an illustrative example: a run of 180 tool calls, 34 of them writes, 15 seconds of genuine reading per request, six runs in one reviewer's session:

```text
tool granularity: 34 requests per run of 180 calls, 510 s of reading per run
  6 runs: 204 requests, 3,060 s (51.0 min); past prompt 50: 154 (75%)
argument granularity: 3 requests per run of 180 calls, 45 s of reading per run
  6 runs: 18 requests, 270 s (4.5 min); past prompt 50: 0 (0%)
requests saved per run: 31
```

At tool granularity the gate fires $34 \times 6 = 204$ times in the session, $204 \times 15 = 3{,}060$ seconds, and prompts 51 to 204, three-quarters of them, arrive after the 50 prior prompts past which the study measured the lower block rate. Gate only the 3 writes outside the working tree and the session holds 18 requests, all before that point. The gate did not get weaker; it got 31 fewer chances per run to teach the reviewer that the answer is always yes.

The design goal follows: *few, well-supported* requests. Gate only what reversibility and visibility select, batch related approvals, and give the reviewer the exact diff, the reason and the blast radius. Faros AI makes the same point about review load, "Review fatigue sets in, mistakes slip through" ("Harness engineering", 22 May 2026); the permission-prompt numbers make it a design constraint.

### Keep the record of who decided what

An approval that leaves no trace cannot be audited, and the audit is half of why the gate exists. Every decision should record the call and its arguments, why it was gated, who decided, what they decided, and how long the request sat. The companion's `Result` keeps two of those five, and only for refused calls: `Result.denied` is a list of tool-and-message pairs, with no arguments, no decider and no timing (a tracer adds the arguments and a `denied` span outcome), and the snippet's run shows a reviewer's refusal and a timeout leaving identical entries. Approvals, the ones needed to count anything, are not recorded at all. A production gate writes both to the same trace store as everything else ([post 21](../21-observability-traces/index.md)); `snippets/async_approval.py` keeps all five fields in its own record.

With the full record the **rubber-stamp rate** becomes measurable rather than a suspicion. Response latency is the obvious proxy (two seconds on a diff nobody could read that fast), but it is a heuristic; the measured predictor is prompts already seen in the session, and it is as easy to log. When a bad action gets through, "was this approved, by whom, and what were they shown?" then has an answer.

### The gate stops at the loop it was passed to

One boundary to carry into Part IV. An approval gate is an argument to one `run()` call, not a property of the system, so every loop a delegation spawns needs it passed again. In the companion's demo the child agent starts with an empty tool registry and no gate, safe only because a child with no tools cannot do anything worth gating. The Agent SDK leans the other way: "A subagent runs in the parent session's permission mode" unless its own definition sets one while the parent is in `default`, `dontAsk` or `plan`, so a parent in `bypassPermissions` hands that mode down (Anthropic, "Configure permissions", consulted October 2026). One design forgets to propagate the gate, the other propagates its absence. [Post 16](../16-multi-agent-orchestration/index.md) picks up the other side, counting isolation, a sub-agent with a sandbox and a permission set of its own, among the cases where a second agent pays.

---

## 11. Make it run

The plan's exercise for this post is to run the approval primitive of `code/25-harness-plus/` on a flagged call, answer it asynchronously, and let one call time out. The three snippets run offline from the series root with the standard library; `async_approval.py` imports the companion from `code/25-harness-plus/src` unchanged:

```bash
uv run python posts/15-human-in-the-loop/snippets/async_approval.py
uv run python posts/15-human-in-the-loop/snippets/escalation.py
uv run python posts/15-human-in-the-loop/snippets/gate_budget.py
```

The first and the last print the outputs quoted above, and `escalation.py` prints the reason each of its six run states returns; the first takes about a second, because two requests wait out the 0.5 second timeout. The companion's own tests, two of them on approval, run from inside `code/25-harness-plus/` with `uv run --extra dev pytest -q`. To try a variation, set `REPLY_AFTER` above `TIMEOUT` and watch the reviewer's answers arrive too late to count; then add `"write_file"` to `IRREVERSIBLE` and watch both unanswered calls fail closed.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **Deny on timeout for everything.** The no-answer default is deny for every gated call; an overnight run whose reversible edits all timed out finishes having done nothing.
- **One reply channel for every request.** The decider waits on a shared queue; a reviewer's late "yes" to an expired request is read as the answer to the next one, and a deploy nobody approved runs.
- **A summary the model wrote.** The request shows the model's description instead of the arguments; the reviewer approves "update the staging config", and the call that runs writes to production.
- **A gate that fires on everything.** Every write asks; the reviewer soon answers each prompt in seconds, and the one dangerous request is approved like the rest.
- **A sub-agent without the gate.** The parent's run passes `approval=` and the child's does not; the child later gets a write tool, and its writes land unasked.

---

## Common pitfalls

1. **Gating everything.** Too many requests spend the attention the next request needs; the measured human block rate fell from about 17% to about 5% across a long session.
2. **Gating nothing irreversible, or nothing visible.** If the deploy, the delete or the pull request has no human on it, one bad run is unrecoverable or public before anyone looked.
3. **Synchronous approval on the hot path.** Blocking the agent on a person per action collapses throughput; make the reply asynchronous and bound the wait.
4. **No way to interrupt.** A loop that cannot take a message between turns, or an embedded run in single-message mode, can only be killed, never steered.
5. **Rejecting without a reason.** A refusal with no message is a dead end; one that names the alternative is a hint rather than a wall.
6. **A gate with no test and no record.** Separate the policy from the decider and the policy becomes testable code; record only denials and the rubber-stamp rate stays a suspicion.

---

## Further reading

- Kief Morris, "Humans and Agents in Software Engineering Loops" (martinfowler.com, 4 March 2026): humans outside, in and on the loop, and why in-the-loop review is a bottleneck.
- K. J. Kevin Feng, David W. McDonald and Amy X. Zhang, "Levels of Autonomy for AI Agents" (Knight First Amendment Institute, 2025; arXiv:2506.12469): autonomy as a design decision, and five levels indexed by the user's role.
- Conner Phillippi, "Auto mode is now the default in Claude Code for Pro, Max, and Team plans" (Anthropic, 7 August 2026): the 1,053-tester study, the within-session decay and the production severity comparison.
- John Hughes, "How we built Claude Code auto mode" (Anthropic, 25 March 2026): the two-stage classifier and its error rates.
- Anthropic, Claude Agent SDK and Claude Code documentation (consulted October 2026): the evaluation order, the approval answers, `dontAsk`, `defer`, sub-agent modes and the hard-deny tier.
- Faros AI, "Harness engineering" (22 May 2026): review fatigue as a cost of convincing generated output.
- ai-boost, awesome-harness-engineering (GitHub, 2026): the Human-in-the-Loop primitive.
- `ctx-023`: the out-of-band confirmation this post's gate implements, and why the model is never the permission system.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 16 - Multi-agent orchestration: topologies, and when not to](../16-multi-agent-orchestration/index.md):** Part IV moves from one agent under oversight to many agents coordinated, and counts a sub-agent inside its own sandbox among the cases where a second agent earns its cost.
- **[Post 25 - Build #2: add hooks, sandbox, and sub-agents](../25-build-harness-plus/index.md):** the approval gate of this post, assembled with hooks, a sandbox and a sub-agent into one runnable harness.
