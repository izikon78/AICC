# Assignment: independently evaluate the AICC processing study

You are evaluating the AICC project's measured event-processing and neural plan-selection experiment. Your task is to test the claims and produce your own results, including failures and negative findings. Do not aim to confirm the theory.

Repository: https://github.com/izikon78/AICC

Packet: `experiments/processing_study/agent-replication/`

Branch containing the implementation and packet: `research/processing-and-learning-study`.

Frozen measured implementation commit: `75de32b757b8bdc43886213ee6b9dd9470717918`. Verify its eleven recorded Python source hashes before describing a run as an unchanged-source replication.

## Required work

1. Read the packet's README, PROTOCOL, MEASUREMENTS, RECORDED_RESULTS, and TEST_INVENTORY, together with the kernel/runtime contracts. Declare your provider/model/version if known, execution environment, and any limitations. If you can only read files, submit an `evidence_review_only`; never invent timings or imply you executed tests.
2. Check provenance and artifact hashes. Run the 44 unit tests and capture actual output and exit status. Examine the original raw measurements before accepting any summary. Flag disagreements between claims and evidence.
3. If execution is available, perform Track A (local recalibration/retraining) or Track B (frozen model/policy remeasurement) exactly as specified in PROTOCOL. Identify which you chose. Use new output directories. Keep five comparison modes, matched inputs, randomized sequential fresh-process workers, and explicit time/memory boundaries. Run the separate granularity microbenchmark and report the nine runtime-state checks. Do not run multiple benchmark workers concurrently.
4. Produce `AGENT_REPORT.md`, a completed copy of `submission-template.json`, raw logs/results, and file checksums. Compare your local ordinary and AICC paths on the same machine; do not infer causality by comparing one agent's computer with another's. Use the formulas and required tables in MEASUREMENTS. Preserve all failed runs and explain exclusions.
5. Only after freezing the replication result, optionally propose a separate improved implementation. Describe the behavioral contract, change, hypothesis, and acceptance rule before testing. Keep an equally optimized ordinary baseline. Use genuinely fresh evaluation jobs for new claims; the current CLI's fixed seeds are public and are not a hidden evaluation set. Record all AI/human effort and actual available billing if making an economic claim.

## Questions your report must answer

- Do all eligible plans produce exactly equal outputs? Did every test and runtime scenario actually pass on your environment?
- How much processing time, complete worker time, and peak process memory changed relative to the reference, ordinary optimized policy, and corresponding AICC mode?
- Does AICC add a consistent benefit beyond the same ordinary optimized code? If the evidence is too noisy or underpowered, say so.
- Does the learned selector beat the strongest of the four simple conditional policies once feature/inference costs are included? What happens outside the 800–14,000-event calibration range?
- Does operation batching reduce invocation overhead? Which expiry, revocation, or cancellation observations differ when checking only at batch entry?
- What was measured about cost, tokens, training, setup, and maintenance? Which economic claims remain unmeasured?
- What concrete follow-up would most reduce uncertainty, and what result would falsify your favored explanation?

## Guardrails for interpreting results

AI agents designed combinations of established optimization techniques. This is not evidence of an algorithm unknown to humans. The neural network is an actual 867-parameter NumPy cost model, not an LLM or native-opcode language model. The runtime is a trusted in-process prototype, not a production security boundary. Sender/receiver runtime objects are in one OS process. The original 45 stress executions reuse three matched synthetic datasets; they are not 45 independent real-world datasets or AI authoring trials.

Do not overwrite original artifacts, silently retune on evaluation results, weaken the ordinary baseline, manufacture significance, or translate runtime percentages directly into total project dollar savings. Unknown cost fields must remain null/NOT_MEASURED. The original pasted chat GitHub token must never be used; any such exposed credential should be revoked. Use normal account sign-in for uploads and keep credentials out of reports.

Return a reviewable report/branch/patch to the project owner. Do not claim other providers participated unless they actually did, and do not merge or publish a theory-validation claim on the owner's behalf.
