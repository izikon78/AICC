# RTX 3080 learning feasibility gate

Prepared 6 November 2026 under Izik Bachar's research direction. Implementation
and execution by Codex, with collaboration agents reviewing data and protocol.

This screen implements the first local action in the RTX 3080 handoff. It checks
memory fit, throughput and executable learning on a narrow arithmetic subset.
The observable whole-agent experiment is specified in `WHOLE_AGENT_NEXT.md`.

## Frozen screen

- Base checkpoint `Qwen/Qwen2.5-1.5B`, revision
  `8faed761d45a263340a0528343f099c05c9a4323`, Apache 2.0.
- Sequential matched LoRA adaptations of Python, readable IR and numeric AIN.
  AIN is the existing IR's numeric spelling. No vocabulary changes.
- 96 paired training examples, 12 development examples using new constants,
  12 held-out operation compositions. All tasks simplify to affine functions,
  which limits the generalization evidence. Three passes, one fixed seed.
- Rank 16 LoRA on query/value projections, BF16, gradient checkpointing,
  microbatch one, four accumulated examples, learning rate 0.001.
- Maximum 512 positions, 320 generated positions, greedy decoding, one attempt.
  Evaluation prompts contain a task and output format label, with no manual.
- Five-minute training ceiling per arm, 90-second evaluation stage ceilings,
  600-second hard child-process ceiling per arm. Stage limits are checked
  between tasks/updates. Timeouts remain failed assigned examples.
- 7.8 GiB PyTorch reserved-memory ceiling, checked after smoke and each update.
  Device memory used by desktop applications is additional.
- Development correctness threshold 9/12 per representation. If AIN misses it,
  pause scaling under these settings. Holdout outcomes remain descriptive.
- No automatic hyperparameter retries or changes based on holdout results.

The Python judge accepts one `solve(x)` return expression containing integer
literals, addition and subtraction. IR/AIN use the existing validator and VM
with a 1000-instruction execution limit and empty capability catalog. Targets
include the complete numeric envelope and catalog hash. All formats are judged
against an independent arithmetic oracle on seven inputs. The Python subset
and the VM have different accepted syntactic forms, so syntax rates require
that qualification.

## Execution

From the repository root in PowerShell, after creating `.venv` and installing
the frozen dependencies (PyTorch uses the official CUDA 12.8 wheel index), run

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s experiments/native_learning_gate -p test_data.py -v
& .\.venv\Scripts\python.exe experiments/native_learning_gate/run.py
```

The default output is the ignored `work/rtx3080-gate-v1` directory. A manifest
records source/data hashes, checkpoint revision, package versions and hardware
before model training. Every prediction, failed attempt, loss trace, adapter
and result remains there. A fresh output directory is required for a full rerun.

Each representation starts from the same base. A backward-only smoke pass
measures fit without updating parameters. Baseline predictions are then saved,
followed by adaptation and the same evaluation tasks. Development and holdout
tasks are interleaved to distribute stage timeout exposure. Model selection
uses the fixed final checkpoint. The runner records actual presentations because
the time cap can give different exposure across arms.

Training throughput includes forward/backward, gradient clipping and optimizer
work. Token counts are descriptive within the unchanged tokenizer. Peak memory
covers model loading, smoke, training and evaluation. Inference latency uses
CUDA synchronization, while judging latency is recorded separately. Report
initialization/smoke and training separately. No claim about model-internal
symbolic computation, general agent efficiency or AICC reuse follows from this
screen. One seed and small related task sets provide development evidence.

Primary implementation references are the [Qwen model card](https://huggingface.co/Qwen/Qwen2.5-1.5B),
[PyTorch installation instructions](https://pytorch.org/get-started/locally/),
and [PEFT documentation](https://huggingface.co/docs/peft/quicktour).
