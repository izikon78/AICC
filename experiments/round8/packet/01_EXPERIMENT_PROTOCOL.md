# Round 8 — Experimental protocol

## Claims to test

- **H1:** shared public capability contracts + bound, immutable implementation handles improve cost or quality over well-documented existing packages.
- **H3:** preserving scoped compatibility decisions across calls/sessions adds benefit beyond ordinary API documentation caching, without stale trust or authorization.
- **H4:** public and project/private capabilities compose without exposing private implementation, with revocation and resource permissions enforced by a genuine host (the included mock is insufficient for this final claim).
- **H2:** a trained native operation-token model improves all-in *new authoring* vs strong conventional-language/typed AST baselines. This is a separate, higher-cost study.

## Actual provided pilot fixture

- 20 public capabilities, 3 deliberately misleading variants, 1 project-private demonstration capability.
- 8 composition assignments with 20+ edge/corner test cases; separate private binding, unauthorized use, and revocation checks.
- Every arm can use the exact same underlying Python implementation. The capability registry is an alternative interface, NOT a different superior algorithm.
- The source resides under `benchmark/sealed/` so agents can voluntarily avoid seeing it; **not encrypted**.
- The comparison is exploratory, not a production-scale benchmark or secure sandbox.

## Stable arms

**A — strong standard-library baseline:** `from benchmark.public.baseline_api import ...`; use `benchmark/public/API_CONTRACTS.md`; enable normal search and caching; do not read sealed sources without logged trigger.

**B — public commons:** `from benchmark.host.registry import Runtime`; bind names `pub.normalize_tag@1`, etc. `bind()` returns a callable. Get same API contracts and a candidate list, including near misses. No stronger information should be withheld from A.

**C — private composition and refusal:** test `Runtime.bind('private.project_risk_score@1')` with disallowed and allowed scopes/effects, revocation and stale binding. A competent conventional implementation should be compared using the **same** policy envelope, not a bare unsafe import.

**D — AI-native authoring research:** design a separately held-out suite for real models trained on an operation vocabulary, compared with standard code and typed action APIs. The provided Python fixture does not contain that model and cannot support a passing D claim.

## Randomization and isolation

Each evaluator should use independently reset sessions per arm if possible, with equal context and ability to retrieve the public contract, identical tests and tool budget. Randomize which arm is run first across multiple repetitions. If impossible, mark as `SAME SESSION / CONTAMINATED` and do not present it as a randomized replication. Preserve logs and reported API usage. Do not use exact expected outputs from `benchmark/sealed/reference_solution.py` to author the solution.

## Metrics (mandatory where available)

- Correctness: passing public workflow cases, private-policy checks, selected near misses, failures and regression cases.
- Agent input/output/reasoning tokens **as provided by model API telemetry**, cache read/write usage, paid inference cost and total wall-clock. If unavailable: `NOT MEASURED`.
- Tool calls, retrieval cards considered, source files opened, contract expansions, inspections forced by `UNKNOWN`, retries, repairs and human intervention.
- Variant fit precision, incorrect reuse rate, expired/revoked binding rejection, privacy boundary failures, cross-agent contract disagreements.
- Full lifecycle cost including up-front curation, security review, upgrades and maintenance (may require estimates; mark those as modeled rather than measured).

## Adversarial obligations

1. Near-miss: money HALF_EVEN vs HALF_UP for `1.005`.
2. Near-miss: path sanitization that rewrites traversal rather than rejecting it.
3. Near-miss: event grouping by event ID rather than business behavior.
4. Contract insufficiency: identify at least one output or environmental condition not fully specified by the public API contract (e.g., GZIP implementation/platform differences or PNG CRC checks), and state `UNKNOWN` rather than claiming equivalence.
5. Trust: demonstrate an untrusted Python function with false declared effects can bypass this mock outside a real sandbox. Do not call this a validated production security failure; it is a missing protection in the prototype.
6. Private identity: signed and encrypted are different; test unauthorized bind, successful scoped bind, revocation, and specify a production design for key distribution and runtime isolation.
7. Multi-vendor agreement: reconcile contract signatures, behavioral edge cases, license, implementation variants, and proof/test evidence without claiming vendors have formally agreed on one algorithm.

## Pilot commands

From the extracted `AI_Think_Tank_Round8_Packet` directory:

```bash
python -m benchmark.verify_submission --self-test
python -m benchmark.verify_submission --security
python -m benchmark.verify_submission --submission submission_A.py
python -m benchmark.verify_submission --submission submission_B.py
python -m benchmark.token_measure submission_A.py submission_B.py
```

`--self-test` validates only that organizer reference fixtures execute against themselves; it is **not** an agent result. The `--submission` argument expects functions specified in `benchmark/public/TASKS.md` (the eight public workflows). `tiktoken` is optional; actual model token telemetry still requires a model/API response.

## Results that would disconfirm our recommendation

- Commons B offers no reproducible cost/reliability gain over A with realistic package search, caching, and matching, once total overhead is counted.
- The registry increases silently wrong reuse because compact cards hide critical assumptions.
- Private/function execution cannot be sufficiently isolated or revoked at acceptable cost in a realistic runtime.
- Cross-provider semantic agreements are expensive, fragile, or less effective than existing standards + typed APIs.
- Native opcode language reduces bytes but not total cost/correctness compared with ordinary language models + typed action interfaces.

## Production-scale follow-up (mandatory proposal, not executable in pilot)

Define a preregistered blinded study with **at least 20 independently selected production-grade capabilities** across data/IO/image/network/security/algorithm domains; 50–100 unseen multi-file tasks; ≥3 fresh runs per arm; hidden behavioral tests; variant near misses; private-component permissions; full API telemetry and cost. Quantify contract sufficiency and version drift. We do not yet have such a corpus in this packet; agents must not pretend that it has already been tested.
