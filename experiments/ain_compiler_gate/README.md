# Compact AIN to native code screen

Prepared 6 November 2026 under Izik Bachar's research direction. Implementation
and execution by Codex with collaboration agents.

The user requested a test where the AI emits compact AIN and a conventional
compiler generates assembly. This experiment gives Python and readable IR the
same compiler services and measures both reference token lengths and a separate
matched local adaptation run.

## Source and execution contract

Each program takes one integer input `x` and returns the final accumulator.
The compact forms for adding seven and then subtracting four are

| Condition | Model-facing source |
|---|---|
| Python | `x+7-4` |
| Readable IR | `add 7;sub 4` |
| Numeric AIN | `2 7;3 4` |

Numeric opcodes 2 and 3 reuse the existing AIN add/sub meanings. The compiler
provides types, register declarations, constant materialization, the input and
return convention, and the empty capability catalog envelope. Literals and
operation order remain explicit in every source form. All forms lower through
the existing validated IR and then the same LLVM optimizer and native backend.

The admitted domain bounds input and literal magnitudes at 1,000,000 and program
length at 16 operations. This bounds every intermediate far within signed
64-bit native integer range. Invalid code is rejected before JIT execution.
Python accepts a restricted arithmetic expression and the matching plain
`solve(x)` wrapper. Strict parsing permits only the shared arithmetic subset.

The 96 training, 12 development and 12 held-out tasks reuse the earlier gate's
semantic tasks and split. All programs are affine transformations, and some
held-out compositions have identical net offsets. This is a small development
screen. The pretrained checkpoint's prior Python exposure also affects learning.

## Reference measurements

From the repository root after installing `llvmlite==0.44.0` in `.venv`, run

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s experiments/ain_compiler_gate -p 'test_*.py' -v
& .\.venv\Scripts\python.exe experiments/ain_compiler_gate/measure.py --output experiments/ain_compiler_gate/results/rtx3080-2026-11-06-reference-v2
```

The measurement command requires the pinned Qwen2.5-1.5B tokenizer to be cached.
It compiles all reference programs, executes native code on independent inputs,
counts full-envelope and compact source tokens, and saves assembly/LLVM examples.
It writes hashes, raw records and `REPORT_REFERENCE.md` under
`results/rtx3080-2026-11-06-reference-v2` with the command above. Choose a fresh
output directory for a rerun.

Compact reference strings establish their serialized length. Actual model
predictions and their correctness belong to the separate adaptation observations.
LLVM emits assembly using CPU computation. Its assembly text incurs zero
additional LLM output tokens in this pipeline. Source compression, model
inference, compilation and emitted-program execution are distinct measurements.

## Matched learning run

```powershell
& .\.venv\Scripts\python.exe experiments/ain_compiler_gate/run.py
& .\.venv\Scripts\python.exe experiments/ain_compiler_gate/summarize.py
```

The runner adapts matched copies of the pinned Qwen2.5-1.5B base sequentially on
the RTX 3080. Each arm receives 96 examples repeated three times with the same
rank-16 LoRA settings and seed. The frozen limits are 256 training positions,
64 generated positions, 300 training seconds per arm, 120 seconds per evaluation
stage and a 600-second hard process limit. The development threshold is 9/12.
The manifest freezes source/data hashes before training.

Raw predictions, loss traces and adapters are written under the ignored
`work/ain-compiler-gate-v2` directory. The exporter validates hashes and replays
every attempted prediction before copying small observations and writing
`results/rtx3080-2026-11-06-learning-v2/REPORT.md`. Initial interrupted observations
are retained with the report. Both commands require cached model dependencies
from the earlier local setup. The requirements lock records package versions.

These tasks reuse the previous experiment's development and holdout cases for
engineering diagnosis. Compact source, stronger structural constraints and
different evaluation caps all contribute to the change from that earlier run.

The backend follows the official
[llvmlite native compilation example](https://llvmlite.readthedocs.io/en/v0.44.0/user-guide/binding/examples.html).
