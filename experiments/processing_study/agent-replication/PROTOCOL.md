# Exact test design and replication procedure

The version-one implementation and original data are identified by commit `75de32b757b8bdc43886213ee6b9dd9470717918`. Original artifacts live in [results/full-2026-11-05](../results/full-2026-11-05/). This packet specifies future work; publication of the instructions is not another experimental run.

## 1. What the completed study did

### Observable event-processing behavior

All four implementations accept events, a positive integer window, and a minimum severity. They validate every raw row, retain the first input occurrence of each exact event ID before filtering or sorting, normalize tags with NFKC/casefold/whitespace collapse, and preserve message case while collapsing its whitespace. They group by normalized device/kind/message using windows anchored at each group's first event with strict `timestamp - first < window`. Output creation order uses timestamp and original ordinal. Read the complete [kernel contract](../KERNEL_CONTRACT.md) for invalid inputs, precision, and ordering details.

The reference uses a global sort. Alternatives use cached normalization and early filtering, per-key partitioned sorting, or validated ordered streaming. Ordered execution checks every raw timestamp, including discarded rows; a descriptor or 512-row sample cannot prove that precondition. Dedupe/output state grows with unique IDs/groups, so streaming is not constant-memory.

### Five comparisons

| Mode | Selection | Invocation | Question |
|---|---|---|---|
| reference | Reference flow | Ordinary function | Original execution baseline |
| static | Best simple policy fitted on training data | Ordinary function | Value of conventional code optimization |
| aicc_static | Same static policy | AICC binding | Binding around the same optimization |
| learned | Local neural selector | Ordinary function | Value of learned plan choice |
| aicc_learned | Same neural selector | AICC binding | Binding around the same learned choice |

Every path has access to the same applicable optimized kernels. AICC host registration/binding is inside pipeline timing. The host declares source/contract dependencies and checks scoped/versioned compatibility. Its compatibility counter is not a semantic proof, authentication, or execution isolation.

### Calibration and actual training

- Split descriptor generator seeds: train `1105`, validation `2205`, test `3305`; each generates separate per-job event seeds. Counts: 72/24/24. Populations are public and seed-disjoint, not secret tasks.
- Event counts: 800, 1,800, 4,000, 8,000, 14,000. Keys: 4, 24, 128, or `n // 3`; earlier-ordinal reference probability: 0, 0.15, or 0.55; ordering: both; configured message length: 24, 96, or 384; window: 10, 60, or 600; minimum severity: 0, 1, or 2. Descriptors are in calibration.json.
- Each eligible optimized plan runs twice on a materialized job; order is randomized using `job.seed XOR 81231`, with garbage collection before each timed call. Median kernel time supplies the training label. Full output equality to the reference is checked. Ineligible ordered labels are masked, not imputed.
- Eight features inspect at most 512 rows: log event count, device/message/ID ratios, log average message length, qualified fraction, declared order, and log window. Streaming samples are replayed.
- Model: 8–32–16–3, two ReLU hidden layers, 867 parameters, seed 7; Adam with learning rate 0.006; masked MSE on normalized log-runtime labels; gradient clipping at 10. Normalization is fitted on training rows only. Validation chooses the saved epoch from 900 attempted epochs. Test rows are evaluated after selection. The retrospective oracle is only a bound.
- The static baseline exhaustively evaluates four policies: cached or partitioned for general input, each with ordered substitution enabled or disabled. It minimizes summed training kernel time. Do not weaken this baseline to favor learning.

### Million-event stress jobs

| Job | Events | Keys | Earlier-ordinal reference probability | Ordered | Configured message length | Window | Minimum | Event seed | Input |
|---|---:|---:|---:|---|---:|---:|---:|---:|---|
| repeated-shuffled | 1,000,000 | 64 | 0.15 | false | 24 | 600 | 1 | 71001 | Materialized list |
| diverse-shuffled | 1,000,000 | 100,000 | 0.05 | false | 64 | 60 | 1 | 72001 | Materialized list |
| ordered-stream | 1,000,000 | 32 | 0.10 | true | 96 | 600 | 1 | 73001 | Generator |

The probability field is the generator's chance to reference an earlier ordinal, not an exact observed duplicate fraction. A configured message length is a generator parameter, not a guarantee that every string has exactly that length.

The Cartesian product is 3 jobs × 5 modes × 3 repetitions = 45 executions. Task order is shuffled with seed `441105`. Each task runs sequentially in a fresh child process with a 180-second timeout. Each workload uses the same descriptor/seed in every mode/repetition. All output summary fields and SHA-256 digests must match within a workload. Inputs are synthetic; sizes exceed the calibration range and therefore test extrapolation.

### Correctness, runtime state, and invocation granularity

The [44-method inventory](TEST_INVENTORY.md) covers 16 kernel tests, 24 runtime tests, and 4 learning tests, with further subcases inside methods. The kernel differential test uses 150 seeded populations, shuffled and sorted, plus explicit boundary/Unicode/invalid-input cases. Learning tests include masked finite-difference gradients, save/load equality, training-loss decrease on a synthetic target, invalid timing rejection, and strongest-static-policy fitting.

Nine additional deterministic scenarios check cold binding; 20 calls reusing one metadata fit; repeat-bind caching; receiver revalidation; incompatible receiving requirements; unrelated update survival; relevant dependency invalidation; revocation; and denial of caller-asserted authority. They are two Runtime objects in one process. The raw scope string says "processes" in error; it is not a fresh-process/provider handoff.

The separate granularity tool computes `stage_one(x) = (17*x + 3) % 65521`, followed by `stage_two(x) = ((x XOR 12345) * 7) % 65521`. It compares ordinary/AICC split calls, fused calls, and whole-batch execution. There are 8,096 differential integer inputs (4,096 consecutive values and 4,000 seeded random values) and 18 timed runs (6 modes × 3 repetitions) of one million values. One warm host is reused, setup is excluded, and mode order is randomized using seed `5191` after generating check inputs. Batch authority is checked at entry; repeated calls check repeatedly. These are not equivalent mid-batch expiry/revocation/cancellation guarantees.

## 2. Acquire and verify the source

Use a fresh checkout or a clean separate worktree; do not overwrite someone else's working changes. The following commands start from a parent folder where a new `AICC` checkout can be created:

```shell
git clone --branch research/processing-and-learning-study https://github.com/izikon78/AICC.git
cd AICC
git rev-parse HEAD
git status --short
```

Record the actual checkout commit. Compare the eleven source entries in `run-config.json.source_sha256_before_run` with the current source and `run-metadata.json.source_sha256`. Compare all 21 original result assets against `checksums.json`. A documentation-only later commit is compatible if the measured sources and artifacts still match. Changed Python sources constitute a modified implementation, not the frozen replication.

The repository's `tools/validate_processing_study.py` checks the original record, but **rewrites checksums.json** and assumes 45 million-event rows, 72/24/24 splits, plus supplemental granularity/test records. Use it only on an appropriate copy; it is not a generic new-run validator. Do not treat its count assertions as independent proof of tests being executed. Verify new logs yourself. Do not put new Python helpers inside the study directory: the source manifest recursively includes Python files there.

Original measured environment: Python 3.12.14, NumPy 2.3.5, Unicode 15.0.0, Windows 11 build 26200, 12 logical CPUs. Other applications were not controlled. Hardware, OS, temperature, power settings, Python/Unicode/NumPy/BLAS versions, and available RAM can change results. Record yours; do not expect equal absolute timings or the same fitted policy/epoch after remeasurement.

## 3. Set up and run correctness checks

Use Python 3.12+; the lock file pins the measured NumPy version. No GPU or paid model API is needed. Create a new virtual environment at the repository root.

PowerShell:

```powershell
python -m venv .venv
$aiccPython = (Resolve-Path .venv/Scripts/python.exe).Path
& $aiccPython -m pip install -r experiments/processing_study/requirements.lock.txt
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
Set-Location experiments/processing_study
& $aiccPython -m unittest discover -s tests -v
```

POSIX shell alternative, from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r experiments/processing_study/requirements.lock.txt
export PYTHONUTF8=1 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
cd experiments/processing_study
../../.venv/bin/python -m unittest discover -s tests -v
```

Capture stdout, stderr, command, start/end UTC, exit status, and test count. Stop the performance comparison on a correctness failure and preserve the failure. Do not copy the original test-verification.json and claim it is your execution record.

## 4. Choose a clearly labeled replication track

Replace `agent-id-run-001` with a unique identifier; never reuse an existing output path. The driver only refuses a directory containing stress-raw.json, so independently ensure your path is new. Run one benchmark at a time. Do not train, plot, install packages, or run other benchmark agents concurrently with measured workers.

### Track A: repeat the complete calibration/training procedure

From the study directory, in the PowerShell environment above:

```powershell
& $aiccPython -u run_study.py --output results/agent-id-run-001 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900
```

POSIX uses the identical arguments with `../../.venv/bin/python` instead of `& $aiccPython`. This is the original complete run configuration. New local timing labels can select a different policy, epoch, or plan. It reuses the published deterministic dataset seeds; it is a remeasurement, not unseen-seed generalization.

For an optional development smoke run, use a separate directory and `--events 3000 --repeats 1 --train-jobs 8 --validation-jobs 4 --test-jobs 4 --epochs 60`. Do not pool smoke results with the primary comparison.

### Track B: remeasure execution using the frozen trained model/policy

The CLI has `--reuse-model` but no model-directory option. It loads both policies from the new output directory. From the study directory, PowerShell:

```powershell
New-Item -ItemType Directory -Path results/agent-id-frozen-001 -ErrorAction Stop | Out-Null
Copy-Item results/full-2026-11-05/cost-network.json results/agent-id-frozen-001/
Copy-Item results/full-2026-11-05/static-policy.json results/agent-id-frozen-001/
Copy-Item results/full-2026-11-05/learning-report.json results/agent-id-frozen-001/
Copy-Item results/full-2026-11-05/calibration.json results/agent-id-frozen-001/
& $aiccPython -u run_study.py --output results/agent-id-frozen-001 --events 1000000 --repeats 3 --train-jobs 72 --validation-jobs 24 --test-jobs 24 --epochs 900 --reuse-model
```

POSIX uses `mkdir`, `cp` for the same four files, and the same Python arguments. Copy **only** those four artifacts; copying stress-raw.json will prevent the run. calibration.json is copied for provenance; the worker requires the model/policy and report generation requires learning-report.json.

The frozen driver report labels local neural training as executed even with reuse enabled. For Track B this is historical model provenance, **not a new training event**. Your accompanying report must explicitly correct this metadata limitation: training_executed_this_run=false, training cost this run zero for the reused model, original collection/training times historical, model/policy origins and hashes retained. Likewise the copied held-out learning report is historical, not a new held-out evaluation. Do not silently rewrite copied originals to hide that distinction.

## 5. Run the supplemental test and assemble measurements

Return to the repository root and use the same Python environment:

```powershell
Set-Location ../..
& $aiccPython tools/processing_granularity.py --output experiments/processing_study/results/agent-id-run-001/granularity.json --events 1000000 --repeats 3
```

For Track B substitute its output directory. This tool rejects an existing granularity.json. Its host is warm/in-process, unlike the fresh stress workers; do not merge these time samples.

The driver already produces binding-scenarios.json, raw/summary stress results, report, run configuration, and source metadata. Record your unit-test log separately. Verify all 45 unique `(job, mode, repeat)` combinations, their full output signatures, source hashes before/after, and model/policy hashes. Check artifact checksums without rewriting the original study.

Use [MEASUREMENTS.md](MEASUREMENTS.md) and [submission-template.json](submission-template.json) to build your report. The existing analyzer is tailored to the original run, includes an original-date heading and hard-coded expectations, and requires supplemental granularity.json. Do not present its generated original-date interpretation or copied unit-test record as a new experiment. A new analysis must state your run date, track, repetitions, provenance, and any deviations. Plots are optional and should be generated after timing; plotting requirements are separate from the training lock file.

## 6. Optional next experiments: propose, freeze, then evaluate

| Priority | Hypothesis and implementation | Required control/evidence |
|---|---|---|
| 1 | A guard that falls back outside the calibration domain can avoid poor neural choices | Declare the guard using training/development data; freeze it and test on fresh, preregistered descriptors/seeds; compare with the unchanged strongest static policy |
| 2 | AICC supports replacing a capability with a faster equivalent implementation | New implementation/source identity; conformance plus error/order/authority behavior; equal optimized implementation available to the ordinary control; report invalidation and setup effort |
| 3 | Coarse capabilities amortize dispatch cost at useful batch sizes | Sweep declared batch sizes, count/check time separately, retain ordinary batching, define/check expiry/revocation/cancellation checkpoints |
| 4 | Reuse lowers total authoring/lifecycle cost across independent agents | Execute the separately planned lifecycle trial with matched tasks, equal semantic evidence controls, actual token/billing/effort records, and failure/repair/maintenance costs |

The current CLI has no seed or workload-descriptor flags. New-seed/workload extensions therefore need a separately versioned driver/configuration and raw records; the public fixed benchmark is not a fresh holdout. Keep original results frozen. For any revised code, measure baseline and candidate under matched local conditions with at least ten randomized repetitions per case as a proposed precision improvement; this count alone does not guarantee statistical power. Define the sample size, comparison metric, and acceptance rule before inspecting new evaluation outcomes. Use paired effects and uncertainty only when the design supports them. Report inconclusive or negative outcomes without selecting only favorable modes or runs.
