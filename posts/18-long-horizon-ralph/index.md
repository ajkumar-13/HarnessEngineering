# 18 - Long-horizon and multi-context execution: Ralph loops and context bridging

> **TL;DR.** Some tasks are bigger than any one context window, however well it is managed, and the answer is not a bigger window but the **Ralph loop**: a fresh context reads a written spec, does one task, commits, and is thrown away, again and again, with all the state on disk. Each reset re-reads a frozen prefix that a prompt cache can serve, provided the cache's clock is chosen from the gaps between reads. The spec stays out of the agent's reach, and the driver, not the agent's report, decides when the work is done, with guards that stop a loop that will not converge.
>
> **Prerequisites:** [post 09](../09-context-management-loop/index.md), the ladder of context moves and the reset behind a handoff file.
> **Safe to skip?** Skip it if the reader can already drive a build across many fresh contexts against a spec the agent cannot edit, price the resets against the prompt cache, and stop such a loop on a gate, a cap, a stale count and a moved spec.
>
> **After reading, you will be able to:**
>
> - Recognise work that has outgrown one context window, and run a Ralph loop: fresh context, written spec, one task, commit, repeat.
> - Size one iteration to one verifiable increment, and price its re-entry tax against the prompt cache's tiers and its clock.
> - Bridge contexts with a read-only spec and a handoff file, and keep the definition of done out of the agent's reach.
> - Enforce convergence with a gate the driver runs, and stop a loop on an iteration cap, a stale-commit count or a moved spec.
> - Design a multi-context build with an initialiser and an end-to-end gate, and plan the review of the commits it leaves.

![Across the top, four files on disk survive every reset: the spec, which a human writes; the handoff file, rewritten each iteration; the status file, whose pass bits the gate writes; and the git history, one commit per iteration. Below, a fresh process reads them and commits one task, the driver's gate runs every check, and the process exits, discarding the window. Four purple stops end the loop: every check passing, exit (1); 50 iterations, exit (2); three rounds without a commit, exit (4); and moved spec bytes, `spec_moved`.](diagrams/01-ralph-loop.svg)

*The window is disposable and the disk is the memory; the driver, not the agent, says when to stop.*

---

## 1. The question: work that outgrows one window

How does a harness finish a task that is bigger than any single context window? [Post 17](../17-parallel-agents-shared-repo/index.md) handled work that was too *much* for one agent. This post handles work that is too *big* for one context: building a whole project, a refactor across hundreds of files, a task whose full state will not fit in a window however carefully it is compacted ([post 09](../09-context-management-loop/index.md)).

Holding such a task in one long-running context fails in known ways. The window fills, context rot sets in (`ctx-006`), and on models prone to it the agent starts wrapping up early as the room runs out, the context anxiety of [post 05](../05-agent-failure-modes/index.md). Rajasekaran reports Opus 4.5 largely removing that behaviour (Anthropic, 24 March 2026), which removes one reason to reset but not the size of the task.

The obvious reply is to wait for a larger window. It does not settle the question, because the work moves too. METR (Model Evaluation and Threat Research) measured the length of software task a frontier model completes with 50% reliability and found it "doubling approximately every seven months since 2019" (Kwa et al., "Measuring AI Ability to Complete Long Software Tasks", March 2025). That measures task length, not window size; the argument drawn from it here is that the jobs handed to agents grow with what agents can do, so a bigger window meets a bigger job.

The cheaper fixes also run out before the hard cases do, and that is a reported finding. Anthropic's "Effective harnesses for long-running agents" (Justin Young, 26 November 2025) says of an agent with compaction available, "However, compaction isn't sufficient", and that even Opus 4.5 on the Claude Agent software development kit (SDK), looping across multiple context windows, falls short of a production-quality web application when given only a high-level prompt. This post starts on the last rung of post 09's ladder and makes the reset not an emergency measure but the ordinary thing that happens between units of work.

---

## 2. The Ralph loop

That architecture has a name. The **Ralph loop** runs the same prompt against a written spec, lets the agent do one task in a fresh context, commits the result, discards the context, and repeats. Geoffrey Huntley named it in "Ralph Wiggum as a 'software engineer'" (14 July 2025): Ralph "works autonomously in a single repository as a single process that performs one task per loop". The spec on disk is the source of truth; the window is a scratchpad thrown away every iteration.

The name is Ralph Wiggum, from *The Simpsons*, and the joke carries the argument. Huntley's framing is "the technique is deterministically bad in an undeterministic world". The loop is not clever about where it is or what it learned, because it threw both away; it re-reads a spec and a repository every time, brute force plus persistence. The evidence that it meets real work is anecdotal and at one remove: Huntley writes that an engineer he taught "used Ralph on their next contract", and beside it embeds a message he was sent, "Cost of a $50k USD contract, delivered, MVP, tested + reviewed" (MVP being a minimum viable product), at $297 with the Amp coding agent. That is a reported outcome, an unnamed engineer's account passed on by the technique's author, not a benchmark.

Its canonical form, in Huntley's article, is one line of shell:

```bash
while :; do cat PROMPT.md | claude-code ; done
```

There is no state in that command, no iteration count, no convergence check and no stop condition. Everything that makes it work sits in `PROMPT.md`, in the repository it runs against, and in the fact that the agent process exits and starts again. The rest of this post is the guards a harness adds before pointing that loop at work that matters.

---

## 3. Sizing one task, and the re-entry tax

Deciding what one iteration does is where the design lives, because every iteration pays a **fixed cost** before it does anything useful: read the spec, read the handoff, orient in the repository. Call it the **re-entry tax**, and split it in two, because the halves behave nothing alike.

The **frozen half** is the system prompt and the spec. It is byte-identical on every iteration, so a prompt cache can serve it at a tenth of the input price. The next section gives the conditions, which are narrower than they look.

The **volatile half** is orientation in a repository that just changed: the status of each criterion, the handoff file, the version history, the files the next task touches. None of it caches, because none of it is the same twice. The figure below opens one iteration of this post's driver: in its toy build the frozen prefix is 208 tokens in every iteration, and the volatile part grows from 28 to 137 tokens at re-entry as history accumulates.

![One iteration's context stacked stable first: the system prompt and the spec, bracketed as the frozen prefix of 208 tokens, byte-identical in every iteration; then the status file, the handoff, the git log and the source files, bracketed as volatile, 28 to 137 tokens at re-entry; then the iteration's own work. Beside it, who may write each file: the spec only a human, the status file only the gate, the handoff and the source the loop.](diagrams/02-inside-one-iteration.svg)

*The part that never changes sits first, where a cache can find it; the part the agent may change sits after it.*

Slice too **large** and the iteration overflows its window, which is the problem being solved. Slice too **small** and the volatile half dominates: an iteration that spends four thousand uncacheable tokens (an illustrative size) working out where the repository is in order to change one line is mostly overhead. Re-reading a cached spec is nearly free; re-orienting in a repository that moved is not.

The workable heuristic is to size a task to **one verifiable increment**: the smallest change that leaves the repository in a state where the checks can say yes or no. It is the boundary the commit and the verification gate already use ([post 11](../11-verification-loops/index.md)), so the loop, the history and the check agree on what a unit of progress is.

---

## 4. Keeping the reset cheap: the frozen prefix and the cache clock

A Ralph loop rebuilds its context fifty times, which sounds ruinous. Two decisions settle whether it is.

The first is **ordering**. If each iteration assembles its context stable first and volatile last (system prompt, spec, then status, handoff and repository state), the leading part is byte-identical across iterations and the provider's prompt cache serves it, because a cache matches an exact prefix ([post 09](../09-context-management-loop/index.md)). This is the freeze-the-prefix rule of `ctx-005`. Put the volatile handoff above the fixed spec and the prefix breaks at the handoff on every iteration.

The second is the **clock**, and it is the one designs fail on. "The lifetime is measured from the start of the request that writes or reads the cache entry, not from the end of its response", and each read refreshes it at no extra charge (Anthropic, "Prompt caching", Claude Platform documentation, consulted October 2026). The default lifetime is five minutes; a one-hour lifetime costs 2x base input to write instead of 1.25x. So the number that matters is not how long an iteration runs but the longest gap between two requests that share the prefix. Calls inside an iteration follow each other within seconds and keep it warm. The gap that goes cold is a long step between reads: a full test suite, or the driver's own end-to-end gate running for eight minutes between one iteration's last call and the next one's first.

`uv run python posts/18-long-horizon-ralph/snippets/reset_cost.py` prices a frozen prefix of 12,000 tokens over 50 iterations at Claude Sonnet 4.6's rate of $3 per million input tokens, with cache reads at 0.1x (Anthropic, "Pricing", consulted October 2026); the sizes are illustrative:

```text
frozen prefix 12,000 tokens, 50 iterations, $3.00 per million input tokens (Claude Sonnet 4.6)
one full read $0.0360; five-minute write $0.0450; one-hour write $0.0720; cache read $0.0036
tier                re-entry gap      writes  reads  re-entry only   with 20 calls inside
no cache configured any gap              n/a    n/a          $1.80                 $36.00
five-minute tier    under 5 minutes        1     49          $0.22                  $3.64
five-minute tier    about 8 minutes       50      0          $2.25                  $5.67
one-hour tier       about 8 minutes        1     49          $0.25                  $3.67
(writes and reads count the re-entry calls)
re-entry only: a cold five-minute tier costs 25% more than no cache at all
with 20 calls inside: cold re-entries cost 56% more than warm ones, and 84% less than no cache
```

The re-entry column is the arithmetic of the reset alone: one write at $0.045 and 49 reads at $0.0036 is $0.22, while fifty cold writes are $2.25, 25% more than the $1.80 of sending the prefix uncached. The right-hand column keeps that in proportion: once an iteration makes 20 calls, the calls after the first read warm in every cached row, so a cold re-entry costs one write per iteration, $5.67 against $3.64, and caching still saves 84% against no cache. The figure below draws both columns.

![Two bar charts of the frozen prefix's cost over 50 iterations, computed. Re-entry calls only: no cache $1.80; five-minute tier, warm, $0.22; five-minute tier, cold after about eight minutes without a read, $2.25, in red; one-hour tier $0.25. With 20 calls inside each iteration: $36.00, $3.64, $5.67 and $3.67.](diagrams/03-reset-cost.svg)

*A cold re-entry pays a write and collects no read; the one-hour tier buys it back for one write at 2x.*

The rule is therefore two-part. Order the prefix stable first, then choose the lifetime from the longest gap between reads, not from the number of iterations. Where every gap is well under five minutes the default tier is cheaper; where a step runs longer, buy the hour, or keep the entry warm: the caching documentation's pre-warm request, sent with `max_tokens: 0`, reads the prefix without generating anything, and "For the default 5-minute cache, send a new pre-warm request at least every 5 minutes to keep the cache warm". Nothing in a trace says "cache miss"; the usage block reports cache writes where reads were expected, and the bill simply arrives. Rates move; re-derive the arithmetic against the current pricing page.

---

## 5. Context bridging: the spec and the handoff

For the loop to work, everything an iteration needs must survive the reset, on disk. Two artefacts carry it, with a third the driver owns:

- **The spec** is the fixed source of truth: what to build, and the check that says each criterion holds. It is written before the loop starts and read into every fresh context.
- **The handoff file** ([post 08](../08-state-filesystem-git/index.md)) is the moving state: post 08's four fields (spec, done, next, state), plus the two this loop adds, decisions with their reasons and open questions. Each iteration rewrites it whole and reads it back, so the next fresh context can tell where it is without re-deriving the history, which git keeps.
- **The status file** holds one pass bit per criterion, written by the gate and nothing else (the next section says why).

Together the spec and the handoff are the **context bridge**. A fresh window is not starting from nothing: it reads the spec to know the goal, and the handoff, the status file and the repository to know the position. A vague spec or a thin handoff makes each iteration rediscover context and drift.

The split is stable enough that independent practitioners arrive at the same files under different names. Addy Osmani's "Long-running Agents" (28 April 2026) describes the Ralph loop with `prd.json` as the plan and `progress.txt` as the lab notes, and puts the principle plainly: "The agent itself is amnesiac, but the filesystem isn't." Anthropic's harness calls them `feature_list.json` and `claude-progress.txt`, the second a log of what each session did beside the git history (Anthropic, 2025). One file is the contract and the other the notebook; kept apart, they can carry different write permissions.

---

## 6. Who may write to the spec

This decides whether a Ralph loop converges on what was asked for, and it is easy to get wrong by being helpful.

The spec is the only thing in the system that says what "done" means. If the agent may rewrite it, an iteration that cannot satisfy a criterion has a second way out: change the criterion. Nothing about that is malicious; an agent asked to make the spec and the code agree will edit whichever is easier, and the loop ends up marking its own homework. Huntley's published prompt leans the other way, telling the agent to update the specs it finds inconsistent, which suits an author watching the stream, not an unattended run.

Anthropic's harness keeps the pass bits inside the feature list and draws a **narrow write channel** in the prompt: coding agents edit the file "only by changing the status of a passes field", with the instruction that "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality" (Anthropic, 2025). The format is a soft guardrail too: JSON (JavaScript Object Notation) was chosen because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown files". Changing one field of one record is a local, deliberate act; a Markdown spec invites fluent rewriting.

An instruction is still only an instruction. This post's driver goes one step further: the spec has no field the agent needs to write, because the pass bits live in a status file that the driver's gate rewrites after every iteration, so the spec becomes read-only to the loop and a hash of its bytes is a complete check. (Where the agent does flip the bit in the spec, as in Anthropic's design, compare the criteria with the bit removed: a hash of the whole file would fire on every honest iteration.) A side benefit is the cache: a spec whose bytes never change stays in the frozen prefix, where a flipped bit would break it at the spec. The permissions, with what enforces each:

| Artefact | Who writes | Who reads | What enforces it |
|---|---|---|---|
| Spec (`spec/feature_list.json`) | a human, between runs | every iteration and the gate | the driver hashes its bytes around each iteration and stops on `spec_moved` |
| Pass bits (`spec/status.json`) | the gate, run by the driver | the next iteration and the progress report | the driver rewrites the file after every iteration, so an edit by the agent never survives |
| Handoff file (`handoff.md`) | the loop, rewritten each iteration | the next iteration | the read-back on write and the head commit it names (post 08); a bad one costs an iteration |
| Repository source | the loop, one commit per iteration | the loop and the gate | the commit count and the gate ([post 11](../11-verification-loops/index.md)) |
| Tests | the loop may add, never edit or delete | the gate | a pre-commit hook rejecting a diff that removes an assertion ([post 13](../13-hooks-enforcement/index.md)) |

Specs do need to change: a requirement was wrong, or something turned out impossible. Route that through the handoff's open questions. An iteration that cannot satisfy a criterion writes down why and stops, a human amends the spec, and the loop restarts. The loop loses a little autonomy and keeps the property that makes the architecture trustworthy: the goalposts sit where the runner cannot reach them ([post 15](../15-human-in-the-loop/index.md)).

---

## 7. A reference design for a multi-context build

There is a documented instance of the whole design. Anthropic's long-running harness builds a clone of the claude.ai web application across many context windows (Anthropic, 2025).

An **initialiser agent** runs once, before the loop: it expands a short product prompt into a feature list of over 200 features for that build, "all initially marked as 'failing'", an `init.sh` that later sessions run to start the development server, a `claude-progress.txt` log, and an initial git commit. One feature, as the article shows it:

```json
{
    "category": "functional",
    "description": "New chat button creates a fresh conversation",
    "steps": [
      "Navigate to main interface",
      "Click the 'New Chat' button",
      "Verify a new conversation is created",
      "Check that chat area shows welcome state",
      "Verify conversation appears in sidebar"
    ],
    "passes": false
  }
```

Every later **coding-agent** session runs the same re-entry ritual: check the working directory, read the git log and the progress file, pick the highest-priority feature not yet done, start the server and run a basic end-to-end test before touching it, build only that feature, commit with a descriptive message, and write a progress update. Then the context is discarded and the next session starts the ritual over.

Two things in that design are easy to skim past. The decomposition is paid **once**, outside the loop, which keeps the re-entry tax small. And the spec is machine-readable, which turns "is it done?" into a count the driver can log every iteration: features passing over features total.

### The gate under the staircase has to be end to end

The count is only as honest as the gate beneath it, and this is where the reference design paid for its experience. Absent explicit prompting, the agent would make code changes and test them "with unit tests or `curl` commands against a development server", yet fail to recognise that the feature did not work end to end; prompted to use browser automation and test as a human user would, it "mostly did well" (Anthropic, 2025). Mostly: the article notes it cannot see browser-native alert modals through its automation server, and features relying on them stayed buggier.

The consequence is specific to this architecture. In a single session, a feature that passes its unit tests and does not work is caught by whoever is watching. In a Ralph loop nobody is watching: the bit flips, the commit lands, the count steps up, and the next fresh context reads a progress file that says the feature is done. Fifty iterations later a rising progress curve sits over a product that does not run: victory declaration ([post 05](../05-agent-failure-modes/index.md)) laundered through fifty commits. Whatever the gate is, on this architecture it has to exercise the feature the way the user will.

---

## 8. Convergence, stopping, and the guards that enforce it

A loop that resets forever needs a clear answer to "when is it done?", and the spec provides it: every criterion's check passes. What matters is *who says so*. Convergence is measured by running the checks, never by reading the agent's account of its work.

Three ways the loop fails need guarding, and all three become cheap once each iteration commits. It might **never converge**, so it carries exit (2), the iteration cap `max_iters`, and exit (4), no progress, from [post 03](../03-the-agent-loop/index.md). Here "no progress" has a definition already on disk: no new commit, because the version history is the progress record and the transcript was thrown away at the last reset. It might **thrash**, redoing or undoing work, which the same discipline makes visible: a thrashing loop's commits alternate rather than accumulate, and a diff against the commit two back says so. And it might **move the goalposts**, which is checked by hashing the spec before the iteration and again after it.

All three fit in a short driver. In `snippets/ralph_driver.py` the agent is a new process each iteration, so no state can leak across the reset even by accident, and the driver's own state is what it reads from git and the spec:

```python
def commits(repo):
    return int(git(repo, "rev-list", "--count", "HEAD"))


def spec_hash(repo):
    return hashlib.sha256((repo / SPEC).read_bytes()).hexdigest()


def gate(repo):
    """The acceptance gate: run every criterion's check in a fresh interpreter, and write the pass bits."""
    spec = json.loads((repo / SPEC).read_text(encoding="utf-8"))
    status = {f["id"]: subprocess.run([sys.executable, "-B", "-c", f["check"]], cwd=repo,
                                      capture_output=True).returncode == 0
              for f in spec["features"]}
    (repo / STATUS).write_text(json.dumps(status) + "\n", encoding="utf-8")
    return status


def ralph(repo, run_agent, *, max_iters=50, stale_cap=3, log=print):
    stale = 0
    for i in range(1, max_iters + 1):
        goalposts, before = spec_hash(repo), commits(repo)
        report = run_agent(repo)                      # a new process: the fresh context
        if spec_hash(repo) != goalposts:
            return i, "spec_moved"                    # the agent changed what done means
        status = gate(repo)                           # the driver runs the checks; the report is not read
        new = commits(repo) - before
        log(i, report, new, status)
        if all(status.values()):
            return i, "completed"                     # exit (1), decided by the gate
        stale = 0 if new else stale + 1
        if stale >= stale_cap:
            return i, "no_progress"                   # exit (4), on commits
    return max_iters, "max_iters"                     # exit (2)
```

`spec_moved` is a return value, not an exception: a legitimate outcome that needs a person, turning a quiet correctness problem into a loud one, as a deterministic hook does ([post 13](../13-hooks-enforcement/index.md)). The snippet runs it on a three-criterion spec (`add`, `sub`, `mul` in a small module) in a temporary git repository, with a deterministic stand-in for the model that does the first failing criterion each iteration, commits, and rewrites `handoff.md`; its first attempt at `sub` is wrong, and it says it is done anyway:

```text
an honest agent, one wrong claim on the way (mode honest, max_iters=50):
   1  claims add done            +1 commit  rev-list 2  handoff done: add           gate: add pass, sub fail, mul fail
   2  claims sub done            +1 commit  rev-list 3  handoff done: add, sub      gate: add pass, sub fail, mul fail
   3  claims sub done            +1 commit  rev-list 4  handoff done: add, sub      gate: add pass, sub pass, mul fail
   4  claims mul done            +1 commit  rev-list 5  handoff done: add, sub, mul gate: add pass, sub pass, mul pass
  stopped after iteration 4: exit (1), completed
```

Iteration 2 is victory declaration in miniature: the handoff says `sub` is done, the commit landed, and the gate says it fails, so iteration 3 picks `sub` again. One commit per iteration is checked with `git rev-list --count HEAD`, two through five. The other three runs stop on the other guards. An agent that cannot do `mul` and rewrites its check to `assert True` stops at iteration 4 on `spec_moved`, and the snippet then shows what the guard prevented: the gate run on the moved spec would pass 3 of 3. One that cannot do `mul` and commits nothing stops at iteration 6 on exit (4), after three rounds without a commit. The honest agent under `max_iters=3` stops on exit (2) with `mul` undone.

![Two computed charts of the honest run. Above, tokens in the window: each of four fresh windows rises from its re-entry context, 236, 315, 338 and 345 tokens, to its end, 307, 401, 423 and 449, above the 208-token frozen prefix, while one context carrying every iteration would have grown to 956. Below, two staircases: commits rise by one every iteration, from 2 to 5, while criteria passing go 1, 1, 2, 3, flat at iteration 2 where the claim failed the gate.](diagrams/04-multi-context-run.svg)

*Commits rise every iteration; criteria passing rise only when the gate agrees.*

The figure above draws that run. Context use is a **sawtooth**: each window starts again from the frozen prefix plus a volatile part that grows slowly with the history (a bounded read such as the `git log --oneline -20` of Anthropic's sessions caps it), while one context carrying everything only climbs. One tooth of that sawtooth is [animated in post 09](../09-context-management-loop/diagrams/05-context-reset.svg): the window fills, clears on one frame, and only the handoff file crosses. Progress is a **staircase** on disk. The two staircases part at iteration 2, which is why the driver counts the gate's passes, not the commits. The sizes are the toy's; the shape is the lesson.

The same shape, with a planner, a ratchet, cost metering and tracing wired in, runs in the capstone: [`code/26-coding-agent/src/coding_agent/driver.py`](../../code/26-coding-agent/src/coding_agent/driver.py) gives each task a fresh context, keeps its commits in memory, and stops on `spec_complete`, `task_failed` or `budget`. Its spec is a Python object the generator has no way to write, so it needs no `spec_moved` guard.

---

## 9. After convergence: who reviews fifty commits

The loop stopping is not the work finishing. A converged Ralph run hands a person a body of work built over hours without supervision, and somebody has to accept it. Osmani names the problem plainly: "Auditing 24 hours of autonomous activity is a real human-time problem" (Osmani, 2026). It is the price of the autonomy, and it appears nowhere in the token bill.

What makes it tractable is the shape the loop already produces. One commit per verifiable increment, each tied to the criterion it satisfies, is a review *series* rather than a review *endpoint*. A reviewer can walk it in the order it was built, stop at the first commit that looks wrong, and know that everything before it cleared the same gate. One enormous diff offers no such place to stop.

This gives the sizing rule a second, independent justification. A slice is not only the unit the window can hold and the gate can judge; it is also the unit a person can review in one sitting, and a slice too large to review is too large, whatever the window says. It also moves the human-in-the-loop question ([post 15](../15-human-in-the-loop/index.md)) from "which actions need approval" to "what shape must the finished work arrive in", decided before the loop starts.

---

## 10. Where this overlaps planner and evaluator

The three roles of [post 12](../12-planner-generator-evaluator/index.md) fit inside one Ralph iteration: a planner picks which criterion is next from the spec and the current state, a generator does it, and an evaluator checks whether it holds. The reset keeps those roles cheap, because each runs in a clean window, and the separation keeps the evaluator honest, because an evaluator that never saw the generator's reasoning cannot be talked round by it. Anthropic's November 2025 harness had no evaluator role, and its own closing section leaves open whether specialised agents would do better; its March 2026 successor added one (Anthropic, 2026), and post 12 is that design.

The Ralph loop is then the outer loop and the three roles the inner one, the composition [post 19](../19-loop-engineering/index.md) is about: designing the loop that drives the agent rather than prompting each step. Both loops meet in [post 26](../26-capstone-coding-agent/index.md), where this driver's shape runs the build.

---

## 11. Make it run

The plan's exercise for this post is to run the Ralph driver on a three-task spec with a mock model, confirm one commit per iteration, and let the acceptance gate rather than the agent's report decide convergence. Both snippets run offline from the series root:

```bash
uv run python posts/18-long-horizon-ralph/snippets/ralph_driver.py
uv run python posts/18-long-horizon-ralph/snippets/reset_cost.py
```

`ralph_driver.py` needs `git` on the path and `tiktoken` from the root environment, builds each repository under the system temporary directory and removes it afterwards, and takes about twenty seconds. It prints the four runs of the previous sections and then the window sizes of the honest one:

```text
windows, honest run (tokens: frozen prefix + volatile re-entry -> end of iteration):
   1  208 + 28 = 236 -> 307
   2  208 + 107 = 315 -> 401
   3  208 + 130 = 338 -> 423
   4  208 + 137 = 345 -> 449
frozen prefix byte-identical in every iteration: True (208 tokens)
largest Ralph window: 449 tokens; one context carrying all 4 iterations: 956 tokens
```

The counts are `tiktoken` `cl100k_base` counts of the toy's own text, an OpenAI tokenizer standing in for the provider's. `reset_cost.py` is pure arithmetic and prints the table of the cache section.

---

## 12. What can go wrong?

These are the mistakes that applying this post's ideas actually produces.

- **Convergence read from the agent.** The driver stops when the progress file or the pass bits the agent wrote say every criterion is done; the run ends early, green, over a feature that fails its check.
- **A cache lifetime chosen from the iteration count.** The default five-minute tier with an eight-minute end-to-end gate between iterations; the usage figures show a cache write on every re-entry, and the re-entry calls cost more than with caching off.
- **A whole-file hash on a spec the agent writes to.** The pass bit lives in the spec, so the hash changes on every honest iteration and the loop stops on its first success, every time.
- **A stale counter on activity rather than commits.** The detector watches tool calls or transcript length, which a stuck agent keeps varying; the loop burns iterations until the cap, with the head commit unchanged.
- **A unit-test gate on a user-facing build.** Every criterion turns green, every commit lands, and the first person to open the application finds the feature does not work end to end.

---

## Common pitfalls

1. **Slicing iterations by feel.** Too large overflows the window; too small pays the uncacheable half of the re-entry tax over and over. Size to one verifiable increment.
2. **Keeping state in the window.** Anything not written to disk is lost at the reset; the spec, the handoff, the status file and the repository are the memory.
3. **Letting the agent edit what "done" means.** A loop that can rewrite its criteria will satisfy them by rewriting them. Keep the spec human-owned and the pass bits the gate's.
4. **Putting the volatile above the frozen.** A handoff or a status file placed before the spec breaks the cached prefix on every reset.
5. **No guards.** Without a gate the driver runs, an iteration cap and a stale-commit count, the loop runs until the budget does.

---

## Further reading

- Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'" (14 July 2025): the plain loop against a spec with one task per loop, its one-line form, and the relayed contract report.
- Anthropic Engineering, Justin Young, "Effective harnesses for long-running agents" (26 November 2025): the initialiser and coding-agent split, the feature list with its `passes` field, the progress file, and the end-to-end verification finding.
- Addy Osmani, "Long-running Agents" (28 April 2026): the plan-file and progress-file split, and the human cost of auditing a long autonomous run.
- Kwa et al., "Measuring AI Ability to Complete Long Software Tasks" (METR, March 2025; arXiv:2503.14499): the doubling time of the task length a frontier model completes at 50% reliability.
- Anthropic, "Prompt caching" and "Pricing" (Claude Platform documentation, consulted October 2026): the read and write multipliers, the two lifetimes, the clock measured from the start of a request, and the pre-warm request.
- Prithvi Rajasekaran, "Harness design for long-running application development" (Anthropic Engineering, 24 March 2026): the successor design with an evaluator, and Opus 4.5 largely removing context anxiety.
- ai-boost, awesome-harness-engineering (GitHub, 2026): the Agent Loop and Memory and State primitives.
- `ctx-005` ("The economics of context: pricing, caching, and latency"): the cached stable prefix at the level of one call, the token-side companion to this run-level view.

Full citations are in [REFERENCES.md](../../REFERENCES.md).

---

## What to read next

- **[Post 19 - Loop engineering: designing the loop that prompts the agent](../19-loop-engineering/index.md):** the Ralph loop as the outer loop of a composition, with layered exits and a budget across both loops.
- **[Post 23 - The economics of a harness and Harness-as-a-Service](../23-economics-haas/index.md):** the cache clock and the reset priced across a whole run, and what a long-horizon run costs on a session-metered runtime.
