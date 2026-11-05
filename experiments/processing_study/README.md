# Larger processing, agent-designed optimization, and local neural selection

This is an executable engineering study of synthetic event processing. AI coding agents designed several equivalent code flows, an AICC binding host, and a small neural cost model that selects a flow. The study measures execution time, output equivalence, and process memory. It does not measure billed model tokens or establish that AICC lowers software-development cost.

## What was built

- Four equivalent processing plans: transparent global sorting; cached normalization with early filtering; per-key partitioning/sorting; and validated ordered streaming.
- A host for scoped, versioned capability bindings, selective invalidation, compatibility memoization, expiry/revocation, and receiver-revalidated JSON handoff.
- An actual locally trained NumPy neural network: eight inputs, two ReLU hidden layers of 32 and 16 units, and three predicted log-runtime outputs; 867 trainable parameters.
- A calibration/validation/test split of measured synthetic jobs, plus fresh-process million-event stress workloads.
- Differential/adversarial tests, numerical gradient checks, and deterministic binding-state scenarios.

Read the [kernel contract](KERNEL_CONTRACT.md) and [runtime contract](RUNTIME_CONTRACT.md) before interpreting results.

## Run

Python 3.12+ and NumPy are required for the learning study. Processing kernels otherwise use the Python standard library. There are no model API calls, credentials, external datasets, GPU requirements, or remote training services.

```shell
python -m unittest discover -s tests -v
python run_study.py --output results/my-run --events 1000000 --repeats 3
```

Run from this directory. Output must be a new directory so existing stress records are not overwritten. A smaller engineering smoke check can use `--events 3000 --repeats 1 --train-jobs 8 --validation-jobs 4 --test-jobs 4 --epochs 60`. Smoke results are development checks, not the primary study.

For reproducible timing, use one numerical-library thread (`OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`). Stress workers set these themselves and run sequentially in separate child processes, with randomized mode order. Other applications and operating-system activity are not controlled, so a few repetitions are descriptive measurements, not a statistical superiority claim.

## Fair comparisons

| Mode | Plan selection | Capability invocation |
|---|---|---|
| `reference` | Transparent original flow | Ordinary function |
| `static` | Best of four simple conditional policies selected on training measurements | Ordinary function |
| `aicc_static` | Identical static policy and same kernels | AICC binding |
| `learned` | Trained neural cost model | Ordinary function |
| `aicc_learned` | Identical neural model and same kernels | AICC binding |

All modes can use every applicable optimized implementation. The static policy can choose one unrestricted plan and optionally use the ordered path on declared ordered input. Its four candidate policies are evaluated on the complete training set; it is not deliberately weakened to help the neural network.

The reference-to-static comparison concerns ordinary algorithm optimization. Static-to-AICC-static concerns binding overhead under the measured setup. Learned-to-static concerns plan selection, including feature/inference overhead in stress runs. AICC-learned-to-learned concerns binding around the same selected kernel. These execution modes do not substitute for the planned independent A/A+/B agent lifecycle trial.

## Work and measurement scope

The complete stress configuration has three synthetic job shapes, five modes, and three repetitions: **45 executions of million-event inputs**. They reuse three matched datasets across modes/repetitions; this is not 45 million unique real-world events.

- Repeated keys with shuffled timestamps.
- More diverse keys/messages with shuffled timestamps.
- Ordered data consumed as a generator, including generation inside processing timing for every mode in that case.

For materialized-list cases, generation is measured separately from processing. Model loading and output hashing are also separately recorded. Parent worker wall time includes startup/imports, preparation, loading, processing, hashing, and serialization. Peak memory is the process-lifetime high-water working set, including inputs/outputs and imports; it is not isolated kernel allocation.

On Windows the memory field uses [`PROCESS_MEMORY_COUNTERS.PeakWorkingSetSize`](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters), expressed in bytes before conversion to MiB.

The ordered path validates every raw input timestamp, including filtered and duplicate rows. A sampled feature cannot prove global order. Exact deduplication and returned groups still require growing state, so streaming is not constant-memory.

`duplicate_rate` is the configured probability of referencing an earlier ordinal, not an exact observed duplicate fraction.

## Actual learning and its limits

Runtime labels come from actual kernel executions, with two timed samples per eligible plan. Training, validation, and test descriptor/seed populations are separate. Feature normalization and the simple policy use only training rows; epoch selection uses validation loss. Test rows are evaluated after model selection. A retrospective best-plan oracle is reported only as a bound, not as an executable agent.

Calibration sizes range from 800 to 14,000 events. Million-event performance is therefore a test of size extrapolation; the model is not retuned after seeing stress outcomes. Held-out calibration comparisons are kernel-only estimates excluding selection overhead. Stress results include bounded feature inspection, network inference, and applicable host registration/binding.

This is real local neural training, but it learns a cost model over supplied plans. It does not train an LLM or an AI-native operation-token language, invent a new algorithm, or demonstrate previously unknown human-level discoveries.

## Agent optimization and publishing a changed implementation

The [optimization record](OPTIMIZATION_LOG.md) explains the code-flow choices and the cold-setup issue found during development. Optimized code is allowed to improve shared capabilities, provided it preserves the caller's required observable behavior.

A changed implementation needs conformance checks, a new artifact/dependency identity, fresh measurements, and appropriate binding invalidation before reuse. The runtime records declared module/contract identities but does not automatically detect arbitrary mutations to all Python globals. Its host controls remain in-process; it is not production authentication, confidentiality, or effect isolation.

## Results

The measured large run is stored under [results/full-2026-11-05/](results/full-2026-11-05/). Start with its [interpretation and figures](results/full-2026-11-05/ANALYSIS.md) and [primary report](results/full-2026-11-05/REPORT.md), then inspect raw rows, calibration measurements, weights, training history, source hashes, and binding scenarios. Retain unfavorable results and small/noisy differences.

The optional [granularity study](../../tools/processing_granularity.py) compares tiny AICC calls, fused operations, and one whole-batch capability using identical mathematical outputs. It holds policy fixed; batching checks authority at entry and does not prove equal mid-batch revocation/expiry/cancellation behavior. A real batching contract must define those observables.

The binding scenario uses two Runtime objects in one Python process. The raw scenario scope string's word `processes` is a descriptive wording error; it is not evidence of a fresh OS-process or AI-provider handoff. All worker modes import NumPy through the common harness, which contributes to their recorded process working sets.

To regenerate interpretation and figures from recorded data, run `python tools/analyze_processing_study.py --results experiments/processing_study/results/full-2026-11-05` and `python tools/plot_processing_study.py --results experiments/processing_study/results/full-2026-11-05` from the repository root. Plotting requires the optional `requirements-plot.txt` dependencies. The measured Python/NumPy versions are recorded in run metadata; `requirements.lock.txt` pins the NumPy version used.

The paper's current economic and trained-native-language hypotheses remain open. Any observed faster processing must be attributed to the relevant algorithm, selector, or host comparison.
