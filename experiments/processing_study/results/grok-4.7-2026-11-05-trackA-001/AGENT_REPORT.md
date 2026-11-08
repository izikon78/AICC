# Agent report: Track A remeasurement

Run id: `grok-4.7-2026-11-05-trackA-001`

Author: Grok 4.7 (xAI). Provider, model, and version are self-reported. No other provider ran this replication. This session did not meter tokens or billing. Every cost field that was not measured is null or `NOT_MEASURED`.

Track A retrained the cost model on this machine and then ran the published million-event matrix. The Python sources were not modified. Original artifacts in `results/full-2026-11-05/` were not modified.

## Provenance

| Item | Value |
|---|---|
| Repository | https://github.com/izikon78/AICC |
| Checkout | `63d012095a6db66a71918cb574fb2c6ceaecf147` (packet tip, depth-1 fetch) |
| Frozen implementation | `75de32b757b8bdc43886213ee6b9dd9470717918` |
| Source hashes | All 11 recorded Python files match `run-config.json` from the frozen run, and the before-run and after-run manifests in this directory match each other |
| Model | Trained this run. SHA-256 is `model_sha256` in `submission-template.json` |
| Policy | Fit this run on training rows only: `partitioned`, with `ordered` when the job declares order |

The frozen commit object was not in the shallow clone. Hash agreement is what makes this an unchanged-source replication. The packet tip adds documentation around those sources.

## Environment and commands

Windows 10.0.19045, AMD Ryzen 7 7800X3D (8 cores, 16 logical processors), 31.6 GiB RAM. Python 3.12.12, NumPy 2.3.5, Unicode 15.0.0, BLAS scipy-openblas 0.3.30. `OPENBLAS_NUM_THREADS`, `OMP_NUM_THREADS`, and `MKL_NUM_THREADS` were 1. The host was not exclusive and was not frequency-pinned. The published run used Python 3.12.14 on a 12-logical-CPU machine. Absolute seconds from that machine are not used as a baseline below.

Virtual environment: `H:\dev\github\itzik\AICC\.venv`. NumPy came from `experiments/processing_study/requirements.lock.txt`.

| Step | UTC | Exit |
|---|---|---|
| `python -m venv .venv` and `pip install -r experiments/processing_study/requirements.lock.txt` | start 2026-11-05T16:57:26Z | 0 |
| `python -m unittest discover -s tests -v` from `experiments/processing_study` | 16:57:42.913Z to 16:57:43.483Z | 0 |
| `python -u run_study.py --output results/grok-4.7-2026-11-05-trackA-001 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900` | 16:57:55.391Z to 17:01:23.215Z | 0 |
| `python tools/processing_granularity.py --output experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/granularity.json --events 1000000 --repeats 3` | 17:01:30.385Z to 17:01:44.440Z | 0 |

Logs: `unit-tests.log`, `study-console.log`, `granularity-console.log`. Workers ran one at a time, in fresh child processes, in the order shuffled with seed 441105. Granularity started only after the study printed `COMPLETE`. Nothing was excluded. There is no `failed-worker.json` or `failed-output.json`.

One wrapper mistake happened before any of those recorded commands: the first unittest launch was aborted because the PowerShell wrapper treated unittest's stderr progress lines as a terminating error. That attempt left no result. The log on disk is the rerun above, and calibration had not started.

## Correctness

44 unit-test methods passed in 0.341 seconds. Failed: 0. Skipped: 0.

Nine of nine binding scenarios passed: cold binding, twenty calls reusing one metadata fit, repeat-bind cache hit, receiver revalidation, incompatible receiving requirements, unrelated update, dependency invalidation, revocation, and denial of a caller scope assertion. Both runtime objects were in one process.

Calibration checks full group equality against the reference for every eligible plan. The run completed, so those checks passed. Seeds for the 72 / 24 / 24 splits are disjoint. Event counts stay inside 800–14,000.

All 45 stress rows are present, one for each job, mode, and repeat. Within each shape, all 15 executions share one output signature. The signatures match the published digests:

| Shape | Groups | Retained events | Severity sum | SHA-256 |
|---|---:|---:|---:|---|
| repeated-shuffled | 49,367 | 651,662 | 1,301,787 | `b4976982669566fbb1f2493a27d35da50a2d7f71340b82d7e13400ff3e149ead` |
| diverse-shuffled | 712,972 | 713,608 | 1,427,605 | `2c52242c415917ec4ec967b9075f245d3591a6ea19979b867a147e985ef8ec11` |
| ordered-stream | 49,518 | 681,930 | 1,364,236 | `b7122424f5f2709f1d76339a0998084f9e3195492f9e301b8acd242fe043128e` |

The granularity tool checked 8,096 integer inputs and then 18 timed million-value runs. All checksums matched.

These checks cover the supplied jobs, the unit tests, and that integer microbenchmark. They are not a proof for every input, and they are not a security certification. The host remains an in-process prototype.

## Stress time and memory

Times are seconds. Each median is over three repeats. Minimum and maximum are the observed repeats, not a confidence interval. Pipeline time includes selection, feature inspection, inference, and AICC host setup when that mode uses them. It excludes model load and, for the two list jobs, list generation. The ordered-stream pipeline includes generator consumption for every mode. Whole-worker time is the parent-observed child duration. Peak MiB is the process-lifetime high-water working set divided by 1,048,576.

| Job | Mode | Plan | Pipeline median | Pipeline min–max | Worker median | Peak median MiB |
|---|---|---|---:|---:|---:|---:|
| repeated-shuffled | reference | reference | 2.872 | 2.859–3.083 | 4.606 | 814.0 |
| repeated-shuffled | static | partitioned | 1.364 | 1.324–1.553 | 3.047 | 559.9 |
| repeated-shuffled | aicc_static | partitioned | 1.328 | 1.324–1.404 | 3.021 | 560.1 |
| repeated-shuffled | learned | partitioned | 1.447 | 1.342–1.473 | 3.079 | 562.0 |
| repeated-shuffled | aicc_learned | partitioned | 1.394 | 1.370–1.544 | 3.075 | 562.4 |
| diverse-shuffled | reference | reference | 3.763 | 3.600–3.910 | 7.861 | 1057.4 |
| diverse-shuffled | static | partitioned | 2.717 | 2.714–2.722 | 6.656 | 844.9 |
| diverse-shuffled | aicc_static | partitioned | 2.738 | 2.684–2.752 | 6.655 | 843.9 |
| diverse-shuffled | learned | partitioned | 2.715 | 2.715–2.971 | 6.793 | 847.0 |
| diverse-shuffled | aicc_learned | partitioned | 2.711 | 2.697–2.736 | 6.656 | 847.1 |
| ordered-stream | reference | reference | 3.268 | 3.259–3.462 | 3.620 | 513.7 |
| ordered-stream | static | ordered | 2.368 | 2.368–2.370 | 2.681 | 133.7 |
| ordered-stream | aicc_static | ordered | 2.385 | 2.362–2.421 | 2.702 | 133.5 |
| ordered-stream | learned | partitioned | 2.534 | 2.526–2.548 | 2.872 | 209.1 |
| ordered-stream | aicc_learned | partitioned | 2.633 | 2.537–2.672 | 2.999 | 209.4 |

Equal-job mix, the sum of the three per-job medians:

| Mode | Pipeline sum s | Versus reference | Worker sum s | Versus reference |
|---|---:|---:|---:|---:|
| reference | 9.903 | baseline | 16.087 | baseline |
| static | 6.449 | 34.9% less | 12.383 | 23.0% less |
| aicc_static | 6.452 | 34.8% less | 12.378 | 23.1% less |
| learned | 6.696 | 32.4% less | 12.745 | 20.8% less |
| aicc_learned | 6.738 | 32.0% less | 12.730 | 20.9% less |

`saved_percent = 100 * (baseline - candidate) / baseline`. Negative values are regressions.

Static versus reference, pipeline medians: repeated 52.5% less time and 31.2% less peak memory; diverse 27.8% less time and 20.1% less peak memory; ordered 27.5% less time and 74.0% less peak memory. That is the ordinary algorithm change. The static policy may use every applicable kernel. The reference arm is the global-sort flow.

AICC static versus the same ordinary static policy, pipeline medians: 2.6% less on repeated-shuffled, 0.8% more on diverse-shuffled, 0.7% more on ordered-stream. The repeated-shuffled static repeats span 1.324–1.553 seconds, so that 2.6% gap is inside one slow static repeat. Median host register-and-bind time across the 18 AICC workers was 0.822 ms (minimum 0.669 ms, maximum 1.232 ms). Binding cannot explain a 35 ms gap, and the gap favors AICC on only one of three jobs. Peak memory differs by less than 0.2% on every static-versus-AICC-static pair.

Learned versus static, pipeline medians: 6.1% more time on repeated-shuffled, 0.1% less on diverse-shuffled, 7.0% more on ordered-stream. On ordered-stream the network chose `partitioned` even though the ordered plan was eligible, and peak memory rose from 133.7 MiB to 209.1 MiB (56.4% more). Whole-worker time moved in the same direction as pipeline time on that job.

AICC learned versus ordinary learned follows the same plans. Pipeline medians: 3.7% less, 0.1% less, and 3.9% more. Those gaps are small next to the repeat ranges, except that ordered-stream AICC-learned is slower across its whole observed range than ordinary learned's median.

## Learning

Collection of the calibration timings took 8.224 seconds. The Adam fit itself took 0.157 seconds. Architecture: 8–32–16–3, 867 parameters, seed 7, 900 epochs attempted. Validation loss selected epoch 900, the last epoch, with validation loss 0.0987508174. The model was not retuned after the stress jobs.

The four training-set policies, summed kernel seconds: partitioned with ordered 0.494, partitioned without ordered 0.504, cached with ordered 0.511, cached without ordered 0.515. The fitted policy is the best of those four.

Held-out kernel-only sums, selection overhead excluded: learned 0.2003 s, static 0.1945 s, retrospective oracle 0.1932 s. Learned is 3.0% higher than static. The network matched the oracle on 10 of 24 held-out jobs. The oracle is a bound, not a runnable policy.

The million-event jobs are outside the 800–14,000 calibration range. On the ordered million-event job the extrapolation chose the slower, larger plan.

## Granularity

Separate warm in-process process. These times are not merged with the stress samples. Setup of the host happened before the timed loop.

| Mode | Median s | Min–max s |
|---|---:|---:|
| ordinary_split | 0.142 | 0.140–0.143 |
| ordinary_fused | 0.125 | 0.123–0.126 |
| aicc_split | 2.687 | 2.675–2.831 |
| aicc_fused | 1.410 | 1.341–1.419 |
| ordinary_batch | 0.108 | 0.105–0.109 |
| aicc_batch | 0.109 | 0.104–0.115 |

AICC split versus AICC batch is 24.7x on the medians. Ordinary batch and AICC batch differ by about 1%, and their ranges overlap. The batch path checks the binding on entry. Per-value calls check on every value. This run did not expire, revoke, or cancel a binding in the middle of a batch, so no mid-batch difference was observed. The unit tests do show that an expired or revoked per-call binding fails on a later call. A whole-batch call would not see a revocation that happens after entry until that call returns. There is no separate cancellation observation in this run.

## Claims

Supported on this machine, as descriptive results from three repeats:

- Eligible plans that the calibration runner executed matched the reference, the stress signatures agree within each shape, and the tests, binding scenarios, and granularity differentials passed.
- The ordinary static policy accounts for the large drop relative to the reference: 34.9% less summed pipeline median and 23.0% less summed whole-worker median, with large peak-memory drops on every shape.
- Batching removes most of the per-call host overhead in the microbenchmark. The ordinary batch function is as fast as the AICC batch call.

Contradicted as a benefit of AICC or of the learned selector:

- AICC binding does not add a consistent gain beyond the same ordinary optimized code. The measured bind is under 1 ms, and the pipeline deltas change sign across jobs.
- The learned selector does not beat the strongest simple policy once the comparison includes the held-out kernels, and it does not beat it on the end-to-end million-event jobs. Outside the calibration range it misses the ordered fast path.

Unresolved:

- Sub-percent AICC differences are smaller than the repeat spread. Three repeats on a busy host do not justify a significance label.
- Tokens, billed model cost, human review time, setup cost, maintenance, and any dollar savings were not measured. Processing percentages are not converted into money here.
- A domain guard was not built or tested. The published seeds are not a hidden evaluation set.

## Next experiment

This was not run. It would be a separate condition.

Hypothesis: falling back to the static policy when the event count is outside 800–14,000 avoids the partitioned choice on large ordered inputs.

Baseline: the unchanged static policy, partitioned, and ordered when declared. Candidate: this network plus that guard. Both use the same kernels.

Design: freeze the guard first. Evaluate on newly drawn descriptors and seeds, not seeds 1105, 2205, 3305, 71001, 72001, or 73001, with at least ten randomized repetitions, including ordered jobs larger than 14,000 events.

Accept only if the guarded candidate's median pipeline on those fresh large ordered jobs is no slower than the static policy by more than the static repeat range, and its median peak working set is no higher. Falsify the explanation if the candidate still selects a slower plan there, or if the guard changes in-range choices and raises held-out kernel time above the static policy.

The favored explanation of this run is the ordinary plan choice. A result that made AICC binding itself the source of the multi-second gap, with the same kernel on both sides and a gap larger than the repeat spread on every job, would falsify that explanation. This run does not show that gap.
