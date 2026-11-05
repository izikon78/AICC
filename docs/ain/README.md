# AIN native programming research

**AIN means AI Native Language and is the working name of this project's proposed programming representation.** AICC remains the AI Computational Commons, a separate capability-reuse architecture. AIN is a research priority, not a claim that a complete native-token language or trained model exists.

The proposed value is a precise representation that helps agents author, inspect, change, and exchange complex programs while a deterministic runtime enforces their computational semantics. Any improvement in correctness, repair effort, latency, or measured cost must be compared with strong conventional source and structured-program controls.

## Next work

1. Read the [research plan](RESEARCH_PLAN.md) and [complex benchmark task](COMPLEX_TASK.md).
2. Freeze a small typed semantic core and reference interpreter. Specify errors, numeric behavior, resources, effects, cancellation, ordering, and state transitions before choosing a compact spelling.
3. Produce equivalent conventional-source, structured-IR, and AIN views of the same complex programs, with equal libraries and metadata. Demonstrate conformance before using model performance as evidence.
4. Run a bounded existing-model pilot on fresh tasks, recording correct completion, edits, failures, time, and available billed usage. Keep this distinct from representation-specific model training.
5. Only after the pilot informs feasibility, design matched training/adaptation experiments for dedicated operation tokens with declared compute/data budgets and fresh held-out evaluation.

No paid model runs or native-language model training are authorized or executed by this planning package. The earlier [867-parameter network](../../experiments/processing_study/README.md) predicts kernel costs; it is not an AIN model. See the [replication synthesis](../research/REPLICATION_SYNTHESIS_2026-11-05.md) for what the existing experiments do establish.

## Working name

AIN keeps the language distinct from AICC; AIC would make those names easier to confuse. Use the repository namespace `AICC / AIN` while the design is exploratory. The acronym is not unique: MBZUAI already uses [AIN for a multimodal model](https://huggingface.co/MBZUAI/AIN/blob/main/README.md). AIC also appears in existing software/language projects, including [AICore](https://github.com/forgeopslabs/aicore). This is a working research label, not a claim of exclusive naming or technical novelty.

Concept and architecture: Izik Bachar. Draft development and engineering assistance are attributed in the article and supplied research records.
