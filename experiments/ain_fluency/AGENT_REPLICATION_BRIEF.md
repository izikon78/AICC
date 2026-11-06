# Independent-agent replication brief

This is a reproduction guide, written after the first run. The preregistered
tasks, rules and predictions remain in [PLAN.md](PLAN.md); the completed evidence
and limitations are in [RESULTS_OVERVIEW.md](RESULTS_OVERVIEW.md).

## Objective

Compare Python, readable IR and numeric AIN using the same model and settings
within your replication. Measure whether demonstrated in-context familiarity
changes resources per correct controller. Do not call supplied-context learning
native model training or infer internal reasoning mechanisms from it.

## Work to perform

1. Record the repository commit, model identifier/provider, settings, usage
   reporting, account limits and a bounded run budget. Publish your adaptation
   before model calls. Reuse the frozen capabilities and exact task semantics.
   If using another provider, adapt only transport and usage extraction first;
   declare any necessary differences rather than pooling unlike models.
2. Run the deterministic harness qualification. Generate participant preparation
   with `tasks.preparation_prompt_for(mode, stage, delta)` and the matching
   schema. Grade the five answers against `tasks.expected_fluency()` outside the
   participant context, with no feedback. Run all assigned coding tasks even
   after a failed gate; keep those failures and costs in the denominator.
3. Launch **fresh participant contexts** that have not read the judge, canonical
   workflow or answer key. A supervising agent that read this repository should
   not solve the tasks in that same context and call its own tests hidden.
   Supply only the generated public preparation, its actual response, the
   generated scored prompt/schema and the assigned predecessor. Disable tools
   or mark their use as a protocol violation. Never supply repository credentials.
4. Preserve the original seeded form order, separate preparation before each
   submission, 300-second cap and one substantive answer per stage. Reproduce
   all 18 assigned stages and all 18 preparation calls. Do not improve prompts,
   add corrective retries or stop after favorable results.
5. Execute each artifact against the independent 55-case judge. Preserve raw
   provider events, response, source artifact, exact prompt/schema, every attempt,
   usage categories, cache counters, elapsed time and judge/provenance results.
   Cached input is a subset of input. Do not add reasoning output twice.
6. Keep usage missing when it is unreported. Publish cost per successful chain
   only with complete resources and valid chain denominators. Distinguish
   token-weight sensitivities from actual applicable bills. Preserve failed
   attempts, service interruptions and all assigned work.

## Known design issue to resolve before a new study

The first run's structural injector could not follow valid register reassignment
in one AIN predecessor. Under exact v1 replication, keep that fallback and
classification explicit; it is not an incorrect model program. For a larger
new protocol, preregister either dataflow-aware mutations or one fixed faulty
controller translated mechanically into all forms. Do not quietly repair the
injector after seeing a participant outcome and relabel a rerun as the original.

Original account-quota failures also interrupted a paired block. Reserve enough
capacity, record provider interruptions, and preregister any continuation rule.
The first run's operational v1.1 amendment is historical, not permission to erase
failed requests or apply unlimited retries in your replication.

## Required deliverable

Publish a separate branch/directory with your frozen protocol/adaptation,
source hashes, all 18 assignments including incomplete ones, raw usage and
artifacts, correctness/effect results, fallback provenance, cost sensitivities,
charts and a short statement of what the evidence supports. Keep the earlier
dataset unchanged. Do not pool duplicated copied records as new observations.

The first run found 18/18 correct submissions, but no established cost saving.
That is the finding to replicate or challenge—not a target to optimize toward.
For the actual learned-native hypothesis, use the separately documented
[trained-native pilot](../../docs/ain/TRAINED_NATIVE_PILOT_PROTOCOL.md), with
matched learning budgets and held-out tasks.
