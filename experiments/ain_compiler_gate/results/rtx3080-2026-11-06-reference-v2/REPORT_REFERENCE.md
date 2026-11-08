# Compact source to native code reference test

6 November 2026. Research direction by Izik Bachar. Implementation and local execution by Codex with collaboration agents.

All 120 reference programs per condition were compiled with the same LLVM backend and checked against independently computed integer results. The observations below measure reference serialization and compilation. Learned candidate correctness is recorded by the separate adaptation run.

| Source | Mean full target tokens | Mean compact target tokens | Reduction | Compact prompt + target tokens | Native-correct programs | Compile seconds |
|---|---:|---:|---:|---:|---:|---:|
| python | 14.325 | 4.525 | 68.4% | 37.250 | 120/120 | 0.600 |
| ir | 92.925 | 5.325 | 94.3% | 36.050 | 120/120 | 0.588 |
| ain | 102.325 | 5.325 | 94.8% | 37.050 | 120/120 | 0.587 |

The full form is the earlier complete Python function or IR/AIN envelope. Compact Python supplies an expression in x. Compact IR and AIN supply the same sequence of accumulator operations and explicit integer literals. The compiler supplies the input/return convention, types, registers and envelope in every condition. All source forms use the same optimization and native-code backend.

Assembly was identical across the three compact forms for 120/120 tasks. Each compiled program was checked on 9 inputs, including the declared input limits. Generated assembly files and their token lengths are saved as diagnostic artifacts. Assembly is emitted by LLVM through ordinary CPU computation and requires zero additional model generation tokens.

The token reduction comes from the compact source contract. Changing only the compiler target leaves the model-facing source sequence to be counted in full. Compiler-generated assembly token counts describe its text size and carry no LLM inference charge in this pipeline.

## Measurement boundary

The tokenizer is `Qwen/Qwen2.5-1.5B` at revision `8faed761d45a263340a0528343f099c05c9a4323` with base vocabulary. Counts use `add_special_tokens=False`. Prompt and target totals include their actual concatenated text. Training/inference accounting belongs to the separate adaptation run. The full and compact target figures compare canonical reference programs with equivalent behavior.

Compilation time includes strict parsing, shared IR construction, verification, optimization, assembly emission and JIT setup as measured by the compiler. The few-instruction functions are too small for a useful end-to-end runtime speed claim through Python/ctypes call timing.

The semantic domain is integer input and literal magnitudes up to 1,000,000, with at most 16 operations. These bounds allow exact signed-64-bit native arithmetic for every admitted program. The earlier VM has broader integer semantics. All current reference tasks are affine arithmetic and some held-out compositions share net offsets. This screen provides limited generalization evidence.

The dataset and source hashes, versions and target information are preserved in `reference-manifest.json`. Every compiled row retains its token counts, native outputs and assembly hash in `reference-records.json`. The sample files show the same task at each source/compiler boundary.

Implementation follows the official [llvmlite native compilation example](https://llvmlite.readthedocs.io/en/v0.44.0/user-guide/binding/examples.html).
