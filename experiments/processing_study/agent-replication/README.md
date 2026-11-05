# AICC study: replication assignment for other AI agents

Prepared 5 November 2026 by Codex for the AICC project owner. This packet describes the completed local engineering study and assigns a reproducible evaluation to other AI agents. No external agent has run this assignment merely because the packet is published.

Repository: <https://github.com/izikon78/AICC>. The study implementation and original measurements are frozen at commit `75de32b757b8bdc43886213ee6b9dd9470717918`. The packet adds documentation; it does not revise those measurements or the measured Python sources. The work is on `research/processing-and-learning-study` in draft PR #2, dependent on the research-archive PR #1; it may not yet be on `main`.

## Give this to an agent

Share [AGENT_PROMPT.md](AGENT_PROMPT.md), or the link to this directory. Ask the agent to execute the assignment and return its report and raw artifacts. Access to a GitHub link alone does not imply that the agent can execute Python; an agent without an execution environment must return an explicitly labeled evidence review.

| File | Purpose |
|---|---|
| [Agent prompt](AGENT_PROMPT.md) | Complete assignment to copy into another AI chat |
| [Protocol](PROTOCOL.md) | Exact original design, commands, replication tracks, and next experiments |
| [Measurements](MEASUREMENTS.md) | Definitions, attribution, savings formulas, and required submission artifacts |
| [Recorded results](RECORDED_RESULTS.md) | Measurements already obtained, including unfavorable findings |
| [Test inventory](TEST_INVENTORY.md) | The 44 automated test methods in the frozen implementation |
| [Submission template](submission-template.json) | Machine-readable report structure; empty fields are not measurements |

The original [study README](../README.md), [kernel contract](../KERNEL_CONTRACT.md), [runtime contract](../RUNTIME_CONTRACT.md), [optimization record](../OPTIMIZATION_LOG.md), and [full interpretation](../results/full-2026-11-05/ANALYSIS.md) remain authoritative context. The independent authoring/lifecycle trial described in the [separate pilot protocol](../../lifecycle-pilot/PROTOCOL.md) has not been completed by this study.

## Requested outcome

Each agent should first audit and reproduce the frozen experiment, then state whether its own measurements support, contradict, or cannot resolve each claim. Report execution speed and memory separately from AI authoring effort, model billing, and financial savings. A result that disproves an expected benefit is useful evidence and must be retained.

Do not change the existing `results/full-2026-11-05/` directory. Store new reports under a unique run directory and return a new branch/patch if repository write access is available. Uploading results is separate from merging them.
