"""Post 22: one illustrative week through the staged production funnel, priced per merged pull request.

Run from the series root:  uv run python posts/22-evaluating-harnesses/snippets/funnel.py

Every input is illustrative: 200 runs a week per harness, the accepted and reverted counts, the model spend per
run, and the human time, priced at a loaded $120 an hour (15 minutes to review an accepted result, 5 to triage a
rejected one, 45 to redo one that was reverted). Faros AI's "dollars per merged PR" counts AI fees only; the ledger
below adds the human time, which is where the two harnesses part. The last line re-prices B with A's escape rate.
"""
HOURLY = 120.0
MINUTES = {"review": 15, "triage": 5, "redo": 45}

WEEK = {  # runs attempted, accepted without rework, later reverted, model spend per run
    "A": dict(runs=200, accepted=118, reverted=9, per_run=0.85),
    "B (heavier verification)": dict(runs=200, accepted=132, reverted=14, per_run=2.55),
}


def ledger(runs, accepted, reverted, per_run):
    minutes = (accepted * MINUTES["review"] + (runs - accepted) * MINUTES["triage"]
               + reverted * MINUTES["redo"])
    model, human = runs * per_run, minutes / 60 * HOURLY
    shipped = accepted - reverted
    return {"first_pass": accepted / runs, "escape": reverted / accepted, "shipped": shipped,
            "model": model, "human": human, "per_merged": (model + human) / shipped}


def main():
    out = {}
    for name, week in WEEK.items():
        r = out[name] = ledger(**week)
        print(f"{name}: first-pass {r['first_pass']:.0%}, escape {r['escape']:.1%}, shipped {r['shipped']}, "
              f"model ${r['model']:,.0f}, human ${r['human']:,.0f}, per merged PR ${r['per_merged']:.2f}")
    a, b = out["A"], out["B (heavier verification)"]
    print(f"B against A per merged PR: {b['per_merged'] / a['per_merged'] - 1:+.1%}")
    extra = (b["model"] + b["human"] - a["model"] - a["human"]) / (b["shipped"] - a["shipped"])
    print(f"B's {b['shipped'] - a['shipped']} extra merges: ${extra:.2f} each")
    b_held = WEEK["B (heavier verification)"]
    reverted = round(b_held["accepted"] * a["escape"])
    held = ledger(b_held["runs"], b_held["accepted"], reverted, b_held["per_run"])
    print(f"B at A's escape rate ({reverted} reverts): per merged PR ${held['per_merged']:.2f}")
    out["held"] = held
    return out


if __name__ == "__main__":
    main()
