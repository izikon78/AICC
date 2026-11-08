# Supplementary final-study checks

Use these commands from the extracted packet root. Choose separate environments
for CPU accounting, plotting and CUDA adaptation so package changes do not alter
another experiment's recorded environment.

## Matched local text comparison

After setup, use the pinned CPU environment and bundled tokenizer,

```text
python scripts/run_representation_comparison.py --output work/text-comparison-001
```

An existing prepared environment can add `--current-python`. This route compares
five local representations of the same correct workflow traces, validates decoded
execution and saved state, and counts complete literal fixture contexts. It makes
no model calls. The protocol, raw strings and observed results are under
`experiments/representation_comparison/`. Its related-work discussion does not
claim that the named third-party systems were executed.

## Compact compiler and scalar data

The compiler maps all three source forms through the same typed IR and LLVM
backend. The admitted domain has at most sixteen add/subtract operations and
input/literal magnitudes of at most one million.

```text
python -m pip install llvmlite==0.44.0
python -m unittest experiments.native_learning_gate.test_data experiments.ain_compiler_gate.test_compiler experiments.ain_compiler_gate.test_data -v
```

The fourteen checks cover the semantic data, rejected unsafe/malformed programs,
native bounds, engine lifetime and native execution of all compact reference
targets. They do not retrain a model. The final canonical reference records are
under `experiments/ain_compiler_gate/results/rtx3080-2026-11-06-reference-v2/`.

To regenerate token counts and native reference records with the pinned tokenizer
already seeded by setup,

```text
python scripts/run_native_reference.py --current-python --output work/native-reference-001
```

This saves a fresh native report. Assembly bytes and timings may vary with the
host/compiler build. Preserve them and compare semantic results and token-count
definitions rather than assuming cross-host timing equality.

## Rebuild the publication figures

After preserving an independent first seal, the optional chart route uses the
final raw records and the published chart-data snapshot,

```text
python -m pip install matplotlib==3.11.2
python tools/build_final_figures.py
```

Use a separate plotting environment. The builder verifies all directly used
frozen source hashes before rendering. The workflow illustration depicts the
proposed architecture and is separate from the four quantitative result charts.

## Processing and binding prototype

The packet retains the final original, Claude and Grok completed records under
`experiments/processing_study/results/`. Each complete record has forty-five
workers using the same three public synthetic dataset shapes/seeds. They are
within-host remeasurements, not independent hidden task sets.

```text
python -m pip install -r experiments/processing_study/requirements.lock.txt
python -m unittest discover -s experiments/processing_study/tests -v
python experiments/processing_study/run_study.py --help
```

The unit checks are a bounded CPU route. Use the run script's `--help` and saved
`run-config.json` to select a fresh full-run output folder and explicit scale.
The million-event study is substantially heavier than the unit checks. Rerun
only when that workload is intended. Preserve raw workers, setup/environment and
unsuccessful attempts. Compare each host's optimized paths against its own
reference. Windows working-set and Linux RSS peaks differ in definition.

## Saved adaptation screens and an optional fresh GPU run

Final full-format records are under
`experiments/native_learning_gate/results/rtx3080-2026-11-06/`. Final compact
records are under
`experiments/ain_compiler_gate/results/rtx3080-2026-11-06-learning-v2/`. The latter
retains its interrupted instrument-development attempt as provenance. Sources,
prompts/data, raw predictions, loss records, configuration, dependency locks and
manifests accompany the reports. Saved adapters and model weights are omitted.

For a fresh training execution inspect both `run.py --help` interfaces and frozen
manifests first. Use a separate CUDA environment with the recorded PyTorch,
Transformers, PEFT and Accelerate versions, obtain the pinned Qwen2.5-1.5B model
revision, and provide suitable GPU memory. The original host had an RTX 3080.
Training is an optional separate execution, never implied by packet verification
or the CPU reference replay. Keep all arms, budgets, unsuccessful predictions,
timeouts and setup/training/evaluation ledgers.

Both saved screens use one seed, reused affine arithmetic tasks and a pretrained
checkpoint with prior Python familiarity. The full/compact interfaces, constraints
and evaluation caps differ. A new run should preserve those facts or explicitly
version and report every change. Broader learned-agent efficiency remains a
separate proposed study.
