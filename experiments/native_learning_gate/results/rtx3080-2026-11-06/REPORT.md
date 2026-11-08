# RTX 3080 local learning feasibility gate

6 November 2026. Research direction and concept by Izik Bachar. Implementation, local execution and report preparation by Codex with collaboration agents.

The frozen development threshold was 9/12 correct tasks (75%) for each adapted condition. Every assigned task remains in the denominator, including timeouts and invalid outputs.

| Condition | Development gate | Correct after adaptation |
|---|---|---|
| python | Pass | 12/12 |
| ir | Pass | 10/12 |
| ain | Fail | 5/12 |

AIN missed the frozen development threshold. Scaling stopped at this gate. The memory-fit check succeeded, while executable learning under these particular data, adaptation and evaluation settings was insufficient for the next whole-agent trial.

This gate measures memory fit, local training throughput and executable language learning. Cost savings remain unestablished. The whole-agent experiment is specified in [WHOLE_AGENT_NEXT.md](../../WHOLE_AGENT_NEXT.md).

## Model and frozen setup

Model `Qwen/Qwen2.5-1.5B`, revision `8faed761d45a263340a0528343f099c05c9a4323`, Apache 2.0 license. The pretrained base checkpoint was adapted with seed 20261106, BF16, LoRA rank 16 and alpha 32 on `q_proj`, `v_proj`. The learning rate was 0.001. The tokenizer vocabulary and embeddings were retained.

The dataset contains 96 training, 12 development and 12 structural-holdout tasks. The target exposure was 3 passes, with 4 presentations per optimization update. Equivalent semantic examples were used across conditions. Numeric AIN is the existing readable IR's numeric serialization.

Codex selected the model, data and automatic caps within the user's request to run the handoff. The frozen caps were 300 seconds of training per condition, 90 seconds per evaluation stage, 512 training positions, 320 generated positions per attempt and 7.8 GiB of CUDA allocator reserved memory. The controller imposed a 600-second hard limit per condition. Soft limits were checked between tasks or updates. These were local execution choices, with no purchased GPU or API budget.

Hardware was NVIDIA GeForce RTX 3080 with 10.00 GiB device memory, 31.91 GiB system RAM and AMD Ryzen 5 5600X3D 6-Core Processor (6 cores, 12 logical processors). CUDA runtime 12.8, BF16 supported `True`. The GPU also served desktop applications during execution.

| Package | Recorded version |
|---|---|
| torch | 2.7.1+cu128 |
| transformers | 4.51.3 |
| peft | 0.15.2 |
| accelerate | 1.6.0 |
| huggingface-hub | 0.36.2 |

## Execution outcomes

The before stage used the unadapted checkpoint through zero-initialized LoRA updates. A smoke backward pass checked training compatibility without an optimizer update. Both evaluation stages used greedy generation, one attempt per task, and task requirements plus the requested output-format label. The fixed language manual was absent. Development and holdout tasks were interleaved.

| Condition | Stage | Split | Correct / assigned | Syntax valid | Attempted | Stage timeouts | At output cap |
|---|---|---|---|---|---|---|---|
| python | before | dev | 12/12 | 12 | 12 | 0 | 0 |
| python | before | holdout | 12/12 | 12 | 12 | 0 | 0 |
| python | after | dev | 12/12 | 12 | 12 | 0 | 0 |
| python | after | holdout | 12/12 | 12 | 12 | 0 | 0 |
| ir | before | dev | 0/12 | 0 | 6 | 6 | 0 |
| ir | before | holdout | 0/12 | 0 | 5 | 7 | 0 |
| ir | after | dev | 10/12 | 10 | 10 | 2 | 0 |
| ir | after | holdout | 5/12 | 10 | 10 | 2 | 0 |
| ain | before | dev | 0/12 | 0 | 12 | 0 | 0 |
| ain | before | holdout | 0/12 | 0 | 12 | 0 | 0 |
| ain | after | dev | 5/12 | 8 | 10 | 2 | 0 |
| ain | after | holdout | 2/12 | 6 | 9 | 3 | 0 |

Syntax validity includes the declared structural and type checks. A correct program must return exact integer results on every judge input. The Python evaluator accepts one restricted return expression, while the existing VM validates IR/AIN programs with bounded execution. Output-cap flags also include a completion ending exactly at that cap.

| Condition | Stage | Input tokens | Output tokens | Inference seconds |
|---|---|---|---|---|
| python | before | 889 | 353 | 16.062 |
| python | after | 889 | 417 | 18.726 |
| ir | before | 392 | 2,032 | 94.697 |
| ir | after | 731 | 2,007 | 92.962 |
| ain | before | 889 | 1,282 | 59.212 |
| ain | after | 693 | 2,028 | 95.128 |

Inference timings include generation and device synchronization. Raw prediction records retain judge timings. Attempted malformed and unsuccessful outputs contribute to these totals. Assigned tasks skipped at the stage ceiling have zero model work.

## Training and memory

| Condition | Presentations | Updates | Processed tokens | Supervised tokens | Training seconds | Processed tokens / second | Stop reason |
|---|---|---|---|---|---|---|---|
| python | 288 | 72 | 14,100 | 4,266 | 68.811 | 204.91 | epochs_complete |
| ir | 288 | 72 | 36,276 | 26,442 | 69.546 | 521.61 | epochs_complete |
| ain | 288 | 72 | 39,252 | 29,418 | 72.208 | 543.60 | epochs_complete |

Training tokens are repeated local model exposures, including prompt positions. Supervised tokens count target positions used by the loss. These token presentations are local computation and carry no ChatGPT token charge. Measured training throughput excludes download, model loading, the smoke pass, evaluation and saving. Token lengths and computation differ even when semantic exposure matches.

| Condition | Tokenizer vocabulary | Total parameters with LoRA | Trainable parameters | Smoke allocated GiB | Smoke reserved GiB | Full allocated GiB | Full reserved GiB |
|---|---|---|---|---|---|---|---|
| python | 151,665 | 1,545,893,376 | 2,179,072 | 3.311 | 3.379 | 3.311 | 3.402 |
| ir | 151,665 | 1,545,893,376 | 2,179,072 | 3.311 | 3.383 | 3.311 | 3.416 |
| ain | 151,665 | 1,545,893,376 | 2,179,072 | 3.311 | 3.383 | 3.311 | 3.416 |

Full peaks cover model loading, smoke, baseline evaluation, training and adapted evaluation in each condition's process. CUDA allocator measurements exclude desktop and other processes' device memory. The existing tokenizer and embedding vocabulary were used throughout, with no added instruction tokens.

Transformers emitted a sliding-window/SDPA compatibility warning in every arm. The pinned checkpoint configuration has `use_sliding_window` set to `false`. The configuration and original warnings are preserved with the observations.

## Setup recovery and provenance

The initial unchunked model-weight download failed. Recovery downloaded byte ranges, assembled the 3,087,467,144-byte weight file and verified its complete SHA-256 before loading. The verified digest was `a961db72e75d52b18e6b0c9d379e51a26973b233385e0e127fdda7d648aec796`. The checkpoint was obtained from [the pinned model revision](https://huggingface.co/Qwen/Qwen2.5-1.5B/tree/8faed761d45a263340a0528343f099c05c9a4323). Setup download attempts are separate from the training and inference timings above.

The starting repository commit was `60ba43bad3588815ecebe1504c35f2dfe7f0e97d`. `manifest.json` records the frozen source hashes, package versions and semantic dataset hash. This export retains the dataset, hardware records, process statuses, raw predictions, training updates, fit/result summaries and arm logs. Adapters and model weights remain in local scratch storage.

## Limits and next experiment

All tasks are affine integer transformations that simplify to an input plus a constant. Repeated net offsets occur, and the structural holdouts are surface compositions within this small semantic family. These observations support only the declared executable-fluency screen. One training seed and a tiny dataset provide limited evidence about variability. The pretrained model already has Python exposure.

This first gate covers code generation. The requested whole-agent comparison still requires learned observable records, memory, actions, tools, repair/change/handoff chains and several compositional domains, using the plan linked above. Correctness, all-attempt resources, learning amortization and uncertainty must be measured in that study before drawing an efficiency conclusion.
