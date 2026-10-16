"""Post 23: what a hosted agent runtime adds to the token bill, and where renting stops being cheaper than owning.

Run from the series root:  uv run python posts/23-economics-haas/snippets/rent_or_build.py

Runtime rates as the vendors' pages stated them when consulted in October 2026:
  Claude Managed Agents (Anthropic, "Pricing"): $0.08 per session-hour, accruing only while the session's status is
    `running`; tokens are billed on top at the standard rates.
  Amazon Bedrock AgentCore Runtime (AWS, "Amazon Bedrock AgentCore pricing"), v2 consumption rates: $0.1276
    per vCPU-hour and $0.0169 per GB-hour, billed per second; CPU is not billed during I/O wait ("waiting for
    LLM responses, tool / API calls, or database queries"); the page prices no model inference, which the
    agent's model service bills.
The runs are illustrative: the running example's 36 seconds (24 s waiting on the model, 12 s running tools
inside the microVM, so CPU is counted for the tool time only), and a long-horizon run of eight hours with the same one-third CPU share, at one
vCPU and 2 GB. The owned cost of $30,000 a month is a placeholder. Standard library only.
"""
SESSION_HOUR = 0.08                       # Claude Managed Agents, dollars per running session-hour
VCPU_HOUR, GB_HOUR = 0.1276, 0.0169       # AgentCore Runtime consumption rates, dollars
VCPU, GB, CPU_SHARE = 1, 2, 1 / 3         # illustrative sizing; CPU busy only during tool time
OWNED_MONTHLY = 30_000                    # placeholder: the people who would own the harness


def session_metered(seconds):
    return seconds / 3600 * SESSION_HOUR


def resource_metered(seconds, cpu_share=CPU_SHARE):
    hours = seconds / 3600
    return hours * cpu_share * VCPU * VCPU_HOUR + hours * GB * GB_HOUR


def crossover(rented_per_run, own_per_run=0.0):
    """Monthly runs at which a fixed owned cost equals the rented margin."""
    return OWNED_MONTHLY / (rented_per_run - own_per_run)


def main():
    token_bill = 0.3293   # the running example on a rolling breakpoint, from run_meter.py
    for label, seconds in (("36-second run", 36), ("eight-hour run", 8 * 3600)):
        s, r = session_metered(seconds), resource_metered(seconds)
        print(f"{label}: session-metered ${s:.4f}, resource-metered ${r:.4f}", end="")
        print(f" ({s / token_bill:.2%} of the short run's ${token_bill} token bill)" if seconds == 36 else "")
    print(f"eight hours with the CPU busy throughout: ${resource_metered(8 * 3600, cpu_share=1):.2f}")
    quarter = session_metered(15 * 60)
    print(f"a fifteen-minute session: ${quarter:.2f} of runtime; crossover at ${OWNED_MONTHLY:,} a month: "
          f"{crossover(quarter):,.0f} runs a month")
    long_run = session_metered(8 * 3600)
    print(f"for eight-hour sessions at ${long_run:.2f} each the crossover falls to {crossover(long_run):,.0f} "
          f"runs a month")
    assert round(session_metered(36), 4) == 0.0008 and round(quarter, 2) == 0.02
    assert round(crossover(quarter)) == 1_500_000


if __name__ == "__main__":
    main()
