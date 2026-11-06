# AICC and AIN

Research into how AI agents can create, change, and reuse software through precise computational representations.

**AIN — AI Native Language** is the working name for the project's next research direction: a proposed programming representation designed for machine authoring, with explicit semantics, types, state, effects, and resource behavior. **AICC — AI Computational Commons** is the companion proposal for discovering and composing reusable capabilities through precise contracts and scoped bindings.

Concept, architecture, and research direction: **Izik Bachar**.

## Start here

- [Native AIN feasibility decision and primary-source research](docs/research/NATIVE_AIN_FEASIBILITY_2026-11-05.md)
- [Article Draft 9: It started with a beep](docs/article/AICC_Article_Draft_9.md)
- [Current native-learning hypotheses and training protocol](docs/ain/NATIVE_HYPOTHESES.md)
- [First executable AIN study: code, tests, agent edits, charts and results](https://github.com/izikon78/AICC/blob/research/ain-v0-foundation/experiments/ain_v0/FIRST_EXECUTION_REPORT.md)
- [Preserved Draft 8 and its Word/PDF review copies](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/article)
- [AIN research plan and next deliverables](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/ain)
- [Complex streaming task and illustrative AIN representation](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/ain/COMPLEX_TASK.md)
- [Combined processing-study results](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/research/REPLICATION_SYNTHESIS_2026-11-05.md)
- [Charts, pie charts, CSV data, and source hashes](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/article/figures/draft8)

The article and reviewed processing archive are maintained on `research/ain-language-and-study-results`; the first executable AIN study is on `research/ain-v0-foundation`. The project description on `main` is the public entry point. Draft studies remain reviewable without treating them as final validation.

## What has been tested

The original local study and submitted Claude and Grok remeasurements contain 135 completed million-event worker executions across three reused synthetic datasets. Their output signatures agree. Optimized ordinary code reduced processing time and peak process memory, and the same optimized implementations remained usable through the AICC prototype.

The studies also trained an 867-parameter local neural cost model. It did not consistently beat a strong simple selection policy. This network predicts the cost of supplied processing plans; it is not an AIN model or an LLM trained on native operation tokens.

These results provide an engineering foundation and a reproducible benchmark. They do **not** establish AICC-specific financial savings, a native-language advantage, a new algorithm unknown to humans, or production private-code isolation. Submitted model identities and remote execution environments are self-reported. Three timing repetitions are descriptive, not statistical proof.

| Area | Current status |
|---|---|
| Equivalent event-processing flows and binding prototype | Implemented and measured |
| Original plus two submitted remeasurements | Records reviewed; raw data and provenance preserved |
| AIN v0 semantics and complex benchmark | Implemented engineering prototype; 69 tests, 27 workers and six agent-edit submissions pass |
| Complete AIN compiler or native-operation model | Not implemented or evaluated |
| Lifecycle economics and billed AI savings | Not established |

The first AIN run establishes executable/editable feasibility for its tested
cases. Numeric AIN and readable IR have identical control flow in this version.
The numeric interpreter was slower than direct Python; neither printed length
nor a reduction in selected operation calls establishes native-language savings.

## Next phase

1. Repair and freeze the judge, preserving the two existing executable prototypes
   and all measured results as records of their tested conditions.
2. Expose sufficient authorable logic and prepare equivalent semantic data for
   source, readable IR, spelling controls and any distinct AIN structure.
3. Freeze a bounded actual training setup. The main condition is a model that
   already knows its language before evaluation, with no fixed-language primer.
4. Compare matched native learning/adaptation on closed programming tasks, with
   actual inference/tool resources per correct chain and a declared stop rule.
   Test AICC lifecycle and AI implementation/compiler effects separately later.

The research question is whether AIN improves correct completed work and maintenance effort, rather than merely shortening printed code. Future results must include failures, repair effort, applicable billing, setup/training costs, and strong conventional controls.

## Evidence and reproduction

- [Executable processing study and commands](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/experiments/processing_study)
- [Assignment for other AI agents](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/experiments/processing_study/agent-replication)
- [Claude replication report](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/agents/claude/processing-study-replication-2026-11-05/AGENT_REPORT.md)
- [Grok replication report](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/AGENT_REPORT.md)
- [Review method and audit records](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/research/replication-review)
- [Historical archive, corrections, and source-version gaps](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/research/REVIEW_2026-11-04.md)

The processing benchmark uses Python/NumPy and no paid model API calls. New language/model experiments are separate future work. Earlier reports, unfavorable findings, original archives, and contribution credits are retained alongside their limitations.
