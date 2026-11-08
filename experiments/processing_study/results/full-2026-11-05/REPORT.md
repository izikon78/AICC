# Processing and local neural-selection study

Measured execution of synthetic jobs and actual local cost-model training. This is not an inference-billing study, an independently blinded multi-agent trial, or a demonstration of novel algorithms.

## Stress workloads

| Job | Mode | Selected plan | Median pipeline seconds | Peak process MiB |
|---|---|---|---:|---:|
| repeated-shuffled | reference | reference | 6.2313 | 814.4 |
| repeated-shuffled | static | partitioned | 3.2262 | 561.7 |
| repeated-shuffled | aicc_static | partitioned | 3.2271 | 561.8 |
| repeated-shuffled | learned | partitioned | 3.1826 | 563.7 |
| repeated-shuffled | aicc_learned | partitioned | 3.6255 | 563.1 |
| diverse-shuffled | reference | reference | 8.6497 | 1060.2 |
| diverse-shuffled | static | partitioned | 6.4179 | 845.5 |
| diverse-shuffled | aicc_static | partitioned | 6.5064 | 846.2 |
| diverse-shuffled | learned | partitioned | 6.2558 | 849.5 |
| diverse-shuffled | aicc_learned | partitioned | 6.6093 | 847.4 |
| ordered-stream | reference | reference | 7.7965 | 515.5 |
| ordered-stream | static | ordered | 5.3853 | 135.8 |
| ordered-stream | aicc_static | ordered | 5.3265 | 135.8 |
| ordered-stream | learned | partitioned | 6.0280 | 211.0 |
| ordered-stream | aicc_learned | partitioned | 5.4611 | 210.7 |

All listed modes produced identical output summaries and SHA-256 digests within each workload.

## Attribution and pairwise comparisons

- **diverse-shuffled:** reference/static = 1.35x; AICC-static/static = 1.014x; learned/static = 0.975x; AICC-learned/learned = 1.057x.
- **ordered-stream:** reference/static = 1.45x; AICC-static/static = 0.989x; learned/static = 1.119x; AICC-learned/learned = 0.906x.
- **repeated-shuffled:** reference/static = 1.93x; AICC-static/static = 1.000x; learned/static = 0.986x; AICC-learned/learned = 1.139x.

The first ratio reflects ordinary algorithm/flow optimization. For the other ratios, values below 1 mean lower measured time and values above 1 mean higher measured time. Both ordinary and AICC modes receive the same optimized kernels and learned model. Small registry differences may be timing noise.

## Actual neural training

- Architecture: 8 inputs, two hidden layers (32 and 16 ReLU units), 3 log-runtime outputs; 867 trainable parameters.
- Measured calibration: 72 training, 24 validation, 24 held-out jobs, separate seeds.
- Data collection: 19.60s; training: 0.32s; selected epoch: 164.
- Held-out kernel-only sum: learned 0.4573s; static 0.4531s; retrospective oracle 0.4223s.
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
