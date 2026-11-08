# Compact AIN to native code learning test

6 November 2026. Research direction by Izik Bachar. Implementation, local execution and review by Codex with collaboration agents.

The compact compiler pipeline executed successfully. After matched adaptation, Python and readable IR each solved 24/24 tasks, and numeric AIN solved 23/24. AIN and IR generated the same number of output tokens. The reference measurement shows that supplying predictable scaffolding through a compiler greatly reduces source length across the controls.

| Adapted condition | Development | Held-out compositions | Generated tokens | Generation seconds | Compiler seconds |
|---|---|---|---|---|---|
| python | 12/12 | 12/12 | 169 | 7.732 | 0.132 |
| ir | 12/12 | 12/12 | 201 | 9.337 | 0.141 |
| ain | 12/12 | 11/12 | 201 | 9.164 | 0.131 |

Every adapted task was attempted, with zero stage timeouts and zero output-cap hits. Generated-token totals include EOS. Canonical reference target counts exclude EOS.

AIN's single error was `3 6;3 12` for a task requiring `3 6;2 12`. It parsed and compiled successfully, then subtracted twelve where addition was required.

The [reference compiler report](../rtx3080-2026-11-06-reference-v2/REPORT_REFERENCE.md) records mean target lengths of 102.325 tokens for full AIN and 5.325 for compact AIN, a 94.8% reduction. Compact readable IR also averages 5.325 tokens, while compact Python averages 4.525. All 360 reference programs passed nine native execution cases each. Equivalent reference programs emitted identical assembly across all three frontends.

The token reduction comes from the compact input/return and register/type convention shared by the frontends. The LLVM backend emits assembly through ordinary CPU work and consumes zero additional LLM generation tokens. The small observed IR/AIN timing difference supplies little evidence about repeatable speed differences.

## Frozen local run

Codex selected the same Qwen2.5-1.5B checkpoint, the arithmetic subset and the bounded run settings within the user's request. The manifest identifies the checkpoint revision, source/data hashes, GPU and package versions. The model uses BF16 with rank-16 LoRA on query/value projections, seed 20261106 and learning rate 0.001. Each arm received 96 paired training tasks repeated three times. The fixed checkpoint was evaluated using task requirements and a format label, with no recurring manual.

The frozen limits were 256 training positions, 64 generated positions per task, 300 training seconds per arm, 120 evaluation seconds per stage, a 600-second hard process limit and a 7.8 GiB CUDA reserved-memory limit. Development passes at 9/12. All three arms met that threshold. All three completed 288 presentations and 72 updates.

| Condition | Training seconds | Processed tokens | Supervised tokens | Peak CUDA reserved GiB |
|---|---|---|---|---|
| python | 70.985 | 10740 | 1482 | 3.398 |
| ir | 68.718 | 10356 | 1674 | 3.398 |
| ain | 68.291 | 10644 | 1674 | 3.398 |

Training-token presentations measure local exposures, including prompt positions. Training timings exclude setup, evaluation and adapter saving. CUDA peaks exclude desktop applications and other processes. Raw results retain model-loading times, loss updates and parameter counts.

## All-attempt evaluation ledger

| Condition | Stage | Correct / assigned | Input tokens | Output tokens | Generation seconds | Judge seconds | Generation + judge seconds per correct task |
|---|---|---|---|---|---|---|---|
| python | before | 1/24 | 841 | 1327 | 60.817 | 0.055 | 60.873 |
| python | after | 24/24 | 841 | 169 | 7.732 | 0.136 | 0.328 |
| ir | before | 0/24 | 793 | 1222 | 56.369 | 0.043 | undefined |
| ir | after | 24/24 | 793 | 201 | 9.337 | 0.144 | 0.395 |
| ain | before | 0/24 | 817 | 1536 | 70.264 | 0.044 | undefined |
| ain | after | 23/24 | 817 | 201 | 9.164 | 0.134 | 0.404 |

Judge time includes parsing, failed parsing attempts, compilation and nine native execution checks. Compiler time is a component of judge time for compiled candidates. Each stage's totals include unsuccessful predictions. All assigned examples were attempted. Development-assistant work and initial environment setup are outside this local evaluation ledger.

## Instrument repair and retained attempts

The first compiler review found a Python parser depth limit that rejected sixteen signed operations while the compact frontends accepted that boundary. The initial learning attempt was stopped before adaptation. The parser was repaired, a boundary regression was added, all nine compiler/data tests passed, and fresh reference and learning manifests were frozen. The arithmetic evaluation tasks use one or two operations.

The interrupted baseline consumed 271 input tokens, 412 output tokens and 19.328 generation seconds across 8 saved predictions. Its raw observations and interruption record are retained under `aborted-v1`. The earlier reference run is also retained with a pointer to the repaired instrument's report.

## Scope and reproducibility

This screen reuses the previous gate's development tasks and composition holdouts for engineering diagnosis. Every task is an affine integer transformation, several net offsets repeat, and there is one training seed. The pretrained checkpoint's Python familiarity affects the comparison. The compact parser also supplies stronger structural constraints than the earlier full-envelope interface, equally across arms.

The prior full-envelope run used different evaluation time and output caps. Its comparison with this run describes an engineering change involving representation, constraints and budgets. The within-run controls share the compiler and limits. Whole-agent memory, tools, change/repair/handoff chains and broad efficiency still require the larger experiment.

The exact native domain admits at most sixteen add/subtract operations with input and literal magnitudes bounded by one million. This bounds intermediates safely inside signed 64-bit arithmetic. Runtime behavior was checked on native code. The few-instruction functions and Python call overhead provide limited runtime benchmarking value.

The original SDPA warning is preserved in each arm log. The pinned model configuration has sliding-window attention disabled. Raw predictions were replayed during export, including assembly hashes, and all frozen source/data hashes matched. Adapter files are stored in local scratch. `example.ain`, `example.ll` and `example.s` show a complete compact-source-to-native example with `2 7;3 4` computing `x+3`.
