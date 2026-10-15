# 13 - Hooks and deterministic enforcement: guardrails as code

> **TL;DR.** Verification still runs through the model's cooperation, and some rules must hold whatever the model decides. A **hook** is deterministic code the harness runs at a fixed lifecycle point (session start, before a tool, after an edit, before a commit) to enforce a rule unconditionally, turning "please don't" into *can't*. Only the two points in front of an action can block it; the other two supply or report. Hooks are the enforcement tooth of the ratchet, kept for failures that must be structurally impossible, and kept fast and silent unless they fire.
>
> **Prerequisites:** [post 11](../11-verification-loops/index.md), the verification gate on the loop's final answer.
> **Safe to skip?** Skip it if the reader can already say which hook events can block and why a policy hook exits 2 rather than 1, keep a deny-list in-process and test it with near misses, and give a guard a logged, single-use override.
>
> **After reading, you will be able to:**
>
> - Name the four hook lifecycle points, session start, pre-tool, post-edit and pre-commit, say which two can block, and place the stop gate beside them.
> - Write a pre-tool gate and a post-edit report hook with their signatures and the exit-code contract, so that a block reaches the model with its reason.
> - Decide which rules to enforce with a hook and which to leave to verification, and explain why the hook is the enforcement tooth of the ratchet.
> - Keep a hook fast and quiet: scope it with a matcher, keep a deny-list in-process, and fail closed on safety.
> - Give a hook a named, single-use, logged escape hatch, and test it with near misses in both directions.

![The agent loop, reason, act and observe, inside a frame, with four hook points. Session start, a grey square between the memory file and reason, supplies. Pre-tool, a purple diamond on the arrow into act, blocks the call. Post-edit, a grey square after act, reports only. Pre-commit, a purple diamond on the way out to git, blocks the commit, one layer below the agent.](diagrams/01-hook-lifecycle.svg)

*Four fixed points, and the model does not choose whether they run. A rule that must never break belongs at a diamond; a square only informs.*

---

## 1. The question: which rules are too important to leave to the model?

Everything in this Part so far has routed through the model. The verification loop of [post 11](../11-verification-loops/index.md) checks the work and hands a failure back for the model to fix; the evaluator of [post 12](../12-planner-generator-evaluator/index.md) is another model call. That is fine for judgement, but some rules cannot depend on it. "Never force-push to main." "Never commit a secret." These must hold on every run, including the run where the model is confused, distracted near a full window, or steered by a hostile instruction that reached it through a tool result ([post 07](../07-skills-mcp-runtime/index.md)).

A rule that lives only in a prompt is a *request*. The model can forget it, reason around it, or be talked out of it, and the failure is silent: the rule can hold on many runs and break on the next, with nothing in the transcript to mark which kind of run it is.

Occupational safety has ranked controls of that shape for decades. The hierarchy of controls of the United States National Institute for Occupational Safety and Health (NIOSH) orders five kinds from most to least effective: elimination, substitution, engineering controls, administrative controls, and personal protective equipment. Administrative controls establish work practices (training, job rotation, limits on access) and sit near the bottom because, like protective equipment, they "require significant and ongoing effort by workers and their supervisors" (NIOSH, "Hierarchy of Controls", 10 April 2024). A rule in a system prompt is an administrative control. A hook is an engineering control, and the sandbox of [post 14](../14-permissions-sandboxes/index.md) is closer to substitution.

So the harness stops asking. A **hook** is deterministic code that runs at a fixed point in the run and enforces the rule in the harness, not in the model: component 07, hooks, one of the four in [post 02](../02-anatomy-of-a-harness/index.md) that govern the loop. The model can propose `rm -rf /` as often as it likes, and the command still never runs, because the rule now lives somewhere the model cannot reach.

---

## 2. The four lifecycle points, and which two can block

Addy Osmani's "Agent Harness Engineering" (April 2026) places hooks at four points: "before a tool call, after a file edit, before commit, on session start". Vendors expose more: Claude Code's "Hooks reference" lists 33 events (Anthropic, consulted October 2026). The four are this series' reduction of that longer list, the points every harness needs whatever its vendor, and they are *not* equally powerful:

- **Session start.** Once, before the loop begins. Inject the memory file ([post 10](../10-continual-learning-ratchet/index.md)), load project configuration, run startup checks. It cannot block; it *supplies*.
- **Pre-tool.** Before any tool executes. The hook sees the proposed call and can **block** it: a deny-list match, a permission check, a path outside the working directory. It is the only point *inside the loop* where a hook can stop a tool call.
- **Post-edit.** After a file changes. Run a typecheck, the tests, a formatter. It **cannot undo the edit**, because the write already happened; it can only report, as an observation the model must deal with.
- **Pre-commit.** Before a commit or a pull request (PR). Require the tests green, scan for secrets. This is usually not a harness event at all but the ordinary git hook, one layer below the agent, which is why it still fires when the agent is not the thing committing; section 4 takes up its documented bypass.

Two of the four can block, and they block different things: pre-tool refuses a tool call inside the loop, pre-commit refuses a commit one layer below it. Session start is how a rule arrives; post-edit is how the harness finds out that one was broken. Getting that backwards is how a hook set ends up decorative.

"Supplies" is literal. Session start is one of four Claude Code events whose plain-text standard output is added to the model's context, and its matcher filters on *how* the session started: `startup`, `resume`, `clear`, `compact` or `fork` (Anthropic, "Hooks reference", consulted October 2026). Compaction ([post 09](../09-context-management-loop/index.md)) can summarise away the rules the ratchet accumulated, and a hook matched to `compact` re-injects them. `ctx-026` places six of Claude Code's events on the loop; this post groups them by what they can do.

**The stop gate.** One extra event matters enough to name. Claude Code lets a hook block several events, including `UserPromptSubmit`, `SubagentStop` and `Stop`. A blocking `Stop` hook is the deterministic answer to victory declaration ([post 05](../05-agent-failure-modes/index.md)): a hook that runs the tests when the agent tries to finish and exits 2 with `tests are red: 3 failing in the parser suite` refuses the loop exit (1), final answer, and the message becomes the next observation. That is the verification gate of post 11, attached through the host's hook system instead of written into the loop. A gate that never passes is an infinite loop, so Claude Code ends the turn after eight consecutive continuations forced by stop hooks and passes a `stop_hook_active` flag (Anthropic, "Hooks reference", consulted October 2026); a harness of its own pairs the gate with exit (2), iteration cap, and exit (3), budget, of [post 03](../03-the-agent-loop/index.md).

The blocking asymmetry is written into the runtime. `PreToolUse` can deny a call outright: the hook exits 2, or returns a `permissionDecision` of `deny`, and the tool never runs. `PostToolUse` cannot: an exit of 2 there shows the hook's standard error to the model, because "the tool already ran". Any *other* non-zero exit, without valid JavaScript Object Notation (JSON) on standard output, is a "non-blocking error": the action goes ahead, the user sees a notice in the transcript, and the model sees nothing. The reference is plain: "If your hook is meant to enforce a policy, use exit 2" (Anthropic, "Hooks reference", consulted October 2026). Exit 1, the conventional failure code, gives a policy hook that tells the person and never the model. "Post-edit" is not a distinct event either; it is a post-tool hook with a matcher scoped to the editing tools.

So the honest framing is: **pre-tool prevents, post-edit corrects.** A post-edit hook does not protect a run from a bad edit; it guarantees the run *finds out* about one at once, without relying on the model to check. To prevent a bad edit, gate at pre-tool with a matcher of `Edit|Write` and check the target path before the write: outside the working tree, a vendored directory, a lockfile, a test file the agent may not weaken. Post-edit then covers only what cannot be known beforehand: whether the file still typechecks and passes its tests.

`snippets/block_vs_report.py` runs both halves with the [code companion](../../code/13-hooks/) in a temporary directory. It sends `rm -rf workspace` at a workspace holding a marker file, first through the companion's shipped deny-list and then with one rule added, and it writes a broken `calc.py` under a post-edit test runner:

```text
shipped deny-list:     'rm -rf workspace' -> ran: bash rm -rf workspace
  executor calls: 1; marker file exists afterwards: False
with the added rule:   'rm -rf workspace' -> blocked: recursive delete of the workspace
  executor calls: 0; marker file exists afterwards: True
post-edit, calc.py written with a bug:
  report: tests failed after editing calc.py: AssertionError: add(2, 2) != 4
  the broken edit is still on disk: True
```

The first run is a warning in its own right: the shipped list blocks `rm -rf` only on a broad path (`/`, `~`, `*`), so a named directory walked past it. The figure below draws the other two side by side.

![Two runs drawn as turns from left to right, with a dashed line at the act. In the first, the model proposes rm -rf workspace, the purple pre-tool hook blocks it before the line, the executor is never called, and marker.txt still exists. In the second, nothing stands in front of the edit, calc.py is written and stays, and the post-edit hook reports AssertionError after the line.](diagrams/02-block-vs-report.svg)

*The block lands before the act and the shell is never reached; the report lands after it, and the edit stands.*

---

## 3. The shape of a hook: gates and reports

Because the two kinds of hook do different jobs, they have different signatures. The companion makes the split explicit:

```text
pre-tool hook:  (tool: str, args: str) -> Decision          # allow, or block with a reason
post-edit hook: (path: str, content: str) -> str | None     # a problem, or nothing
```

A pre-tool hook returns a **verdict**. A post-edit hook returns a **finding**. Collapsing them into one type invites code that treats a post-edit failure as a block, which the runtime cannot honour.

The composition rules differ too. Pre-tool hooks are evaluated in order and **the first block wins**: there is no point asking the rest about a command already ruled out, and stopping early keeps the hot path cheap. From the companion's `hooks.py`:

```python
    def check_tool(self, tool: str, args: str) -> Decision:
        """Run every pre-tool hook; the first block wins (fail-closed on a match)."""
        for hook in self.pre_tool:
            decision = hook(tool, args)
            if not decision.allow:
                return decision
        return ALLOW
```

Post-edit hooks run to completion and **collect every problem**, because the model is about to spend a turn responding and should see all of what broke; hiding three test failures behind a typecheck error buys a round trip that finds them anyway. The figure below runs both rules through the companion's registry.

![Left, rm -rf / meets three pre-tool hooks in order: the secret scan allows, the deny-list blocks, and the permission check, drawn dashed, is never asked; one reason returns. Right, an edit meets three post-edit hooks and all run: typecheck and tests each report a problem, the formatter finds nothing, and both problems return as one observation.](diagrams/03-gates-and-reports.svg)

*A gate stops at the first block; a report runs everything and returns all it found.*

A production verdict has more than two values. Claude Code's `PreToolUse` decision takes `allow`, `deny`, `ask`, which hands the call to a person's permission prompt, and `defer`, which, in a non-interactive `-p` run, exits so the call can be resumed later; an `updatedInput` field replaces the tool's arguments before it runs, which lets a hook repair the input rather than report it (Anthropic, "Hooks reference", consulted October 2026). The companion keeps the two-verdict form because the composition rule is easier to see without them.

**What a hook is on disk.** Those signatures are the real contract with the JSON stripped off. In a host, a hook is a configuration entry naming an event, a matcher and a command; the command is handed a JSON object on standard input and answers with an exit code, or with JSON on standard output. In Claude Code's shape:

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

The script illustrates the vendor's shape; this post does not run it. Three details repay attention. The exit code is 2 rather than 1. The tool input is *parsed* rather than interpolated, because it is model-chosen text that may repeat an instruction from a tool result: a hook that splices it into a shell string is a command-injection sink inside the harness's own trust boundary ([post 14](../14-permissions-sandboxes/index.md)). And the timeout is explicit, because the default for a command hook is 600 seconds (Anthropic, "Hooks reference", consulted October 2026), which is not a budget so much as the absence of one.

The last piece is what the model sees. A blocked call does not raise, and it does not return nothing; it returns its reason, in the channel a successful call would have used:

```python
def gated_call(
    registry: HookRegistry,
    tool: str,
    args: str,
    execute: Callable[[str, str], str],
) -> str:
    """Run pre-tool hooks, then execute only if allowed. A blocked call never runs."""
    decision = registry.check_tool(tool, args)
    if not decision.allow:
        return decision.reason  # deterministic observation; execute is never called
    return execute(tool, args)
```

So the reason string is part of the design. `"blocked: force-push"` tells the model what rule it hit and lets it choose another route. `"error"` tells it nothing, and a model that cannot tell a blocked action from a broken tool may retry the blocked one: a doom loop ([post 05](../05-agent-failure-modes/index.md)) manufactured by the harness's own guardrail.

---

## 4. What to enforce deterministically

Hooks are for rules that are **cheap to check and must never be broken**, where the right answer is always the same:

- **A deny-list at pre-tool.** Block the dangerous command outright: `rm -rf` on a broad path, a force-push, `DROP TABLE`, a fork bomb, `mkfs`. This is the direct fix for destructive action ([post 05](../05-agent-failure-modes/index.md)). Judgement is not a safety control; a pattern match is.
- **Checks at post-edit.** Run the typecheck, the linter and the fast tests after every edit, and feed a failure back as an observation. The edit stands; what the harness has bought is that no broken edit survives to the next turn unnoticed.
- **Approval before the irreversible.** Opening a PR, deploying, touching production data: gate these behind a person. Because the decision must happen *before* the action, this is the `ask` decision on a set of tools marked sensitive, not a post-hoc review ([post 15](../15-human-in-the-loop/index.md)).
- **Silent fixes.** Auto-format on write, add a trailing newline, sort imports. If a rule can be *repaired* deterministically rather than merely flagged, the hook rewrites the input and says nothing.

The dividing line: if the correct response is always identical, enforce it with a hook; if it needs a judgement about *this* case, that is verification (post 11) or evaluation (post 12).

Where a rule attaches decides what it can do about a violation. The last column is an illustrative order of magnitude, not a measurement:

| Rule | Point | Can it block? | On violation | Rough cost per firing |
| --- | --- | --- | --- | --- |
| `rm -rf` on a broad path, a force-push | pre-tool | yes | reason returned as an observation | microseconds (an in-process regex) |
| opening a PR, or a deploy | pre-tool (`ask`) | yes, pending a person | the run pauses ([post 15](../15-human-in-the-loop/index.md)) | a human response time |
| typecheck or lint after an edit | post-edit | no | failure appended as an observation | about a second |
| the full test suite after an edit | post-edit | no | failure appended as an observation | seconds to minutes: scope it |
| a secret in the diff | pre-commit | yes, blocks the commit | the commit fails | seconds |
| the memory file reaching the model | session start | no: it supplies | nothing to violate | once per session |
| declaring done with red tests | stop gate | yes | the loop is refused exit (1) | one test run per exit attempt |

The pre-commit row carries a caveat, because a local git hook cannot defend itself. The pre-commit hook "can be bypassed with the `--no-verify` option", which `git commit` also spells `-n`, and with `git push --no-verify` the pre-push hook "is bypassed completely" (Git, githooks, git-commit and git-push documentation, consulted October 2026). An agent that hits a pre-commit block has a shell and one flag. Enforcement is therefore a ladder: a prompt rule is a request; a pre-tool hook blocks the call and can be bypassed only by editing the harness; a git hook blocks the commit unless somebody passes `--no-verify`; server-side branch protection with required status checks is out of reach of any client-side flag. So `--no-verify`, and `-n` on `git commit` (on `git push`, `-n` is a dry run), belong on the pre-tool deny-list, where the rung below cannot protect itself.

And a deny-list is not a boundary. It stops the commands its author thought of, as the named-directory delete of section 2 showed. Bounding what *any* command can reach (allow-lists, a directory jail, no network) is the sandbox of [post 14](../14-permissions-sandboxes/index.md): the hook is the cheap gate on obvious intent, the sandbox the boundary that holds when intent was not obvious.

---

## 5. Hooks are the enforcement tooth of the ratchet

[Post 10](../10-continual-learning-ratchet/index.md) defined the ratchet: every mistake becomes a rule, held by three teeth, a line in the memory file, a hook that enforces it, and a reviewer check, so that a mistake has to defeat all three to recur. The hook is the second tooth, and the one that makes the ratchet hold.

A rule that lives only in the memory file is back to asking nicely, and it drifts (silent drift, [post 05](../05-agent-failure-modes/index.md)): the model can read the line and still not follow it. The hook turns the line into a property of the harness, so the durable response to a mistake shipped once is not a sterner prompt but a hook that makes it impossible on the next run.

Osmani's worked case is a pull request with a commented-out test, merged by accident: "The next version of my pre-commit hook greps for `.skip(` and `xit(` in the diff" (Osmani, April 2026). That rule was hookable because it reduced to a grep over a diff, not a judgement about test quality. A failure earns a hook exactly when a violation is deterministically detectable, the test post 10 applies to every memory-file line; when it is not, it gets a reviewer check instead. So a hook set grows from incidents rather than imagination, and each entry arrives with a story that says why it is there.

---

## 6. Keeping hooks fast and quiet

A hook runs on every relevant action, which sets two constraints. It must be **fast**, because a slow pre-tool hook taxes every tool call and a slow post-edit check tempts everyone to switch it off. And it must be **quiet**: success is silent, failures are verbose, HumanLayer's phrase as Osmani reports it (post 11), so a hook speaks only when it blocks or reports. One that narrates every success trains the reader to ignore it.

Fast deserves a number. With illustrative figures, a subprocess that costs 50 ms to spawn, on a run of 200 tool calls with a pre-tool hook written as a script, pays $200 \times 50 = 10{,}000$ ms, 10 seconds of gate tax before any check does any work, which is why a deny-list belongs in-process as a compiled regular expression. A post-edit `pytest` of 8 seconds across 40 edits is $40 \times 8 = 320$ seconds, over five minutes, which is why a scoped fast subset is the post-edit default and the full suite belongs at pre-commit. The platform will not impose this: the default hook timeout is 600 seconds.

**Scope the hook to what it cares about.** The cheapest check is the one not run. The companion's post-edit hook returns at once unless the changed file is Python:

```python
    def hook(path: str, content: str) -> Optional[str]:
        if not path.endswith(".py"):
            return None
        ok, report = run_tests()
        return None if ok else f"tests failed after editing {path}: {report}"
```

A host gives this as configuration rather than code, a matcher on the tool name, so a hook registered against `Edit|Write` never fires for a read. Either way, a hook with no matcher is a tax on every action in the run.

Two defaults keep the system safe and usable. **Fail closed on safety**: if a deny-list check itself errors, block rather than allow, because the cost of a wrongly-run destructive command dwarfs the cost of a false block. In Claude Code a hook that crashes, times out or cannot start is a non-blocking error by default, so a policy hook sets `onFailure: "block"` (Anthropic, "Hooks reference", consulted October 2026). And **do not over-hook**: every gate is latency and friction. The core is small; the companion's whole deny-list is five patterns:

```python
DEFAULT_DENY: List[Tuple[str, str]] = [
    (r"rm\s+-rf\s+(/|~|\*)",       "recursive delete of a broad path"),
    (r"git\s+push\s+--force",      "force-push"),
    (r"DROP\s+TABLE",              "destructive SQL"),
    (r":\(\)\s*\{.*\|:.*\};\s*:",  "fork bomb"),
    (r"\bmkfs\b",                  "filesystem format"),
]
```

`deny_list()` compiles them once, when the hook is built, and case-insensitively, which matters for Structured Query Language (SQL), where `drop table` is the same statement as `DROP TABLE`. That is the list before the `--no-verify` entry of section 4, and the next section shows why its force-push pattern is not finished.

---

## 7. The escape hatch, and testing the guard

Two things separate a hook set that survives a year from one switched off in a week.

**Every hook needs a sanctioned way through.** Sooner or later a force-push is the correct action, and if the only route is disabling hooks for the session, someone will do that and forget to turn them back on. A guardrail with no exception path gets removed. The mechanism is small: a named, single-use override token the pre-tool hook consumes. `snippets/override.py` wraps the companion's deny-list with one (the companion does not ship it):

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

Run against two tokens, one with an empty reason and one for the force-push rule, it prints:

```text
DROP TABLE, token has no reason    -> blocked: destructive SQL
rm -rf /, no token for that rule   -> blocked: recursive delete of a broad path
force-push, token for this rule    -> allowed
force-push again, token spent      -> blocked: force-push
override log: [{'rule': 'blocked: force-push', 'why': 'rewrite a leaked secret out of history', 'who': 'release-lead', 'at': '2026-10-15T10:05', 'command': 'bash git push --force origin main'}]
tokens left: []
```

Three properties do the work. The override names the rule it lifts, so it cannot widen to a neighbouring one. It requires a reason, in prose, from a person. And it is spent by the call it authorises, so nobody can leave the guard off. The log is the point: a recorded override can be counted, and a rule overridden every few days is either the wrong rule or the right rule in the wrong workflow, the firing-rate signal post 10 reads for memory-file lines. Each outcome also gets its own name in the trace, allowed, blocked or overridden, because a gate nobody can see fire is a gate nobody can trust ([post 21](../21-observability-traces/index.md)).

**Every hook needs tests, and they have to be near misses.** A pattern that stopped matching after a refactor blocks nothing and reports nothing, so the first sign of trouble is the incident it was written to prevent. A deny-list fails in two directions and the obvious suite checks neither: blocking `rm -rf /` and allowing `ls -la` proves nothing, because `ls -la` was never near the pattern. The tests that earn their keep are the commands one step away from the rule. `snippets/near_miss.py` scores eight of them against the companion's patterns and against a fix:

```text
command                                  should   shipped         fixed
git push --force origin main             block    blocked         blocked
git push --force-with-lease origin main  run      FALSE POSITIVE  runs
git push -f origin main                  block    MISSED          blocked
git push origin main --force             block    MISSED          blocked
rm -rf /                                 block    blocked         blocked
rm -fr /                                 block    MISSED          blocked
rm --recursive --force /                 block    MISSED          blocked
rm -rf ./build                           run      runs            runs
wrong: shipped 5 of 8, fixed 0 of 8
```

Neither direction is visible without the near-miss test, and both are cheap to fix once seen: the fixed force-push pattern is `git\s+push\b.*(--force(?![\w-])|\s-f\b)`, and the fixed `rm` pattern accepts the two flags in either order and in long form. It is still a list of spellings, which is why post 14 exists. The over-broad direction is the more expensive one, because a guardrail that blocks correct work is the guardrail somebody turns off.

---

## 8. Make it run

The [code companion](../../code/13-hooks/) is one module, `hooks.py`, with the `Decision` type, `deny_list()`, `post_edit_tests()`, the `HookRegistry` whose `check_tool` section 3 quotes, and `gated_call`. Its nine tests run offline, with no application programming interface (API) key and no network. From inside `code/13-hooks/`:

```bash
uv run --extra dev pytest -q
uv run python -m hook_system
```

The first runs the nine tests; the second runs the demo, which lets `ls -la` through, blocks `rm -rf /` and `git push --force`, and reports a broken edit to `math_utils.py`.

The lab for this post adds a deny rule for one destructive command and a post-edit test runner, and shows the command blocked before execution while the test failure is only reported. That is `snippets/block_vs_report.py`, whose output section 2 quotes; the other two snippets print the outputs of section 7. From the series root:

```bash
uv run python posts/13-hooks-enforcement/snippets/block_vs_report.py
uv run python posts/13-hooks-enforcement/snippets/override.py
uv run python posts/13-hooks-enforcement/snippets/near_miss.py
```

To try a variation, delete `ADDED_RULE` from the second registry in `block_vs_report.py` and watch the marker file disappear and the snippet's check fail, or add `git commit --no-verify` to the near-miss cases and write the pattern that blocks it.

---

## 9. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **A policy hook that exits 1.** The hook prints its refusal and exits 1; the tool call goes ahead, the person sees a hook error notice, and the model never learns a rule fired.
- **A post-edit hook expected to prevent.** The deny rule is written as a post-tool hook on `Edit|Write`; the forbidden file is overwritten anyway, and the report arrives one turn after the damage.
- **A deny-list trusted as the boundary.** The audit shows the hook blocking `rm -rf /`, and the incident is `rm -rf workspace`, a spelling nobody listed.
- **A hook script that cannot start.** A mistyped path in the settings file makes the shell exit 127; without `onFailure: "block"` that is a non-blocking error, and every guarded command runs unguarded.
- **A stop gate with no cap of its own.** The gate exits 2 on a test that can never pass; the loop is held until a cap or a budget ends it, and every forced continuation is billed.

---

## Common pitfalls

1. **Expecting a post-edit hook to reject an edit.** The write has already happened; put the control at pre-tool, with a matcher on the editing tools.
2. **A block the model cannot act on.** Exit 1 is a non-blocking error the model never sees, and a reason of "error" cannot be told from a broken tool, so the model retries the blocked call.
3. **Hooking a judgement call.** Hooks are for rules with one correct answer. "Is this design good?" is verification or evaluation, not a deny-list.
4. **Trusting a git hook the agent can skip.** `--no-verify` bypasses it, and the agent has a shell; put the flag on the pre-tool deny-list and the real gate server-side.
5. **A slow, chatty or fail-open hook.** Scope it with a matcher, keep it in-process, stay silent on success, and block when the check itself errors.
6. **No escape hatch, and no near-miss tests.** The first gets the hooks disabled; the second lets them rot, over-broad one way and porous the other.

---

## Further reading

- Anthropic, "Hooks reference", Claude Code documentation (consulted October 2026). The event list, tool matchers, the exit-code contract per event, `permissionDecision` and `updatedInput`, the stop-hook continuation cap, `onFailure`, and the default timeouts.
- Addy Osmani, "Agent Harness Engineering" (April 2026). Hooks as the enforcement layer at four lifecycle points, and the worked ratchet in which a merged commented-out test becomes a memory-file line and a pre-commit grep.
- NIOSH, "Hierarchy of Controls" (10 April 2024). The five-level ranking that puts administrative controls below engineering controls, and says why.
- Git, "githooks", "git-commit" and "git-push" documentation (consulted October 2026). The client-side hooks, and the `--no-verify` bypass that makes them the wrong last line of defence.
- ai-boost, awesome-harness-engineering (GitHub, consulted October 2026), the Permissions & Authorization and Verification & CI Integration sections. Curated sources on gating an agent.
- `ctx-026` (`context-engineering`): hooks as a workflow feature, with six of Claude Code's events placed on the loop and a hook that guards edits.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 14 - Permissions, sandboxes, and security: the AI control plane](../14-permissions-sandboxes/index.md):** bounding the blast radius of what a deny-list cannot anticipate.
- **[Post 15 - Human-in-the-loop: approvals, interventions, async feedback](../15-human-in-the-loop/index.md):** the `ask` decision made into an approval gate, for the irreversible actions a hook should not decide alone.
