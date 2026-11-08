# Processing and local neural-selection study

Measured execution of synthetic jobs and actual local cost-model training. This is not an inference-billing study, an independently blinded multi-agent trial, or a demonstration of novel algorithms.

## Stress workloads

| Job | Mode | Selected plan | Median pipeline seconds | Peak process MiB |
|---|---|---|---:|---:|
| repeated-shuffled | reference | reference | 4.8781 | 815.7 |
| repeated-shuffled | static | partitioned | 2.2497 | 561.9 |
| repeated-shuffled | aicc_static | partitioned | 2.0811 | 561.6 |
| repeated-shuffled | learned | partitioned | 2.2922 | 564.2 |
| repeated-shuffled | aicc_learned | partitioned | 2.0564 | 564.2 |
| diverse-shuffled | reference | reference | 6.2695 | 1065.1 |
| diverse-shuffled | static | partitioned | 4.8905 | 847.2 |
| diverse-shuffled | aicc_static | partitioned | 4.8887 | 847.1 |
| diverse-shuffled | learned | partitioned | 4.9991 | 849.4 |
| diverse-shuffled | aicc_learned | partitioned | 4.8488 | 849.4 |
| ordered-stream | reference | reference | 5.1483 | 515.7 |
| ordered-stream | static | ordered | 3.2420 | 136.6 |
| ordered-stream | aicc_static | ordered | 3.2581 | 136.8 |
| ordered-stream | learned | ordered | 3.1391 | 139.1 |
| ordered-stream | aicc_learned | ordered | 3.3474 | 139.3 |

All listed modes produced identical output summaries and SHA-256 digests within each workload.

## Attribution and pairwise comparisons

- **diverse-shuffled:** reference/static = 1.28x; AICC-static/static = 1.000x; learned/static = 1.022x; AICC-learned/learned = 0.970x.
- **ordered-stream:** reference/static = 1.59x; AICC-static/static = 1.005x; learned/static = 0.968x; AICC-learned/learned = 1.066x.
- **repeated-shuffled:** reference/static = 2.17x; AICC-static/static = 0.925x; learned/static = 1.019x; AICC-learned/learned = 0.897x.

The first ratio reflects ordinary algorithm/flow optimization. For the other ratios, values below 1 mean lower measured time and values above 1 mean higher measured time. Both ordinary and AICC modes receive the same optimized kernels and learned model. Small registry differences may be timing noise.

## Actual neural training

- Architecture: 8 inputs, two hidden layers (32 and 16 ReLU units), 3 log-runtime outputs; 867 trainable parameters.
- Measured calibration: 72 training, 24 validation, 24 held-out jobs, separate seeds.
- Data collection: 12.56s; training: 0.15s; selected epoch: 456.
- Held-out kernel-only sum: learned 0.2551s; static 0.2551s; retrospective oracle 0.2517s.
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
