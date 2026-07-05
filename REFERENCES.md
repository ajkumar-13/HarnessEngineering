# References

Master bibliography for the *Harness Engineering* series, grouped by post. Where a source is referenced from multiple posts, it is listed once — under the first post that cites it — and later posts cross-link to that entry. URLs are given where a stable canonical URL exists; living vendor docs cite the documentation root.

> Citation style: author(s) or org, title, venue or publisher, year. A one-line note explains which point the source supports where that is not obvious. Sources shared with the *Context Engineering* series are marked **[CE]** and cite that series' `REFERENCES.md` for the full entry.

---

## Post 01 — From context to harness

- **Osmani, A.** "Agent Harness Engineering." *Personal blog*, April 2026. https://addyosmani.com/blog/agent-harness-engineering/ — source of `Agent = Model + Harness`, the ratchet principle, and the co-training flywheel.
- **OpenAI.** "Harness engineering: leveraging Codex in an agent-first world." *OpenAI blog*, 2026. https://openai.com/index/harness-engineering/ — the term used as a first-class discipline by a model provider.
- **Faros AI.** "Harness Engineering: Making AI Coding Agents Work in 2026." *Faros AI blog*, 2026. https://www.faros.ai/blog/harness-engineering — the three-era framing (phrasing → information → autonomy); the LangChain Terminal-Bench #30→#5 result.
- **Hugging Face.** "Harness, Scaffold, and the AI Agent Terms Worth Getting Right." *Hugging Face blog*, 2026. https://huggingface.co/blog/agent-glossary — the model / scaffold / harness / orchestration vocabulary.
- **Anthropic.** "Building Effective Agents." *Anthropic Engineering*, December 2024. https://www.anthropic.com/engineering/building-effective-agents — workflow-vs-agent distinction; the model-plus-loop framing.
- **Anthropic.** "Claude Agent SDK" / "Claude Code" documentation, 2025–26. https://docs.anthropic.com/ — the SDK described as "the agent harness that powers Claude Code."
- **Karpathy, A.** on context engineering, *X (Twitter)*, June 2025. **[CE]** — the era-2 rename this series builds on.

## Post 02 — The anatomy of a harness

- **ai-boost.** "awesome-harness-engineering." *GitHub*, 2026. https://github.com/ai-boost/awesome-harness-engineering — the component taxonomy (loop, tools, context, skills/MCP, permissions, memory, orchestration, verification, observability, HITL).
- **Databricks.** "What is an AI Agent Harness?" *Databricks blog*, 2026. https://www.databricks.com/blog/ai-harness — prebuilt vs custom harness layers.
- **O'Reilly Radar.** "Agent Harness Engineering." *O'Reilly*, 2026. https://www.oreilly.com/radar/agent-harness-engineering/ — the harness as an operating system around the model.
- Osmani, "Agent Harness Engineering" — see Post 01 (the layered Claude Code breakdown).

## Post 03 — The agent loop

- **Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., Cao, Y.** "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR 2023* (arXiv:2210.03629, 2022). https://arxiv.org/abs/2210.03629 — the reason→act→observe loop.
- Anthropic, "Building Effective Agents" — see Post 01.

## Post 04 — Why the harness beats the model

- **MindStudio.** "What Is Harness Engineering? Why Your Agent Wrapper Drives More Performance Than the Model." *MindStudio blog*, 2026. https://www.mindstudio.ai/blog/what-is-harness-engineering — reported ~6× same-model performance spread; enterprise throughput figures.
- **HumanLayer.** The "skill issue" framing (agent failures as configuration, not weights), 2026. — cited via Osmani, Post 01.
- Faros AI, "Harness Engineering" — see Post 01 (the Terminal-Bench leaderboard movement).

## Post 05 — Agent failure modes

- **Fowler, M.** "Humans and Agents in Software Engineering Loops." *martinfowler.com*, 2026. https://martinfowler.com/articles/exploring-gen-ai/humans-and-agents.html — human/agent loop dynamics and failure handling.
- **Breunig, D.** "How Long Contexts Fail." *Personal blog*, June 2025. **[CE]** — the context-failure taxonomy this post's runtime failures build on.
- Faros AI, "Harness Engineering" — see Post 01 (victory declaration, context anxiety, one-shotting).

## Post 18 — Long-horizon & multi-context execution

- **Huntley, G.** The "Ralph" technique (running a coding agent in a plain loop against a spec, fresh context each iteration), *Personal blog*, early 2026.
- **Anthropic.** Long-running agent harness for multi-context software development, November 2025. — planner/generator/evaluator roles; handoff artefacts; parallel instances claiming tasks via files.

## Post 19 — Loop engineering

- **Osmani, A.** "Loop engineering" (stop prompting the agent; design the loop that prompts it), June 2026. — see Post 01 entry for the blog.
- **tosea.ai.** "What Is Loop Engineering? A Complete Guide from Prompt to Harness Engineering (2026)." https://tosea.ai/blog/loop-engineering-ai-agents-complete-guide-2026 — the layered-exit taxonomy.
- **Greyling, C.** "Loop Engineering." *Medium*, June 2026. https://cobusgreyling.medium.com/loop-engineering-62926dd6991c

## Post 22 — Evaluating harnesses

- **Terminal-Bench.** Agentic terminal-task benchmark, 2025–26. — harness A/B on trajectories.
- **Jimenez, C., Yang, J., et al.** "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" *ICLR 2024* (arXiv:2310.06770). https://arxiv.org/abs/2310.06770

## Post 16 — Multi-agent orchestration

- **Cognition.** "Don't Build Multi-Agents." *Cognition blog*, 2025. — the steelman for single-agent defaults. **[CE]**

---

*This bibliography grows as posts are drafted. Each post's "Further reading" names its sources and points here.*
