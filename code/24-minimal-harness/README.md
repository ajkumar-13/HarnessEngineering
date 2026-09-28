# Build #1 — a minimal agent harness

Companion code for **Harness Engineering, Post 24 — "Build #1: a minimal agent harness from scratch."**

A real, useful harness is small once you have internalised Parts I to IV. This one is four primitives wired together:

| Primitive | Module | From |
|-----------|--------|------|
| The loop (reason → act → observe) | `harness.py` | Post 03 |
| A schema-validated tool registry + deny-listed bash | `tools.py` | Post 06 |
| A verification gate ("done" means "verified") | `verify.py` | Post 11 |
| Layered exits (completed / max-iters / budget / no-progress) | `harness.py` | Posts 03, 19 |

The whole thing is **offline by design**: drive it with a `ScriptedModel` and an injected tool runner and no network or API key is touched. Swap in `AnthropicModel()` and `subprocess_runner` to make it live.

## The idea

A bare loop exits when the model *says* it is done. That is a victory declaration waiting to happen (Post 05). Build #1's loop never exits on a final answer alone: a candidate answer goes through the **verification gate** first. If the gate passes, the run stops as `verified`. If it fails, the failure report is fed back into the loop as the next observation and the agent tries again — success is silent, failures are verbose (Post 11).

```
model → final answer? ──no──> run tools → observe → loop
             │yes
             ▼
        verification gate ──pass──> DONE (verified)
             │fail
             ▼
   inject the report, keep looping
```

## Run it

```bash
# offline demo — the agent writes a buggy function, the gate rejects it,
# the agent fixes it, and only then does the run stop as verified
python -m minimal_harness            # (add src to PYTHONPATH, or `pip install -e .`)

# tests — the gate and every stop condition, no API key
python -m pytest -q                  # 10 passed
```

## What was deliberately left out

Build #1 is the honest minimum. It has no hooks, no real sandbox, no sub-agents, no human approval gate, and no observability. The verifier execs candidate code in-process, which is exactly the blast radius that **Build #2 (Post 25)** sandboxes. Those four hardening layers are what turn a minimal harness into one you would trust.

MIT-licensed, like all code in this series.
