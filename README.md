# AICC and AIN

Research into how AI agents can create, change, and reuse software through precise computational representations.

**AIN — AI Native Language** is the working name for the project's next research direction: a proposed programming representation designed for machine authoring, with explicit semantics, types, state, effects, and resource behavior. **AICC — AI Computational Commons** is the companion proposal for discovering and composing reusable capabilities through precise contracts and scoped bindings.

Concept, architecture, and research direction: **Izik Bachar**.

## Start here

- [Latest article and printable review copy](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/article)
- [AIN research plan and next deliverables](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/ain)
- [Complex streaming task and illustrative AIN representation](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/ain/COMPLEX_TASK.md)
- [Combined processing-study results](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/research/REPLICATION_SYNTHESIS_2026-11-05.md)
- [Charts, pie charts, CSV data, and source hashes](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/article/figures/draft8)

The research materials are maintained on `research/ain-language-and-study-results`; this README on `main` is the project entry point. Draft studies remain reviewable without treating them as final validation.

## What has been tested

The original local study and submitted Claude and Grok remeasurements contain 135 completed million-event worker executions across three reused synthetic datasets. Their output signatures agree. Optimized ordinary code reduced processing time and peak process memory, and the same optimized implementations remained usable through the AICC prototype.

The studies also trained an 867-parameter local neural cost model. It did not consistently beat a strong simple selection policy. This network predicts the cost of supplied processing plans; it is not an AIN model or an LLM trained on native operation tokens.

These results provide an engineering foundation and a reproducible benchmark. They do **not** establish AICC-specific financial savings, a native-language advantage, a new algorithm unknown to humans, or production private-code isolation. Submitted model identities and remote execution environments are self-reported. Three timing repetitions are descriptive, not statistical proof.

| Area | Current status |
|---|---|
| Equivalent event-processing flows and binding prototype | Implemented and measured |
| Original plus two submitted remeasurements | Records reviewed; raw data and provenance preserved |
| AIN semantics and complex benchmark | Proposed research specification |
| Complete AIN compiler or native-operation model | Not implemented or evaluated |
| Lifecycle economics and billed AI savings | Not established |

## Next phase

1. Freeze the complex task's observable semantics and build a readable reference implementation with adversarial state/effect traces.
2. Implement a small typed semantic core and equivalent conventional-source, structured-IR, and AIN views.
3. Evaluate current models on fresh build, edit, repair, optimization, and handoff tasks with equal libraries and evidence.
4. Use those results to decide whether matched model adaptation and dedicated operation tokens justify further experiments.

The research question is whether AIN improves correct completed work and maintenance effort, rather than merely shortening printed code. Future results must include failures, repair effort, applicable billing, setup/training costs, and strong conventional controls.

## Evidence and reproduction

- [Executable processing study and commands](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/experiments/processing_study)
- [Assignment for other AI agents](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/experiments/processing_study/agent-replication)
- [Claude replication report](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/agents/claude/processing-study-replication-2026-11-05/AGENT_REPORT.md)
- [Grok replication report](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/AGENT_REPORT.md)
- [Review method and audit records](https://github.com/izikon78/AICC/tree/research/ain-language-and-study-results/docs/research/replication-review)
- [Historical archive, corrections, and source-version gaps](https://github.com/izikon78/AICC/blob/research/ain-language-and-study-results/docs/research/REVIEW_2026-11-04.md)

The processing benchmark uses Python/NumPy and no paid model API calls. New language/model experiments are separate future work. Earlier reports, unfavorable findings, original archives, and contribution credits are retained alongside their limitations.
