# AICC processing study: independent replication report

**Run ID:** `anthropic-claude-opus-5.5-2026-11-05-trackA-002` (primary). `…-trackA-001` is preserved as an incomplete run.

**Track:** **A**, local recalibration and retraining with the original configuration.

**Agent:** Anthropic, Claude Opus 5.5, in a claude.ai chat with a Linux code sandbox. Identity is **self-reported**. One authoring session; no other provider participated.

**Status:** CODE EXECUTED. Correctness tests, 45 stress workers, the granularity microbenchmark and 9 runtime-state checks all completed in this environment. Two additional post-replication probes (sections 7 and 8) are labelled as such.

**Upload:** first returned as a patch, because the assignment's guardrail forbids using the pasted chat token. Then pushed to branch `claude/processing-study-replication` on 2026-11-05 **at the repository owner's explicit request**, overriding that guardrail. Not merged.

## Summary

| Question | Short answer from my measurements |
|---|---|
| Equal outputs; all tests pass? | **Yes.** 44/44 unit tests passed (exit 0). All 15 executions per job had identical output signatures, **byte-identical to the original Windows run** (same group counts, retained events, severity sums and SHA-256). 9/9 runtime-state checks passed |
| Time and memory changes | Ordinary optimisation (reference → static) cut pipeline time by **22.0–53.9%** and peak memory by **20.5–73.5%**, consistent with the original. AICC around the same code: **no consistent effect** (−0.5% to +7.5% pipeline; the same-code noise floor is about ±10%) |
| Consistent AICC benefit beyond the same ordinary code? | **No.** AICC-versus-ordinary differences change sign between jobs, runs and machines. Three repetitions on a shared host cannot resolve effects this small. Register plus bind cost 0.92 ms (median) |
| Learned selector vs strongest simple policy | **Does not beat it.** Held-out kernel time: one retraining was 2.83% worse, the other tied (0.00%); the original was 0.94% worse. Outside the training range, the original model and one retraining chose a plan **30.1% slower** at 1M ordered events (probe, section 7) |
| Does batching reduce invocation overhead? | **Yes, but it recovers AICC's own overhead.** AICC split / AICC batch = 28.8×; AICC batch ≈ ordinary batch (1.000×). Each bound call costs about 1.7 µs. With entry-only checks, a batch **continued for 700–750 elements after revocation, expiry or cancellation** (probe, section 8) |
| Cost, tokens, training, maintenance | Measured: calibration collection 12.56 s, training 0.155 s, unit tests 0.33 s, run wall clock about 5.4 min. **Not measured:** model tokens, billing, human time, registry maintenance. No economic claim is supported |

---

## 1. Provenance

| Item | Result |
|---|---|
| Checkout | Fresh `git clone --branch research/processing-and-learning-study`, HEAD `63d012095a6db66a71918cb574fb2c6ceaecf147` |
| Relation to frozen commit `75de32b` | Ancestor confirmed. Changes since then: 9 documentation files only, no Python |
| 11 measured Python sources | **11/11 match** `run-config.json` and `run-metadata.json`, before and after the run; no extra Python files in the study directory |
| 21 original result assets | **21/21 match** `checksums.json`. Verified read-only (`tools/verify_provenance.py`); the repository validator, which rewrites checksums, was not used |
| Granularity tool | `tools/processing_granularity.py`, sha256 `2337e492…`, unchanged since `75de32b` |
| Raw-versus-summary audit | Every original table value (medians, ranges, equal-job sums, the 1.6723 ms bind median) **recomputed exactly** from `stress-raw.json` by `tools/analyze_run.py`. No disagreement between the published summary and raw data |
| My model and policy | `cost-network.json` sha256 `a70f97d9…08915`; `static-policy.json` sha256 `2e5f242b…052d9`; both **trained in this run** |

## 2. Environment and commands

| Field | Value |
|---|---|
| OS | Linux 6.18 (x86_64, glibc 2.39), sandbox VM |
| CPU / logical CPUs / RAM | Intel Xeon @ 2.10 GHz / **1** / 3.9 GiB, no swap |
| Python / NumPy / Unicode / BLAS | **3.12.3** / 2.3.5 (lock file) / 15.0.0 / scipy-openblas 0.3.30 |
| Threads | `OPENBLAS_NUM_THREADS = OMP_NUM_THREADS = MKL_NUM_THREADS = 1`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1` |
| Host activity | No other workload ran during measured workers; one vCPU makes concurrency impossible. Not frequency-pinned |

**Commands (UTC, 2026-11-05):**
1. Unit tests, ending 15:17:35.484, exit 0. From `experiments/processing_study`: `../../.venv/bin/python -m unittest discover -s tests -v`
2. Track A run 002, 15:23:45.130 → 15:29:08.662, exit 0. `../../.venv/bin/python -u run_study.py --output results/anthropic-claude-opus-5.5-2026-11-05-trackA-002 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900`
3. Granularity, ending 15:29:48.536, exit 0. From the repository root: `.venv/bin/python tools/processing_granularity.py --output experiments/processing_study/results/anthropic-claude-opus-5.5-2026-11-05-trackA-002/granularity.json --events 1000000 --repeats 3`

**Failure, preserved and excluded.** Run 001, with identical arguments, was started in the background. The sandbox ended its process tree when the starting tool call returned, after calibration, training, binding scenarios and 5 of 45 workers. No exit status was written. Its directory is preserved **unchanged** and excluded from the primary comparison. Run 002 was started detached (`setsid`) into a new directory. Run 001's learning report is a complete second training, used only in section 6.

## 3. Correctness

- **Unit tests:** 44 run, 44 passed, 0 failed, 0 skipped, 0.330 s, exit 0 (`logs/unit_tests.log`).
- **Matrix:** 45 rows, 45 unique (job, mode, repeat) combinations, all output signatures identical within each job.
- **Cross-machine determinism:** all three job signatures are byte-identical to the original Windows run.

| Job | Groups | Retained events | Severity sum | SHA-256 |
|---|---|---|---|---|
| repeated-shuffled | 49,367 | 651,662 | 1,301,787 | `b4976982…` |
| diverse-shuffled | 712,972 | 713,608 | 1,427,605 | `2c52242c…` |
| ordered-stream | 49,518 | 681,930 | 1,364,236 | `b7122424…` |

- **Runtime-state checks:** 9/9 passed (`binding-scenarios.json`). The record's scope string still reads "new host processes", the same wording error the protocol notes; both Runtime objects are in one process.
- **Granularity:** 8,096 differential cases, all outputs equal.

## 4. Time and memory (Track A run 002; 3 repetitions per cell; min–max are observations, not confidence intervals)

| Job | Mode | Plan | Pipeline median s | Pipeline min–max | Worker median s | Worker min–max | Peak MiB | CPU s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| repeated-shuffled | reference | reference | 4.878065 | 4.643–4.993 | 7.161033 | 6.998–7.529 | 815.691 | 4.765 |
| repeated-shuffled | static | partitioned | 2.249717 | 2.079–2.319 | 4.524440 | 4.493–4.531 | 561.859 | 2.189 |
| repeated-shuffled | aicc_static | partitioned | 2.081067 | 2.042–2.220 | 4.396034 | 4.306–4.646 | 561.629 | 2.073 |
| repeated-shuffled | learned | partitioned | 2.292245 | 2.160–2.543 | 4.669369 | 4.363–4.954 | 564.164 | 2.145 |
| repeated-shuffled | aicc_learned | partitioned | 2.056383 | 2.012–2.243 | 4.277496 | 4.248–4.615 | 564.152 | 2.010 |
| diverse-shuffled | reference | reference | 6.269454 | 5.943–6.324 | 12.348188 | 11.888–12.818 | 1065.133 | 6.081 |
| diverse-shuffled | static | partitioned | 4.890549 | 4.871–5.731 | 11.288800 | 11.262–13.313 | 847.219 | 4.871 |
| diverse-shuffled | aicc_static | partitioned | 4.888657 | 4.788–5.047 | 11.364002 | 11.010–11.428 | 847.102 | 4.810 |
| diverse-shuffled | learned | partitioned | 4.999052 | 4.790–5.052 | 11.350079 | 11.016–11.782 | 849.434 | 4.950 |
| diverse-shuffled | aicc_learned | partitioned | 4.848849 | 4.839–5.051 | 11.347210 | 11.157–11.401 | 849.430 | 4.818 |
| ordered-stream | reference | reference | 5.148346 | 4.958–5.194 | 5.547906 | 5.343–5.594 | 515.688 | 4.934 |
| ordered-stream | static | ordered | 3.242011 | 3.192–3.584 | 3.582584 | 3.579–3.970 | 136.613 | 3.232 |
| ordered-stream | aicc_static | ordered | 3.258051 | 3.160–3.405 | 3.602285 | 3.525–3.755 | 136.777 | 3.242 |
| ordered-stream | learned | **ordered** | 3.139076 | 3.045–3.176 | 3.468085 | 3.378–3.553 | 139.141 | 3.124 |
| ordered-stream | aicc_learned | **ordered** | 3.347395 | 3.168–3.495 | 3.697820 | 3.531–3.890 | 139.305 | 3.246 |

Peak memory is the process-lifetime high-water RSS from `resource.getrusage` on Linux, which is not the same accounting as Windows `PeakWorkingSetSize`.

### Comparisons (saved % = 100 × (baseline − candidate) / baseline; negative is a regression)

| Job | Baseline → candidate | Attribution | Pipeline saved | Worker saved | Peak MiB saved | Original pipeline saved |
|---|---|---|---:|---:|---:|---:|
| repeated | reference → static | Ordinary optimisation | **53.88%** | 36.82% | 31.12% | 48.23% |
| repeated | static → aicc_static | AICC binding, same code | 7.50% | 2.84% | 0.04% | −0.03% |
| repeated | static → learned | Learned vs static | −1.89% | −3.20% | −0.41% | 1.35% |
| repeated | learned → aicc_learned | AICC binding, same code | 10.29% | 8.39% | 0.00% | −13.92% |
| repeated | reference → aicc_static | Complete path | 57.34% | 38.61% | 31.15% | 48.21% |
| diverse | reference → static | Ordinary optimisation | **21.99%** | 8.58% | 20.46% | 25.80% |
| diverse | static → aicc_static | AICC binding, same code | 0.04% | −0.67% | 0.01% | −1.38% |
| diverse | static → learned | Learned vs static | −2.22% | −0.54% | −0.26% | 2.53% |
| diverse | learned → aicc_learned | AICC binding, same code | 3.00% | 0.03% | 0.00% | −5.65% |
| diverse | reference → aicc_static | Complete path | 22.02% | 7.97% | 20.47% | 24.78% |
| ordered | reference → static | Ordinary optimisation | **37.03%** | 35.42% | 73.51% | 30.93% |
| ordered | static → aicc_static | AICC binding, same code | −0.49% | −0.55% | −0.12% | 1.09% |
| ordered | static → learned | Learned vs static | 3.18% | 3.20% | −1.85% | −11.93% |
| ordered | learned → aicc_learned | AICC binding, same code | −6.64% | −6.62% | −0.12% | 9.40% |
| ordered | reference → aicc_static | Complete path | 36.72% | 35.07% | 73.48% | 31.68% |

### Equal-job mix (sum of three per-job medians; descriptive, not a pooled estimator or bill)

| Mode | Sum pipeline s | vs reference | Sum worker s | vs reference | Original pipeline / worker |
|---|---:|---:|---:|---:|---:|
| reference | 16.295865 | — | 25.057127 | — | — |
| static | 10.382276 | 36.29% | 19.395824 | 22.59% | 33.73% / 20.79% |
| aicc_static | 10.227775 | 37.24% | 19.362322 | 22.73% | 33.59% / 18.26% |
| learned | 10.430373 | 35.99% | 19.487533 | 22.23% | 31.80% / 17.67% |
| aicc_learned | 10.252627 | 37.08% | 19.322526 | 22.89% | 30.79% / 19.33% |

**Interpretation.** The ordinary flow optimisation replicates closely; memory reductions match the original to within 0.3 points. The **learned → aicc_learned** row compares identical plans and models, so its spread (−6.6% to +10.3% here, −13.9% to +9.4% originally) measures noise for the same code. Every AICC-versus-ordinary difference falls inside that band and changes sign across jobs, runs and machines. My equal-job mix shows AICC 0.95 points ahead of static on pipeline time, while the original showed it 0.14 points behind; neither is an AICC effect.

**Measured AICC host cost:** register and bind median **0.9166 ms** (max 4.90 ms; original 1.6723 ms), with `full_validations` = 1 per AICC worker.

**Learned-mode overhead:** feature inspection 0.80 ms and inference 0.26 ms (medians), plus model load 7.27 ms outside the pipeline.

## 5. Absolute speed differs by machine; do not compare across agents

My reference pipeline medians (4.88, 6.27 and 5.15 s) are faster than the original's (6.23, 8.65 and 7.80 s) on different hardware and OS. Per the protocol, only same-machine comparisons support attribution.

## 6. Learning (Track A: actual training executed in this run)

| Item | Original | My run 001 (training complete; stress incomplete) | My run 002 (primary) |
|---|---:|---:|---:|
| Calibration collection s | 19.603 | 12.605 | 12.560 |
| Training s | 0.321 | 0.146 | 0.155 |
| Epochs attempted / selected | 900 / 164 | 900 / 415 | 900 / 456 |
| Validation loss | 0.1913 | 0.1521 | 0.1361 |
| Held-out learned kernel s | 0.457297 | 0.267810 | 0.255129 |
| Held-out static kernel s | 0.453058 | 0.260453 | 0.255130 |
| Learned vs static | **+0.94% worse** | **+2.83% worse** | **tie (−0.0001%)** |
| Held-out oracle s / matches | 0.422301 / 11 of 24 | 0.255118 / 13 of 24 | 0.251681 / 15 of 24 |
| Static policy | partitioned; ordered when declared | same | same |

- **Held-out kernel time:** in three trainings the selector never beat the static policy (worse twice, tied once). These held-out figures exclude selection overhead.
- **End-to-end stress (run 002):** learned mode was slower than static on two jobs (−1.9%, −2.2%) and faster on ordered-stream (+3.2%). On that job both used the same `ordered` plan, so the difference is noise.
- **Instability:** retraining on the same data population and machine changed the selected epoch (415 vs 456), the held-out verdict, and, outside the training range, the plan chosen (section 7).
- **Splits:** 72/24/24 with seeds 1105/2205/3305, unchanged; no retuning after evaluation.

## 7. Outside the 800–14,000-event calibration range (post-replication probe, `tools/extrapolation_probe.py`)

**Design.** Each stress shape at 800, 14,000, 100,000 and 1,000,000 events. I took the choices of the original model, my run 001 and run 002 models, and the static policy. Every eligible plan was timed: median of 3, garbage collection before each, randomised order, **one warm process, list input for every shape, kernel only**. This deviates from the fresh-process, generator-based stress protocol.

**Regret = chosen plan time / best plan time − 1.**

| Events | Shape | Best plan | Original model | Run 001 | Run 002 | Static |
|---:|---|---|---|---|---|---|
| 800 | repeated | partitioned | cached +6.0% | cached +6.0% | cached +6.0% | **+0.0%** |
| 800 | diverse | partitioned | cached +2.5% | cached +2.5% | **+0.0%** | **+0.0%** |
| 800 | ordered | ordered | cached +14.7% | partitioned +7.1% | partitioned +7.1% | **+0.0%** |
| 14,000 | repeated | partitioned | +0.0% | +0.0% | +0.0% | +0.0% |
| 14,000 | diverse | partitioned | +0.0% | +0.0% | +0.0% | +0.0% |
| 14,000 | ordered | ordered | partitioned +6.3% | partitioned +6.3% | partitioned +6.3% | **+0.0%** |
| 100,000 | repeated | partitioned | +0.0% | +0.0% | +0.0% | +0.0% |
| 100,000 | diverse | **cached** | partitioned +8.1% | partitioned +8.1% | partitioned +8.1% | partitioned +8.1% |
| 100,000 | ordered | ordered | partitioned +9.5% | partitioned +9.5% | **+0.0%** | **+0.0%** |
| 1,000,000 | repeated | partitioned | +0.0% | +0.0% | +0.0% | +0.0% |
| 1,000,000 | diverse | partitioned | +0.0% | +0.0% | +0.0% | +0.0% |
| 1,000,000 | ordered | ordered | partitioned **+30.1%** | partitioned **+30.1%** | **+0.0%** | **+0.0%** |

**Findings:**
- The static policy was best in 11 of 12 cells. The models missed 7, 7 and 4 of 12.
- The models' main failure is ignoring the ordered fast path even when it is eligible, including **inside** the training range.
- At 1M ordered events, two of three trained models chose a plan 30.1% slower. This reproduces the original study's 1M ordered-stream misselection, and shows that whether it occurs depends on which retraining you happen to get.

## 8. Batching and authority checkpoints (post-replication probe, `tools/batch_checkpoint_probe.py`)

**Granularity measurements (in-process, warm, setup excluded):**

| Mode | Original median s | My median s |
|---|---:|---:|
| ordinary_split | 0.270652 | 0.168260 |
| ordinary_fused | 0.248713 | 0.138184 |
| aicc_split | 4.615543 | 3.533783 |
| aicc_fused | 2.286713 | 1.823978 |
| ordinary_batch | 0.192520 | 0.122542 |
| aicc_batch | 0.203634 | 0.122587 |

- AICC split / AICC batch: **28.8×** here, 22.7× originally.
- Ordinary split / ordinary batch: 1.37× here, 1.41× originally.
- AICC batch / ordinary batch: 1.000 here, 1.058 originally.
- Each bound call costs about **1.7 µs** here, 2.1 µs originally.

**Checkpoint observations.** The probe used the unchanged frozen Runtime with an injected fake clock (1 ms per element); 1,000 elements; the event at element 250 (or 300); 100-element chunks.

| Event | Per-call checks | 100-element chunks | Whole batch (entry check only) |
|---|---|---|---|
| Revocation at element 250 | stops at once (`StaleBinding`), 0 extra elements | 50 extra, then `StaleBinding` | **750 extra elements; the batch returns normally** |
| Expiry (TTL 0.3 s) | stops at element 300, 0 extra | 0 extra (expiry fell on a boundary) | **700 extra elements; returns normally** |
| Cancellation at element 250 | caller stops, 0 extra | 50 extra | **750 extra; no cancellation point exists** |

**Conclusion.** Batching does reduce invocation overhead, but its main effect is to remove the per-call cost AICC added; ordinary batching is equally fast. Entry-only checks make revocation, expiry and cancellation invisible for the rest of the batch. Chunking bounds the overrun at chunk size minus one, for about 1.7 µs of checking per chunk. A batching contract must state that bound as an observable.

## 9. Cost and economics

**Measured:**
- calibration collection 12.56 s and training 0.155 s (CPU, no GPU);
- unit tests 0.33 s;
- Track A wall clock about 5.4 minutes;
- granularity about 40 s;
- no model API calls inside the benchmark.

**NOT MEASURED:**
- my own authoring session's tokens and billing (the chat interface exposes no telemetry);
- human review time;
- registry setup and maintenance;
- failure and repair cost;
- hosting.

**No economic claim is supported** by this replication. Runtime percentages are not dollar savings.

## 10. Claims: supported, contradicted, unresolved

**Supported:**
- The four plans produce identical outputs on the three stress jobs, across machines and operating systems.
- Ordinary flow optimisation cuts pipeline time 22–54% and peak memory 20–74% on these shapes.
- AICC binding cost is about 1 ms per worker and does not change outputs.
- The 9 binding-state behaviours pass.
- Batching amortises per-call binding checks.

**Contradicted:**
- That AICC adds a measurable speed benefit beyond the same ordinary code. No consistent sign: the original's equal-job mix had AICC 0.14 points behind static, mine 0.95 points ahead, both within same-code noise.
- That the learned selector improves on the strongest static policy. It is worse or tied on held-out jobs in all three trainings, and worse in 4–7 of 12 extrapolation cells.

**Unresolved:**
- AICC effects smaller than about 10%. Three repetitions on a shared host are underpowered.
- Whether a domain guard would make learned selection worthwhile.
- Any lifecycle, authoring or economic benefit.
- Isolation or security beyond the in-process prototype.

## 11. Deviations and limitations

1. Python 3.12.3 instead of 3.12.14; Linux instead of Windows; 1 logical CPU instead of 12; RSS-based peak memory instead of PeakWorkingSetSize.
2. Run 001 incomplete (sandbox ended background processes); excluded and preserved; run 002 used a new directory.
3. The driver's `REPORT.md` and `run-metadata.json` are the frozen driver's own output; in this Track A run, training genuinely did execute.
4. The probes in sections 7 and 8 are post-replication analyses that use list input in one warm process, not the stress protocol. They were designed after seeing the original results but before running them; they are not preregistered.
5. Same-session, single-agent work. Seeds are public, so this is a remeasurement, not unseen-seed generalisation.

## 12. Proposed next experiment (declared here before any testing; none run)

**Hypothesis.** A guard that falls back to the static policy whenever the job declares `ordered`, or whenever `log_n` lies outside the training range, removes the learned selector's losses. Even then it will not beat the static policy by more than its own feature and inference cost of about 1 ms.

**Baseline and candidate.** Unchanged strongest static policy versus learned-plus-guard, with identical kernels and ordinary invocation.

**Evaluation design.**
- New, preregistered descriptor seeds, with sizes spanning 800 to 2,000,000.
- At least 30 fresh descriptors per size band.
- 10 randomised fresh-process repetitions per case on one exclusive host.

**Acceptance rule.** Accept the guard as useful only if the paired median end-to-end pipeline time across all cases improves on static by at least 2%, the bootstrap 95% interval excludes 0, and no single size band regresses by more than 2%.

**Falsification.** If the guarded selector never departs from the static choice, or departures do not save more than the selection overhead, then learned selection adds nothing here, and the favoured explanation (the model only fails out of domain) is wrong.
