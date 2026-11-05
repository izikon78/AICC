# Processing and local neural-selection study

Measured execution of synthetic jobs and actual local cost-model training. This is not an inference-billing study, an independently blinded multi-agent trial, or a demonstration of novel algorithms.

## Stress workloads

| Job | Mode | Selected plan | Median pipeline seconds | Peak process MiB |
|---|---|---|---:|---:|
| repeated-shuffled | reference | reference | 2.8716 | 814.0 |
| repeated-shuffled | static | partitioned | 1.3638 | 559.9 |
| repeated-shuffled | aicc_static | partitioned | 1.3284 | 560.1 |
| repeated-shuffled | learned | partitioned | 1.4470 | 562.0 |
| repeated-shuffled | aicc_learned | partitioned | 1.3938 | 562.4 |
| diverse-shuffled | reference | reference | 3.7627 | 1057.4 |
| diverse-shuffled | static | partitioned | 2.7166 | 844.9 |
| diverse-shuffled | aicc_static | partitioned | 2.7380 | 843.9 |
| diverse-shuffled | learned | partitioned | 2.7146 | 847.0 |
| diverse-shuffled | aicc_learned | partitioned | 2.7113 | 847.1 |
| ordered-stream | reference | reference | 3.2685 | 513.7 |
| ordered-stream | static | ordered | 2.3684 | 133.7 |
| ordered-stream | aicc_static | ordered | 2.3854 | 133.5 |
| ordered-stream | learned | partitioned | 2.5345 | 209.1 |
| ordered-stream | aicc_learned | partitioned | 2.6326 | 209.4 |

All listed modes produced identical output summaries and SHA-256 digests within each workload.

## Attribution and pairwise comparisons

- **diverse-shuffled:** reference/static = 1.39x; AICC-static/static = 1.008x; learned/static = 0.999x; AICC-learned/learned = 0.999x.
- **ordered-stream:** reference/static = 1.38x; AICC-static/static = 1.007x; learned/static = 1.070x; AICC-learned/learned = 1.039x.
- **repeated-shuffled:** reference/static = 2.11x; AICC-static/static = 0.974x; learned/static = 1.061x; AICC-learned/learned = 0.963x.

The first ratio reflects ordinary algorithm/flow optimization. For the other ratios, values below 1 mean lower measured time and values above 1 mean higher measured time. Both ordinary and AICC modes receive the same optimized kernels and learned model. Small registry differences may be timing noise.

## Actual neural training

- Architecture: 8 inputs, two hidden layers (32 and 16 ReLU units), 3 log-runtime outputs; 867 trainable parameters.
- Measured calibration: 72 training, 24 validation, 24 held-out jobs, separate seeds.
- Data collection: 8.22s; training: 0.16s; selected epoch: 900.
- Held-out kernel-only sum: learned 0.2003s; static 0.1945s; retrospective oracle 0.1932s.
- The held-out kernel-only sum excludes feature/inference overhead; the stress worker pipeline timings include those costs.
- The model selects among supplied plans. It does not synthesize a new algorithm, train an LLM, or learn a native-opcode programming language.

## Measurement boundaries

- Stress jobs above 14,000 events are size extrapolation beyond the calibration range; no retuning on stress results.
- Fresh child processes, randomized task order, and matched generated inputs; each case uses identical seed and shape across modes.
- List-input pipeline timing excludes list generation and model loading; their measured times are in the raw records. Streaming pipeline timing includes generator consumption for every mode.
- Worker wall time additionally includes process/import/startup, generation, loading, execution, digesting and serialization. Peak working set is a process-lifetime high-water mark.
- Ordered input is declared by the job descriptor and then validated on every raw row; sample features do not establish the order precondition.
- Exact dedupe and returned output require memory proportional to unique IDs and group count; streaming is not constant-memory.
- Configured duplicate_rate is a probability of referencing an earlier ordinal, not an exact measured duplicate fraction.
- The AICC host is in-process with declared dependency identities, not a production authentication/isolation boundary.
- Prototype full_validations counts compatibility checks, not an automatic semantic proof or a conformance-test run.
- No monetary model cost, billed tokens, cross-provider authoring, or lifecycle break-even was measured.

Raw records, model weights, training history, environment and source hashes accompany this report.
