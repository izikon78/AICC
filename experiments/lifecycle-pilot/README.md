# Next task: AICC reuse across agents and software changes

Prepared 4 November 2026. **Status: planning package; new pilot implementation and agent trials have not started.**

The research question is whether AICC lets new agents reuse a capability together with evidence about when it remains valid, and whether that reduces mistakes or total work as projects evolve. First-use savings, later break-even, and production security are outcomes to test.

## Start with one workflow

Implement the event-processing workflow first: ingest synthetic events, normalize and deduplicate them, group them into time windows, and apply genuinely new application logic. Create conventional, equal-evidence, and AICC paths over the same underlying capabilities. Add a small fresh grading set for reuse, handoff, relevant changes, and unrelated changes.

This deterministic engineering step can begin before paid agent trials. A passing implementation qualifies the experimental apparatus; it does not establish that AICC beats another approach.

## Package contents

- [Research brief and rationale](../../docs/research/NEXT_STUDY_AICC_FUTURE_VALUE.md)
- [Frozen-study protocol to complete before agent trials](PROTOCOL.md)
- [Ordered work packages and acceptance checks](TASKS.md)
- [Study configuration example](study-config.example.json)
- [One-stage measurement record example](trial-record.example.json)
- [Existing prototype rerun evidence](../../docs/research/evidence/README.md)

The JSON examples are **templates, not measurements or a runnable study configuration**. Unselected providers, budget, and measurements are intentionally null or empty.

## Intended pilot

| Dimension | Proposed scope |
|---|---|
| Workflows | Event processing; bounded-memory streaming; bounded workers/retries/cancellation |
| Comparisons | A: competent conventional agent; A+: conventional agent with equal semantic evidence; B: AICC |
| Sequence | Cold start, warm reuse, fresh-session handoff, relevant change, unrelated change/new use |
| Repeats | Three independent project chains per workflow and arm |
| Planned total | 27 project chains, each with five stages: 135 stage executions |
| Interpretation | Descriptive engineering pilot; no predetermined statistical power or guaranteed savings |

A project chain contains linked stages; its stages are not five independent replications. Freeze one initial implementation on the event workflow before expanding to the other workflows. An event-only run must be labeled as that subset.

## Ready-to-run gate

Before running agent trials, complete the checklist's preparation work: verify the three paths, freeze input/version manifests, isolate held-out grading cases, test the logging adapter, and record the selected models, configurations, limits, and spending cap. A cross-provider claim requires more than one provider. Missing billing telemetry prevents a billed-cost conclusion.

## Expected article contribution

Produce a concrete case study showing what one agent can reuse from another, which assumptions remain valid, which changes require review, and how cost and failures accumulate. Report results against both A and A+. If ordinary packages with the same evidence perform equally well, credit that evidence and avoid assigning a unique benefit to registry syntax.

The AI-native programming language remains an independent future study. This pilot does not choose its final syntax or claim a trained native-operation model has been evaluated.
