# Lifecycle pilot protocol — draft 0.1

Date: 4 November 2026. This is a plan to freeze and complete before new agent trials. Provider configurations, monetary limits, and exact task/grading manifests are still unset. It is not an executed or preregistered confirmatory study.

## Research question and outcomes

Test whether shared capability records and validated bindings help agents reuse correct behavior across sessions and changes beyond competent conventional reuse.

Report two primary outcome families separately:

1. **Reliability:** whole-project correctness, false reuse/stale acceptance, and unnecessary invalidation.
2. **Economics:** total measured cost per correctly completed five-stage project chain, comparing B against A and A+ separately.

Secondary outcomes include qualification/repair work, handoff effort, timing, resource use, and authorization failures under the tested boundary. The pilot is descriptive. Do not claim a guaranteed percentage saving, statistical superiority, or production security from these runs.

## Arms and information parity

| Arm | Available resources |
|---|---|
| A | Same capability implementations, ordinary package APIs/docs, discovery, code execution, caching, durable project notes/code, and version locks |
| A+ | A plus the same conformance tests, manifests, and semantic evidence available to B |
| B | Same capabilities and evidence plus shared versioned capability records and host-checked portable bindings |

All arms receive the same task and equivalent runtime authority, tools, and execution limits. Conventional agents may retain and reuse valid information. Charge common evidence preparation consistently to A+ and B. Record B-specific registry/binding overhead separately. A B-versus-A result without a B-versus-A+ advantage supports a narrower conclusion about the evidence or its organization.

## Workflows and replication unit

Proposed workflows:

- **W1 events:** synthetic event ingestion, normalization, deduplication, time-window grouping, and new application rules.
- **W2 streams:** bounded-memory file processing, chunked hashes/transforms, cleanup, and failure handling.
- **W3 workers:** bounded concurrency, cancellation, ordering, retries, and idempotency.

Start by qualifying W1. Expand only after the harness and logger meet their acceptance checks. The complete proposed pilot has three independent chains per workflow per arm: 3 workflows × 3 arms × 3 chains = **27 project chains**. Each chain has five linked stages, producing **135 stage executions**. The independent unit is a new project chain; stages within it share history and are not independent replications.

These counts are engineering planning choices, not a statistical power calculation. A W1-only subset contains nine chains and 45 stage executions and must be reported as that subset.

## Five-stage sequence

| Stage | Intervention | Expected observation |
|---|---|---|
| S1 cold start | Discover, qualify, and compose capabilities for an unfamiliar task | Correct behavior and complete preparation/usage costs |
| S2 warm reuse | Add application logic without changing relevant validity conditions | Valid reuse; measure repeated qualification and repair work |
| S3 handoff | A fresh agent session continues using only permitted project artifacts | Correct continuation; measure new qualification and context work |
| S4 relevant change | Change a requirement, implementation/dependency, contract, policy, environment, expiry, or revocation state | Affected reuse must be reconsidered before incorrect or unauthorized execution |
| S5 unrelated change/new use | Change an unrelated component and test legitimate reuse plus a separate unauthorized attempt | Unaffected work remains usable; unauthorized reuse is denied by the tested host |

Before runs, define exact variants and expected behavior for every intervention. Include all relevant change categories in the grading/engineering checks; allocate agent-stage variants with a recorded balanced seed schedule and report coverage. Do not imply that one S4 intervention per chain tests every category independently.

The stage order stays fixed because it models project evolution. Randomize arm execution order and matched scenario seeds. Use the same model/provider sequence for paired arms; record exact model/version, settings, context/memory policies, and tool limits. Keep separate arms' project state and answers isolated.

For cross-provider claims, the handoff must include another provider and its direction must be recorded. If only one provider is available, label the result as within-provider handoff. Do not pool those conditions silently.

## Grading and experimental integrity

- Use fresh synthetic tasks and held-out cases. Published Round 7/8 fixtures and the 1,206-case historical conformance pool are regression material, not unseen evaluation data.
- Fix observable outputs, error behavior, ordering, effects, and resource limits. Include valid, incompatible, and insufficiently specified candidates without names that reveal the answer.
- Keep grading cases outside the authoring agent's accessible project/context; record access controls and any leakage. A folder named `sealed` alone does not provide isolation.
- Version/hash all tasks, contracts, implementations, dependencies, runtime images, policy settings, and grading cases. Preserve failed versions and all repair attempts.
- Capture the permitted handoff artifacts and model-visible messages/tool outputs, with secrets excluded. Record the change schedule and random seeds.
- If a model/provider or task must be replaced, record a protocol deviation rather than quietly changing the comparison.

## Measurement and accounting

Use `trial-record.example.json` as a field guide, not as measured data. Each stage belongs to a chain and each attempt gets its own identifier. Retain failed and incomplete attempts.

Collect available uncached/cached input, output/reasoning, cache-write data, and root/subagent usage with provider definitions. Avoid double counting reasoning when it is included in another total. Retain raw usage and billing provenance. Static file tokenization is a separate artifact measurement.

Measure wall time and available model, tool, qualification/bind, verification, and repair durations with a monotonic clock. CPU/memory measures concern host execution, not hidden model compute. Declare any unavailable components.

For each arm, report:

```text
total lifecycle cost = preparation/curation + all attempts + maintenance + infrastructure
cost per successful chain = total lifecycle cost / number of chains passing all required stages
net difference(N) = comparator cumulative cost(N) - B cumulative cost(N)
```

Show provider charges and valued human work separately, state currency/rates, and avoid double counting shared costs. If no chain succeeds, cost per successful chain is undefined; report the costs and zero success instead of dividing by zero. If required billing is absent, label the economic endpoint NOT MEASURED rather than imputing zero.

Count shared setup once and amortize over observed uses. Show cold, warm, handoff, and change phases separately. Do not assume first-use loss, a later break-even, or a ten-use threshold. An extrapolated crossing is modeled; an observed crossing is limited to the measured workload and accounting assumptions.

## Readiness, stopping, and completion

Before paid model trials: freeze the study/configuration manifest, pass the three-path engineering checks, test the logger, select provider configurations, and record the spending cap. Model calls must stay within that cap; record a budget-limited chain as incomplete.

An incorrect compatibility decision or authorization failure is an observed failure. Stop an unsafe implementation version, preserve its record, and require a versioned repair and a fresh readiness check before continuing. Use synthetic resources and the same controlled execution boundary across arms. Passing these checks does not establish a general security guarantee.

The pilot is complete when all planned attempts or explicit deviations are accounted for, the raw records support each reported measure, outcomes are separated by arm/workflow/provider/stage, and the final analysis includes failures and source limitations. A negative or inconclusive result completes the scientific question for the tested conditions; no favorable outcome is required.

Use the measured variance and an explicitly chosen practically important effect to design a larger confirmatory study. Freeze that study's thresholds before its results are seen.

## Required outputs

1. Versioned scope/configuration and input manifests.
2. Comparable implementations and engineering/change checks.
3. New grading cases with documented authoring separation.
4. Complete raw attempts, provider/billing provenance, and test records.
5. Observed correctness, revalidation, and cumulative-cost analysis.
6. An article case study that states exactly which claims the results support.
