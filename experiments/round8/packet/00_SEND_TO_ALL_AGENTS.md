# Round 8 — Identical cross-agent challenge

**To:** Claude, Gemini, Grok, GPT-6, and other independent evaluators
**Date:** November 3, 2026

Our research group has a **strong proposed research architecture**, not a proven deployment choice: the **AI Computational Commons (AICC)**. It integrates (a) public, cross-provider capability contracts and implementation variants, (b) encrypted/owner-controlled private project capabilities, (c) revocable host-validated bindings, and (d) an optional AI-native typed opcode language for new authoring. See `ARCHITECTURE_RECOMMENDATION.md`.

**Your mission: attempt to falsify this recommendation** using a strong normal-library baseline. A model agreeing with the proposal is not a success. We need actual cost, error and security evidence.

## Required process

1. Do not look inside `benchmark/sealed/` during authoring. Do not copy or rewrite reference implementations. Report any unintentional exposure honestly. This is a *cooperative blind*, not an access-control guarantee.
2. Read `benchmark/public/API_CONTRACTS.md` and `benchmark/public/TASKS.md`. They are common to every arm and must not be selectively withheld.
3. **Arm A:** In a fresh chat/session, solve the eight public tasks using normal Python imports from `benchmark.public.baseline_api`. Search/read normal API documentation as needed; no source reading unless you log an explicit inspection trigger.
4. **Arm B:** In a separate fresh chat/session with equivalent budget, solve the *same tasks* using `benchmark.host.registry.Runtime().bind('pub.<name>@1')`, recognizing near-miss candidates. The same contract text must be accessible; do not pretend A must reread every source implementation or contract.
5. Run `python -m benchmark.verify_submission --submission <your_file.py>` from the packet directory. Log test outcomes, revisions, source inspections and actual token/cost telemetry when available. Run `python -m benchmark.verify_submission --security`. Perform additional adversarial probes, especially ways to bypass the mock's authority boundaries, if feasible.
6. **Privacy track:** Demonstrate that a public-only bind to `private.project_risk_score@1` fails, and an authorized project-scope bind succeeds; then revoke and show old binding cannot be reused. Explicitly state that this does **not** implement encrypted private code or real OS sandboxing.
7. **Multi-agent agreement track:** Independently propose a machine-checkable contract for *one* capability (e.g. `group_by_window`) and two alternative implementations or environments. Record what third-party agents would need to validate interoperability. In the second pass, compare it with another model's independently authored contract. Do not claim multi-agent consensus after one model answer.
8. **H2 track:** Do not re-run the previous toy example as if it settles a native language. Describe an actual equal-budget typed-opcode-model versus mainstream-code model experiment and give a runnable proposal only if resources permit. Mark the trained-model test NOT EXECUTED otherwise.
9. Return your results in `02_RESULTS_TEMPLATE.md`. Include generated source, logs, tokenizer scripts, artifact SHA-256 hashes and a reproducible command list. Label measurements, illustrative examples, externally reported claims and unexecuted tests separately.

## Important ground rules

- This packet contains **20 representative small-to-medium public functions**, not a corpus of 20 audited real-world production subsystems. Its runnable tests validate orchestration mechanics. To make meaningful general claims, propose an extension using at least 20 *independently sourced, production-scale capabilities* and publish selection criteria, assurance levels and held-out workflows.
- `Runtime` is an **honest mock**, not a secure sandbox, credential vault, cryptographic binding certificate, or encryption system. Its Python source is available in the packet; OS-level file access isn't restricted. Identify and test these weaknesses rather than credit the mock with protection it does not have.
- We don't yet know what fraction of an application is reusable. Proposed 60–80% public functionality is an **unverified hypothesis**; the unit of measurement needs definition and empirical collection.
- Baseline A gets the same mature implementation package as B. Registry B must demonstrate **incremental value** through safer matching, better selection, cross-provider interoperability, reduced context, or persistent verified bindings—not just reusing a function.
- One-off pass counts don't establish success rates; actual billed/model input-output-reasoning token telemetry is required for any claim about inference savings. Source-file bytes and tiktoken artifact counts are weaker evidence.
- Use the supplied test fixture version unchanged, publish exact SHA-256 manifest; if changed, publish a fork and compare separately.

**Primary research question:** With the same existing implementations available, does AICC reduce *cost per correct task* or materially improve security/compatibility relative to competent ordinary API reuse, under realistic public/private boundaries?
