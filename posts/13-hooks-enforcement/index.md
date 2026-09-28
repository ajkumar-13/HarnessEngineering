# 13 · Hooks & deterministic enforcement — guardrails as code

> **TL;DR.** Verification and evaluation still run through the model's cooperation. Some rules are too important for that: they must hold every time, whatever the model decides. A **hook** is deterministic code that runs at a fixed lifecycle point (at session start, before a tool, after an edit, before a commit) and enforces a rule unconditionally, turning "please don't" into *can't*. Two of those four points can block and two can only report, and only one of the blockers sits inside the agent loop. Hooks are the enforcement half of the ratchet, and the discipline is to keep them for the failures that must be structurally impossible, fast, and silent unless they fire.
>
> **After reading this you will be able to:**
> - Name the four hook lifecycle points, plus the stop gate, and say which of them can block.
> - Decide what to enforce with a deterministic hook versus what to leave to verification.
> - Write a pre-tool deny-list and a post-edit check that gate a run, fast and quiet.
> - Give a hook an escape hatch, an override log, and near-miss tests, so it survives real work.

![The loop on the left with four coloured bars marking where hooks attach, and on the right the four points with what each can do: session-start supplies but cannot block, pre-tool can block the call, post-edit reports only, and pre-commit can block the commit.](diagrams/01-hook-lifecycle.svg)
*Four fixed points, and the model does not choose whether they run. Two of them can stop something; only one of those two sits inside the loop.*

---

## 1. The limits of asking the model nicely

Everything in this Part so far has routed through the model. The verification loop ([Post 11](../11-verification-loops/index.md)) asks the model to run a check and act on it; the evaluator ([Post 12](../12-planner-generator-evaluator/index.md)) is another model call. That cooperation is fine for judgement, but some rules cannot depend on it. "Never force-push to main." "Never run a migration without a backup." "Never commit a secret." These must hold on every run, including the run where the model is confused, distracted near a full window, or steered by a hostile instruction that reached it through a tool result ([Post 07](../07-skills-mcp-runtime/index.md), section 9).

A rule that lives only in a prompt is a *request*. The model can forget it, reason around it, or be talked out of it. The failure is silent and probabilistic: the rule holds on ninety-nine runs and breaks on the hundredth, and nothing in the transcript marks which kind of run you are having.

Occupational safety has ranked controls of that shape for decades. The hierarchy of controls published by the United States National Institute for Occupational Safety and Health (NIOSH) orders five kinds from most to least effective: elimination, substitution, engineering controls, administrative controls, and personal protective equipment. Administrative controls (a written procedure, training, changing how the work is done) sit near the bottom because they, like protective equipment, "require significant and ongoing effort by workers and their supervisors" (NIOSH, 2024). A rule in a system prompt is an administrative control: it holds only while the actor keeps choosing to follow it. A hook is an engineering control, and the sandbox of [Post 14](../14-permissions-sandboxes/index.md) is closer to substitution.

So stop asking. A **hook** is deterministic code that runs at a fixed point in the run and enforces the rule in the harness, not the model. The goal is to make a class of failure structurally impossible rather than merely discouraged, which is the enforcement half of Osmani's ratchet: a failure that got through once becomes an input, and the next version of the hook is what stops it recurring (Osmani, 2026). The model can propose `rm -rf /` all it likes, and the command still never runs. Nothing about the model changed; the rule now lives somewhere the model has no access to.

---

## 2. The four lifecycle points, and which of them can stop you

Hooks fire at fixed points around the loop, and the model does not choose whether they run. Four points cover almost everything, and they are *not* equally powerful:

- **Session-start.** Once, before the loop begins. Inject the memory file ([Post 10](../10-continual-learning-ratchet/index.md)), load project config, run startup checks. It cannot block; it *supplies*.
- **Pre-tool.** Before any tool executes. The hook sees the proposed call and can **block** it: a deny-list match, a permission check, a path outside the working directory. This is the only point *inside the loop* where a hook can stop a tool call, which makes it the safety gate.
- **Post-edit.** After a file changes. Run a typecheck, the tests, a formatter. It **cannot undo the edit**, because the write already happened; it can only report, and the report is appended to the loop as an observation the model must deal with.
- **Pre-commit.** Before a commit or a pull request (PR). Require the tests green, scan for secrets, demand approval for the irreversible. This one usually is not a harness event at all: it is the ordinary git hook, one layer below the agent, which is why it still fires when the agent is not the thing committing. It is also the rung with a documented bypass (§4).

Two of the four can block, and they block different things: pre-tool refuses a tool call inside the loop, pre-commit refuses a commit one layer below it. The other two never stop anything. Session-start is how a rule arrives; post-edit is how you find out one was broken. Getting that backwards is the commonest way a hook set ends up decorative.

"Supplies" is literal. Session-start is one of the few events whose ordinary standard output is added to the context the model can act on (Anthropic, 2025–26), which is how a memory file and the day's goal arrive at all, and it takes a matcher on *how* the session started, including `compact`. That closes a real hole: compaction ([Post 09](../09-context-management-loop/index.md)) can summarise away the rules the ratchet accumulated, and a hook matched to `compact` re-injects them after the reset. The Context Engineering series previewed hooks as a workflow feature with seven attachment points (Context Engineering, Post 26); the count differs here because pairs collapse into one event with different matchers, and because session-end enforces nothing.

**The stop gate.** Real hook systems have more than four events, and one of the extras matters enough to name. Claude Code marks several as blocking, including `UserPromptSubmit`, `SubagentStop` and **Stop** (Anthropic, 2025–26). A blocking **Stop** hook is the deterministic answer to victory declaration ([Post 05](../05-agent-failure-modes/index.md) §2.1): a hook that runs the tests when the agent tries to finish and exits 2 with `tests are red: 3 failing in the parser suite` refuses the loop its stop condition ①, and the message becomes the next observation. That is the verification loop of Post 11 promoted from a request into an exit the model cannot open. It needs one safeguard, since a stop gate that never passes is an infinite loop: pair it with the iteration cap and budget of [Post 03](../03-the-agent-loop/index.md) (stop conditions ② and ③). Verification decides whether the work is done; the stop gate decides whether the model may act on that answer.

The blocking asymmetry is written into the runtime rather than chosen. `PreToolUse` can deny a call outright: the hook exits 2, or returns a `permissionDecision` of `deny`, and the tool never runs. `PostToolUse` has no such power. An exit of 2 there surfaces the hook's standard error to the model and nothing more, because the tool has already run; any *other* non-zero exit is worse than powerless, because without valid JavaScript Object Notation (JSON) on standard output it is a non-blocking error, the run carries on, and the model never sees the message. Exit 1, the conventional failure code, therefore produces a hook that reports to nobody, and the documentation warns about exactly that (Anthropic, 2025–26). "Post-edit" is not a distinct event either; it is a post-tool hook with a matcher scoped to the editing tools.

So the honest framing is: **pre-tool prevents, post-edit corrects.** A post-edit hook does not protect you from a bad edit; it guarantees you *find out* about one, immediately and without relying on the model to check. That is the fail-fast economics of [Post 11](../11-verification-loops/index.md) §5 made automatic, but it is a different kind of control, and designing as though it can reject an edit leaves you with a guardrail that does not guard. To actually prevent a bad edit, gate at pre-tool with a matcher of `Edit|Write` and check the target path before the write: outside the working tree, a generated or vendored directory, a lockfile. Post-edit then covers only what cannot be known beforehand, which is whether the resulting file still typechecks and passes its tests.

![Two tiers: a pre-tool hook matching a destructive command against a deny-list and blocking it before it reaches the shell, returning the reason to the loop as an observation; below, the five patterns the hook compiles once and the companion run, in which ls -la is allowed while rm -rf / and git push --force are blocked.](diagrams/02-blocked-command.svg)
*The check runs before execution. The command is blocked and returns an observation the model can react to; the shell is never reached.*

---

## 3. The shape of a hook: gates and reports

Because the two kinds of hook do different jobs, they have different signatures. The companion in [`code/13-hooks/`](../../code/13-hooks/) makes the split explicit:

```
pre-tool hook:  (tool: str, args: str) -> Decision          # allow, or block with a reason
post-edit hook: (path: str, content: str) -> str | None     # a problem, or nothing
```

A pre-tool hook returns a **verdict**. A post-edit hook returns a **finding**. Collapsing them into one type invites code that treats a post-edit failure as a block, which the runtime cannot honour.

![Two columns comparing a pre-tool hook and a post-edit hook by signature, what each returns, how they compose — first block wins against collect every problem — and what the model sees.](diagrams/03-gates-and-reports.svg)
*Two signatures, two composition rules. The difference in what they return is what forces the difference in how they compose.*

A production verdict has four values, not two, and the extra pair is load-bearing later. Beyond **allow** (silent) and **deny** (a refusal carrying a reason the model can act on), a pre-tool hook can **escalate**, handing the call to a human permission prompt, which is where the approval gate of §4 lives; and it can **rewrite**, returning a corrected tool input in place of the one proposed, which is how an auto-format becomes a gate rather than a report (Anthropic, 2025–26). The companion keeps the two-verdict form because the composition rule is easier to see without them.

The composition rules differ because the return types differ. Pre-tool hooks are evaluated in order and **the first block wins**: there is no point asking the remaining hooks whether a command already ruled out is also acceptable to them, and stopping early keeps the hot path cheap.

```python
def check_tool(self, tool: str, args: str) -> Decision:
    """Run every pre-tool hook; the first block wins (fail-closed on a match)."""
    for hook in self.pre_tool:
        decision = hook(tool, args)
        if not decision.allow:
            return decision
    return ALLOW
```

Post-edit hooks run to completion and **collect every problem**, because the model is about to spend a turn responding and should see all of what broke. Reporting the typecheck error and hiding three test failures behind it buys a round trip that finds them anyway.

**What a hook is on disk.** Those signatures are the real contract with the JSON stripped off. In a host, a hook is a configuration entry naming an event, a matcher and a command; the command is handed a JSON object on standard input and answers with an exit code, or with JSON on standard output.

```json
{ "hooks": { "PreToolUse": [ { "matcher": "Bash",
    "hooks": [ { "type": "command", "command": ".claude/hooks/deny.sh", "timeout": 5 } ] } ] } }
```

```bash
#!/usr/bin/env bash
# stdin carries session_id, cwd, hook_event_name, tool_name and tool_input.
command=$(jq -r '.tool_input.command')            # parse it; never interpolate it
case "$command" in
  *"rm -rf /"*|*"git push --force"*)
    echo "blocked by policy: destructive command" >&2
    exit 2 ;;                                     # 2 blocks. 1 would not.
esac
exit 0                                            # silent on success
```

Three details repay attention. The exit code is 2 rather than 1. The tool input is *parsed* rather than interpolated, because it is model-chosen text and the model may be repeating an instruction that arrived through a tool result ([Post 07](../07-skills-mcp-runtime/index.md), section 9): a hook that splices it into a shell string is a command-injection sink inside your own trust boundary ([Post 14](../14-permissions-sandboxes/index.md) §1). And the timeout is set explicitly, because the default for a command hook is 600 seconds (Anthropic, 2025–26), which is not a budget so much as the absence of one.

The last piece is what the model sees. A blocked call does not raise, and it does not return nothing; it returns its reason, in the channel a successful call would have used:

```python
def gated_call(registry, tool, args, execute):
    """Run pre-tool hooks, then execute only if allowed. A blocked call never runs."""
    decision = registry.check_tool(tool, args)
    if not decision.allow:
        return decision.reason      # deterministic observation; execute is never called
    return execute(tool, args)
```

So the reason string is part of the design. `"blocked: force-push"` tells the model what rule it hit and lets it choose another route. `"error"` tells it nothing, and a model that cannot tell a blocked action from a broken tool will retry the blocked one, which is a doom loop ([Post 05](../05-agent-failure-modes/index.md) §2.4) manufactured by your own guardrail.

---

## 4. What to enforce deterministically

Hooks are for rules that are **cheap to check and must never be broken**, not for judgement. Reserve them for the failures where the right answer is always the same:

- **A deny-list at pre-tool.** Block the dangerous command outright: `rm -rf` on a broad path, a force-push, `DROP TABLE`, a fork bomb, `mkfs`. This is the direct fix for destructive action ([Post 05](../05-agent-failure-modes/index.md) §2.6). Judgement is not a safety control; a pattern match is.
- **Checks at post-edit.** Run the typecheck, the linter and the fast tests after every edit, and feed a failure back as an observation. The edit stands; what you have bought is that no broken edit survives to the next turn unnoticed.
- **Approval before the irreversible.** Opening a PR, deploying, touching production data: gate these behind a person. Because the decision must happen *before* the action, this is the escalate verdict of §3 on a set of tools marked sensitive, not a post-hoc review ([Post 15](../15-human-in-the-loop/index.md)).
- **Silent fixes.** Auto-format on save, add a trailing newline, sort imports. If a rule can be *repaired* deterministically rather than merely flagged, the hook should rewrite the input and say nothing.

The dividing line: if the correct response is always identical, enforce it with a hook; if it needs a judgement about *this* case, that is verification (Post 11) or evaluation (Post 12).

Where a rule attaches decides what it can do about a violation, and that is the reference worth keeping:

| Rule | Point | Can it block? | On violation | Cost per firing |
| --- | --- | --- | --- | --- |
| `rm -rf` on a broad path, a force-push | pre-tool | yes | reason returned as an observation | microseconds (a regex) |
| opening a PR, or a deploy | pre-tool (escalate) | yes, pending a person | the run pauses ([Post 15](../15-human-in-the-loop/index.md)) | a human response time |
| typecheck or lint after an edit | post-edit | no | failure appended as an observation | about a second |
| the full test suite after an edit | post-edit | no | failure appended as an observation | seconds to minutes: scope it |
| a secret in the diff | pre-commit | yes, blocks the commit | the commit fails | seconds |
| the memory file reaching the model | session-start | no: it supplies | nothing to violate | once per session |
| declaring done with red tests | stop gate | yes | the loop is refused its exit | one test run per exit attempt |

The pre-commit row carries a caveat that upgrades the picture, because a local git hook cannot defend itself: it "can be bypassed with the `--no-verify` option", and `git push --no-verify` bypasses the pre-push hook "completely" (Git, githooks and git-push documentation). An agent that hits a pre-commit block and is told to try again has a shell and one flag. Enforcement is therefore a ladder, each rung catching what the rung above cannot: a prompt rule is a request; a pre-tool hook blocks the call and can be bypassed only by editing the harness; a git hook blocks the commit unless somebody passes `--no-verify`; server-side branch protection with required status checks cannot be skipped from a client at all. The ladder implies a deny-list entry: `--no-verify` and `-n` belong at pre-tool, exactly where the rung below cannot protect itself. Any control the agent can disable from inside its own sandbox is an advisory control wearing a gate's clothes.

And note what a deny-list is not. It stops the dangerous commands you thought of, and says nothing about one you did not anticipate. Bounding what *any* command can reach (allow-lists, a directory jail, no network) is a different mechanism, and it is [Post 14](../14-permissions-sandboxes/index.md). The two are complementary: the hook is the cheap gate on obvious intent, the sandbox the boundary that holds when intent was not obvious.

---

## 5. Hooks are the enforcement half of the ratchet

[Post 10](../10-continual-learning-ratchet/index.md) defined the ratchet: every mistake becomes a rule, held by three teeth, a line in the memory file, a hook that enforces it, and a reviewer check. The hook is the second tooth, and the one that makes the ratchet hold.

A rule that lives only in the memory file is back to asking nicely, and it drifts (silent drift, [Post 05](../05-agent-failure-modes/index.md) §2.5): the model reads the line most of the time and ignores it under load. The hook converts a line in a team agreement into a property of the harness. When an agent ships a mistake once, the durable response is not a sterner prompt; it is a hook that makes the same mistake impossible on run two.

Osmani gives the worked case. An agent ships a pull request with a commented-out test and it is merged by accident: "The next version of my `AGENTS.md` says 'never comment out tests; delete them or fix them.' The next version of my pre-commit hook greps for `.skip(` and `xit(` in the diff" (Osmani, 2026). Notice what made that rule hookable. It reduced to a grep over a diff, not a judgement about test quality. A failure earns a hook exactly when a violation is deterministically detectable ([Post 10](../10-continual-learning-ratchet/index.md) §5); when it is not, a reviewer check is what you get instead. So a hook set grows from incidents rather than imagination, and each entry arrives with a story that tells the next reader why it is there.

---

## 6. Keeping hooks fast and quiet

A hook runs on every relevant action, which sets two constraints. It must be **fast**, because a slow pre-tool hook taxes every tool call and a slow post-edit check tempts everyone to switch it off. And it must be **quiet**: success is silent ([Post 11](../11-verification-loops/index.md) §4), so a hook speaks only when it blocks or reports. One that narrates every success trains the reader to ignore it.

Fast deserves a number rather than an adjective. Assume a subprocess costs 50 ms to spawn: a 200-tool-call run with a pre-tool hook implemented as a script pays 10 seconds of gate tax before any check does any work, which is why a deny-list belongs in-process as a compiled regular expression. A post-edit `pytest` at 8 seconds across 40 edits is over five minutes of a run spent re-running tests, which is why the scoped fast subset of [Post 11](../11-verification-loops/index.md) §6 is the post-edit default and the full suite belongs at pre-commit. The platform will not impose this discipline: the default hook timeout is 600 seconds (Anthropic, 2025–26).

**Scope the hook to what it cares about.** The cheapest way to keep a check off the hot path is not to run it. The companion's post-edit hook returns immediately unless the changed file is Python:

```python
def hook(path: str, content: str) -> Optional[str]:
    if not path.endswith(".py"):
        return None
    ok, report = run_tests()
    return None if ok else f"tests failed after editing {path}: {report}"
```

Real systems give you this as configuration rather than code, as a matcher on the tool name, so a hook registered against `Edit|Write` never fires for a read (Anthropic, 2025–26). Either way, a hook with no matcher is a tax on every action in the run.

Two defaults keep the system safe and usable. **Fail closed on safety**: if a deny-list check itself errors, block rather than allow, because the cost of a wrongly-run destructive command dwarfs the cost of a false block. And **do not over-hook**: every gate is latency and friction. The core is small:

```python
import re
from hook_system.hooks import ALLOW, Decision      # code/13-hooks

DENY = [(re.compile(p, re.IGNORECASE), why) for p, why in [
    (r"rm\s+-rf\s+(/|~|\*)",       "recursive delete of a broad path"),
    (r"git\s+push\s+--force",      "force-push"),
    (r"DROP\s+TABLE",              "destructive SQL"),
    (r":\(\)\s*\{.*\|:.*\};\s*:",  "fork bomb"),
    (r"\bmkfs\b",                  "filesystem format"),
]]

def pre_tool(tool: str, args: str) -> Decision:
    """Allow, or block a whole class of command. Fast, deterministic, fail-closed."""
    text = f"{tool} {args}"
    for pattern, why in DENY:
        if pattern.search(text):
            return Decision(allow=False, reason=f"blocked: {why}")   # never executed
    return ALLOW                                                     # silent on success
```

Compiling case-insensitively is not decoration: without it, `RM -RF /` walks past a list that blocks `rm -rf /`. That is the companion's list, before the `--no-verify` entry argued for in §4; §7 shows why its force-push pattern is not yet finished.

---

## 7. The escape hatch, and testing the guard

Two things separate a hook set that survives a year from one switched off in a week.

**Every hook needs a sanctioned way through.** Sooner or later a force-push is the correct action, and if the only route is editing the deny-list or disabling hooks for the session, someone will disable hooks for the session and forget to turn them back on. A guardrail with no exception path does not get respected; it gets removed. The mechanism is small: a named, single-use override token the pre-tool hook consumes.

```python
def with_override(hook, tokens, log):
    """Wrap a pre-tool hook so a named, reasoned, single-use override can pass one call."""
    def gated(tool: str, args: str) -> Decision:
        decision = hook(tool, args)
        if decision.allow:
            return decision
        token = tokens.pop(decision.reason, None)          # one rule, one token
        if token is None or not token.reason.strip():      # no token, or no reason: stay blocked
            return decision
        log.append({"rule": decision.reason, "why": token.reason, "who": token.who,
                    "at": token.at, "command": f"{tool} {args}"})
        return ALLOW                                       # spent: the token is gone
    return gated
```

Three properties do the work. The override names the rule it lifts, so it cannot silently widen to a neighbouring one. It requires a reason, in prose, from a person. And it is spent by the call it authorises, so nobody can leave the guard off. The log is the point rather than paperwork: an override that is recorded is one you can count, and a rule overridden more than a couple of times a week is either the wrong rule or the right rule wrapped in the wrong workflow, which is the firing-rate signal [Post 10](../10-continual-learning-ratchet/index.md) section 10 applies to memory-file lines. Give each outcome its own name in the trace as well, allowed against blocked against overridden, because a gate you cannot see fire is a gate you cannot trust ([Post 14](../14-permissions-sandboxes/index.md) §5, with [Post 21](../21-observability-traces/index.md) for the machinery).

**Every hook needs tests, and they have to be near misses.** A guardrail nobody tests is a guardrail nobody has, and the failure is quiet: a pattern that stopped matching after a refactor blocks nothing and reports nothing, so the first sign of trouble is the incident it was written to prevent. A deny-list fails in two directions and the obvious suite checks neither. Blocking `rm -rf /` and allowing `ls -la` proves nothing, because `ls -la` was never near the pattern. The tests that earn their keep are the commands one character away from the rule:

| Command | Should it run? | What the §6 pattern does |
| --- | --- | --- |
| `git push --force origin main` | no | blocked: correct |
| `git push --force-with-lease origin main` | yes, the safe idiom | blocked: a false positive that costs you trust |
| `git push -f origin main` | no | allowed: the same act, missed |
| `rm -fr /`, `rm --recursive --force /` | no | allowed: the same act, missed |

Neither direction is visible without the near-miss test, and both are cheap to fix once seen: `--force(?!-with-lease)|-f\b` on one side, an `rm` pattern that accepts the flags in either order and in long form on the other. The over-broad direction is the one people skip and the more expensive of the two, because a guardrail that blocks correct work is the guardrail somebody turns off.

The runnable companion in [`code/13-hooks/`](../../code/13-hooks/) wires the pre-tool deny-list together with a post-edit test runner into a small hook registry, and shows a gated call that refuses to execute a blocked command. Its nine tests run offline, with no application programming interface (API) key and no network (`python -m pytest -q`).

---

## Common pitfalls

- **Expecting a post-edit hook to reject an edit.** The write has already happened; a post-tool hook reports, and only a pre-tool hook prevents. Put the control at the point that can stop it, with a matcher on the editing tools (§2).
- **A block the model cannot act on.** Exiting 1 from a policy hook is a non-blocking error the model never sees; exit 2. And a reason of "error" leaves a model unable to tell a blocked action from a broken tool, so it retries the blocked one (§2, §3).
- **Hooking a judgement call.** Hooks are for rules with one correct answer. "Is this design good?" is verification or evaluation, not a deny-list (§4).
- **Trusting a git hook the agent can skip.** `--no-verify` bypasses it, and the agent has a shell. Put the flag on the pre-tool deny-list and the real gate server-side (§4).
- **A slow or chatty hook on the hot path.** A pre-tool hook runs on every call, so scope it with a matcher and keep it in-process; and narrating success trains the reader to ignore it (§6).
- **Failing open on safety.** If a safety check errors, block, do not allow. The asymmetry of cost demands fail-closed (§6).
- **No escape hatch, and no near-miss tests.** The first gets your hooks disabled; the second lets them rot silently, over-broad in one direction and porous in the other (§7).

---

## Further reading

- Addy Osmani, "Agent Harness Engineering" (2026): hooks as the enforcement layer, and the worked ratchet in which a merged commented-out test becomes a memory-file line and a pre-commit grep.
- Anthropic, "Claude Code hooks" documentation (2025–26): the event list, tool matchers, the blocking model (`PreToolUse` denies; `PostToolUse` only reports), the exit-code contract, and the default timeouts.
- NIOSH, "Hierarchy of Controls" (2024): the five-rung taxonomy that ranks a written procedure below an engineering control, and says why.
- Git, "githooks" and "git-push" documentation (2026): which hooks exist client-side, and the `--no-verify` bypass that makes them the wrong last line of defence.
- awesome-harness-engineering (2026): the Permissions and Verification sections.
- Context Engineering, Post 26: hooks as a workflow feature, with the seven-point list this post reduces to four points and a stop gate.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 14 — Permissions, sandboxes & security](../14-permissions-sandboxes/index.md)**: bounding the blast radius of what a deny-list cannot anticipate.
- **[Post 25 — Build #2: hooks, sandbox, and sub-agents](../25-build-harness-plus/index.md)**: where this deny-list becomes a running gate inside a real harness.
- **[Post 10 — Continual learning & the ratchet](../10-continual-learning-ratchet/index.md)**: the hook as the enforcement tooth of the ratchet.
