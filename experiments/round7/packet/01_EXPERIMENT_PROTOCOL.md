# Round 7 experiment protocol — version 1.0

This packet tests *specific, falsifiable parts* of H1, H2, and H3. It is an exploratory benchmark and cannot establish general software-development economics with a few tasks. Use fresh chats or stateless trials for comparisons whenever possible.

## Quick start

- Requirements: Python **3.10+** and only the standard library for execution tests.
- Place your own files in the packet root. Examples below are file names, not provided solutions.
- Test: `python fixtures/test_tasks.py --submission submission.py` (H1 arm)
- Test: `python fixtures/test_tasks.py --python-controller controller_submission.py` (new code in Python)
- Test: `python fixtures/test_tasks.py --symbolic controller_submission.sym` (new code in toy symbolic syntax)
- Trust-control checks: `python fixtures/binding_checks.py`
- Optional real artifact-token accounting: `python fixtures/token_measure.py` (requires installed `tiktoken`). Record the tokenizer name/version.

The supplied harness has been checked against organizer-held reference solutions. These are **harness sanity tests**, not model-performance observations.

## Common behavior tasks

### T1 — Small controller example

Implement a function that returns the messages emitted by this C# logic. Preserve exact message strings and counts:

```csharp
public void Main(int NumOfRuns)
{
    for (int i = 0; i < NumOfRuns; i++)
    {
        if (i == 0)
            m_log.Info($"Starting controller service for {NumOfRuns} runs");
        else
            m_log.Info($"Restarting controller service for run {i+1} of {NumOfRuns}");
    }
}
```

The test uses `n = -2,0,1,2,3,17`. Because the harness doesn't have an actual C# logger, the observable output is a list of the exact logging strings in order. This is a test abstraction, not full C#/.NET behavioral equivalence.

### T2 — Larger activity rollup

Implement a wrapper that produces exactly the behavior described in `fixtures/activity_contract.md`: normalize events, sort them, group nearby duplicate behavior, apply severity filtering, and return deterministic groups. The harness exercises mixed-case values, event timing, invalid records, same signatures with subtly wrong behavior, and invalid input errors.

### T3 — Near miss and authorization check

In `fixtures/capability_cards.md` there are five matching-looking handles. Some are incorrect or request disallowed effects. Choose the correct ones **from contract information** before running the tests. Record why you rejected `controller.logs_zero_based`, `activity.rollup_by_eventid`, and `activity.rollup_and_save`. Run `python fixtures/binding_checks.py` and state precisely what this toy binding check does *not* establish about real zero-trust security.

## H1: compare against a strong baseline, not a straw man

Two experimental arms implement **the same two wrappers**:

- **Arm A (ordinary library reuse):** Read `fixtures/baseline_api.md` and `fixtures/activity_contract.md`; import existing `controller_logs` and `rollup_activity` from `capabilities`. Do **not** inspect the implementation unless needed. Write `submission.py` exporting `run_controller(n)` and `run_rollup(events,window_seconds=600,min_severity=0)`. You are allowed to use existing Python API calls rather than generate implementations. This deliberately creates a strong, honest baseline.
- **Arm B (registry reuse):** Read `fixtures/capability_cards.md` and the contracts it references. Use `registry.bind(handle, allowed_effects=())`, then implement the *same* two wrapper functions. Reject the misleading and effect-unsafe candidates. Do not inspect implementation unless needed.

A and B should have the same access to tests, tools, model budget, and behavioral contract detail. **Run them in independent fresh model conversations/trials if possible.** Doing A then B in the same chat contaminates the second arm; mark as `EXPLORATORY SAME-SESSION` if unavoidable. Your model may not have access to independent agents or API-level usage metrics; say so.

For each arm record: how many implementation files were opened, contract/documentation tokens consumed if actually measured, search candidates considered, retries, exact test counts, and any API-reported inference usage. Do NOT equate avoided source-file tokens with actual total-token savings.

## H2: new authoring, separate from reuse

For this comparison, **pretend no registry capability is available** for T1. Do not import the reference implementation.

- **Arm C (Python):** Create `controller_submission.py` defining `controller_logs(n)` and run `python fixtures/test_tasks.py --python-controller controller_submission.py`.
- **Arm D (toy symbolic text):** Create `controller_submission.sym` implementing T1 using the provided fixed grammar in `fixtures/symbolic_runtime.py` documentation. Run `python fixtures/test_tasks.py --symbolic controller_submission.sym`.

Toy language forms supported by the parser:

```
@number(parameter:I){expression}
R(count,index){expression}
?(left=right,then_expression,else_expression)
!7(T0,integer_expression)
!7(T1,integer_expression,integer_expression)
```

A term is a parameter or loop-index name, an unsigned integer literal, or a variable plus an unsigned integer. `R(n,i)` counts `i=0` through `n-1` and does nothing for `n<=0`. `T0` is the exact first-log template (one numeric operand) and `T1` is the exact restart-log template (run ordinal and total runs; two numeric operands). A model generating correct instructions must still choose correct operands. This tiny grammar is **not general-purpose and does not test learned atomic-token vocabularies**.

Record generated program bytes, tokens under a specified tokenizer if available, parse failures, incorrect traces, and revision attempts. More important, record whether the model had to reread extensive grammar documentation. If you can only simulate special single-token opcodes, label those counts **hypothetical**, not measured model tokens.

**H2's real test requires model training or adaptation** plus a general-purpose benchmark of fresh tasks. Do not claim that the results of this toy language settle H2.

## H3: validated binding and reuse persistence

Use Arm B's verified selected handles for repeated calls. After the first valid binding, simulate 20 invocations in the same session and count the payload bytes/tokens for:

1. Reprinting the full contract before every call.
2. Supplying the contract once and using a short local alias thereafter.

If a tokenizer is available, measure both exact serialized payloads; else report byte/character counts, explicitly labeled. Do not report an overall model token reduction unless actual inference usage is available. Long chat histories can still consume model attention even when a contract is not reprinted.

Run `fixtures/binding_checks.py`, which tests denial of unauthorized declared effects and artifact digest mismatch. Explain what happens when the environment, requirement, permissions, dependency versions, or revocation state changes. This packet **does not implement** cryptographically signed certificates, runtime sandboxes, or revocation; these remain research/design requirements.

## Required adversarial counterexample

Demonstrate at least one condition under which same signatures and similar names do *not* permit substitution:

- `controller.logs_zero_based` produces the wrong restart ordinal.
- `activity.rollup_by_eventid` does not merge equivalent events.
- `activity.rollup_and_save` demands `filesystem.write`, which is forbidden for pure activity analysis.

Which can be rejected by contract alone? Which require executable test evidence or runtime controls? An agent declaring a component safe is not itself proof of safety.

## Measurements and quality thresholds

Report counts under named tokenizers only when run. If billing or model telemetry is unavailable, mark `TOTAL MODEL TOKENS: UNKNOWN`. Require correctness equal to or better than the strong baseline before calling a cheaper representation a win. Quantify cost per *correctly completed task* when the data allows, including extra reasoning, retries, retrieval, review, and debugging.

Keep findings in three categories: `MEASURED`, `REPORTED BY ANOTHER MODEL, UNREPLICATED`, `HYPOTHESIS / ESTIMATE`.

### Optional stronger replication

Perform at least three fresh trials per arm, randomized execution order and held-out additional tasks. The single-run toy results are exploratory only; they cannot validate universal performance claims.

## Stop conditions

If an agent cannot actually execute tests, run tokenizers, or isolate the trial arms, it should return a design assessment and runnable candidate files, with `NOT EXECUTED` marked prominently. It must not manufacture timings, generated token counts, or security outcomes.
