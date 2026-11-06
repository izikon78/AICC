# Continue AICC/AIN on the RTX 3080 computer

Prepared 6 November 2026. This is a substantive handoff summary, **not a verbatim
chat export or a claim that a Codex chat was imported to another device**.

Concept, architecture and research direction: **Izik Bachar**. Experiment,
documentation and review assistance: Codex and same-session collaboration agents;
earlier Claude/Grok contributions retain their original credits and provenance.

## Repository state to open

- Repository: https://github.com/izikon78/AICC
- Branch: **`research/ain-fluency-current-agents`**
- Review: https://github.com/izikon78/AICC/pull/6
- Last completed study/results commit before this handoff: `d3962e0c4699fc693c53a422670f682a965368be`.
- Clone the branch tip to include this handoff, then record `git rev-parse HEAD`.
  The complete latest study is on this branch, not `main`.

This branch stacks on the native-hypothesis reassessment and earlier research.
Keep historical reports and raw results intact. Do not merge or overwrite main
as an incidental part of moving computers. Create a new branch for new work.

## What the user actually wants to test next

Compare **two complete agent workflows** starting from matched copies of an
accessible model. One uses conventional programming/tool interactions; the other
learns AIN before evaluation and uses it for observable working records, memory,
actions, tool interactions and executable artifacts. This is broader than asking
an unchanged general-purpose agent to print a different final code format.

Human-readable code is an optional projection. Syntax/stable identifiers can be
rendered deterministically; useful descriptive names and explanations may need
metadata or additional inference. Count requested rendering and boundary
translations at their actual frequency. New requirements and literal business
data still need representation; they are not free information inside an opcode.

The native condition has no recurring fixed-language manual at evaluation.
Fine-tuning a pretrained model is an adaptation test, distinct from training a
model exclusively on AIN from scratch. Neither AIN-only output nor agent records
prove that every hidden neural computation uses a symbolic language. An exact
closed commercial-model clone is not required for a bounded mechanism test.

The broad question is whether learned machine-oriented representations reduce
correct-work resources versus conventional source. If learned AIN and readable
IR both beat Python, that supports the shared mechanism even if AIN ties IR.
An AIN-specific advantage is a separate claim. Current numeric AIN is a mechanical
spelling of the existing typed IR; do not invent a distinct architecture for it.

AICC (AI Computational Commons) is a separate potential lifecycle/reuse benefit.
Keep library/capability access equal in the first language/agent comparison.

## Destination hardware and first action

The user confirmed **RTX 3080, 10 GB dedicated GPU memory, 32 GB system RAM**.
Verify these on the destination host. The source computer reported a GTX 1660 Ti
with 6 GB; running there or in a cloud environment would not use the other PC's
3080. In the desktop app select Codex and **This computer / Local** on the 3080 PC.

Begin with hardware/software inspection, an isolated training environment and a
tiny memory-fit, throughput and AIN-learning feasibility gate. A roughly 1B
parameter open model with memory-efficient adaptation and short contexts was a
proposed starting point, not a selected checkpoint or a verified fit. Train
matched versions sequentially on the same GPU. Check model license, tokenizer,
training compatibility, precision and actual peak memory before choosing settings.

No AIN model has been trained, downloaded or benchmarked by this chat. The source
machine's Python environment did not have PyTorch/Transformers installed when
inspected; do not assume the destination's dependencies or capabilities.

## Planning estimates, not agreed spending limits

The discussion proposed a small two-agent pilot with a few bounded task families:

- Roughly 3–5 working days for implementation/data/checks, with uncertainty.
- Roughly 6–18M training-token presentations; central illustration:
  `2,000 episodes * 750 tokens * 3 passes * 2 agents = 9M`.
- Roughly 300k–1M evaluation tokens; central illustration:
  `50 tasks * 2 agents * 5 calls * (1,000 input + 200 output) = 600k`.
- A proposed 500k development-assistant token cap was discussed but **not accepted
  as a binding budget**. Teacher-generated trajectories could add substantial
  inference usage; prefer executable synthetic generation where appropriate.

Training-token presentations are repeated local training exposures, not ChatGPT
token charges. Count conversation history/tool responses every time they are
processed. Training duration remains unmeasured; benchmark throughput before
projecting hours. Do not treat these estimates as a purchased GPU/API budget,
permission for unbounded training, or evidence of achievable savings. Freeze the
model, data splits, hardware-hour limits and stop rules before a substantial run.

## What the completed experiment established

Read [the results overview](../../experiments/ain_fluency/RESULTS_OVERVIEW.md).
The current-agent controller experiment had three representations, two variants
and build/change/repair stages: 18 scored submissions plus 18 preparation calls.
All 18 artifacts passed preparation/fluency gates and all 55 execution cases.

There were 38 requests: 36 metered responses and two empty account-quota
rejections. The original stopped dataset and an operational v1.1 continuation
are preserved. Copied earlier records in the continuation are the same
observations, not an independent replication. Do not silently count them twice.

Genuine chains are 5/6, with numeric AIN 1/2. The excluded AIN handoff is a **fault
injector limitation**, not a wrong program: the correct predecessor reused two
registers, and static name matching confused their later roles. Its canonical
fallback repair passed. Do not call this 50% AIN accuracy.

No cost saving was established. Two quota requests have unknown counters, so the
primary all-attempt AIN cost is undefined. Under hypothetical cache-neutral input
1/output 5 weights, the known subtotal permits **at most 0.4% saving versus IR**,
and is already **25.3% above Python**. These are bounds under illustrative weights,
not point savings estimates, provider prices or proof about native training.
The pre-run neutral prediction was 0% versus IR; optimistic 10–20% scenarios were
explicitly conditional assumptions and were not supported by that run.

The experiment used an unchanged signed-in current model with supplied context;
it did not evaluate the whole learned-agent workflow now requested. Its 851,015
known input/output tokens include substantial CLI/context overhead and are not a
prediction for a lean locally hosted training/evaluation runner.

## Read next

1. [Canonical native hypotheses](../ain/NATIVE_HYPOTHESES.md).
2. [Draft trained-native protocol](../ain/TRAINED_NATIVE_PILOT_PROTOCOL.md).
3. [Feasibility review and primary sources](../research/NATIVE_AIN_FEASIBILITY_2026-11-05.md).
4. [Completed controller study overview](../../experiments/ain_fluency/RESULTS_OVERVIEW.md).
5. [Current-agent replication brief](../../experiments/ain_fluency/AGENT_REPLICATION_BRIEF.md).
6. [Article Draft 9](../article/AICC_Article_Draft_9.md): preserve the title,
   "It started with a beep" section and Izik's requested origin paragraph.
7. [Original reconstructed handoff](AICC_Codex_Conversation_Handoff.md) for older
   architecture, examples and history. It is dated background, not proof or a
   substitute for later user clarifications and authorizations.

The trained-native protocol is still a draft. Extend it for observable whole-agent
traces, agent tools and memory rather than merely rerunning the prompted-code
pilot. Measure resources per correctly completed unseen task, with all failed
attempts, repairs, adapters, optional rendering and amortized learning included.
Keep strong compact-Python/IR controls and equal capabilities.

## What does and does not move between computers

Cloning transfers tracked research, code, article files, raw results and Git
history. It does not transfer the verbatim chat, a running model/session, local
environments, ignored scratch directories, account sign-ins or GPU dependencies.
Recreate the environment on the destination and sign in normally.

An old GitHub personal access token was pasted into the original chat. It is
excluded from this handoff and must not be recovered, copied or reused. Revoke it
if that has not already been done. Use normal GitHub browser authentication;
do not copy authentication files or the whole `.codex` directory between PCs.

Official app instructions: [Codex local environments/modes](https://learn.chatgpt.com/docs/environments/modes)
and [desktop quickstart](https://learn.chatgpt.com/docs/quickstart?setup=app).
Codex's checkout/worktree Handoff feature is not a claim of cross-PC chat import.
