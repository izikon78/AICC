# AIN research plan

Status update, 5 November 2026: the [first executable development study](../../experiments/ain_v0/FIRST_EXECUTION_REPORT.md) now implements the engineering foundation: Python, typed IR and numeric AIN controls; 69 passing tests; 27 matched processing workers; and six first-submission agent edits. Numeric AIN is a mechanical serialization control in this version and showed no execution saving. The larger version-pinned model comparison, matched adaptation and dedicated-token phases below remain proposed. No language-trained model was built.

**AIN is the working name for AI Native Language.** It is not a claim that the name is unique or that a new language has been validated. AICC remains the AI Computational Commons: the separate proposal for discovering, binding, and reusing governed capabilities.

## The question worth testing

Could a model create, understand, change, and repair substantial programs more reliably or with less total work when their executable representation is designed for machine use?

The hypothesis concerns a defined computational representation, not fewer printed characters. Numeric operation identifiers might tokenize poorly for an existing model. A compact program might also hide complexity inside a library, omit required behavior, or become harder to repair. All of those outcomes must remain possible.

AIN and AICC answer different questions:

| Proposal | Candidate benefit | Required comparison |
|---|---|---|
| AIN representation | Less work expressing and editing new computation, with preserved semantics | Different representations, equal libraries, contracts, tools, and task information |
| AICC reuse and binding | Less repeated implementation or compatibility work over a software lifecycle | Conventional reuse with the same implementations and semantic evidence |
| Algorithm improvement | Better equivalent execution flow | Give every representation and ordinary/AICC arm access to the same applicable optimization |

The [existing processing study](../../experiments/processing_study/README.md) measured conventional algorithm changes, local runtime-plan selection, and AICC invocation. Its small neural network predicts supplied plans. It provides no direct evidence that a model benefits from a native programming language.

## Begin with a difficult, reviewable task

Use the [streaming workflow contract](COMPLEX_TASK.md) as an initial task family: out-of-order events, watermarks, finite-horizon deduplication, deterministic grouping, private rules, bounded concurrency, cancellation, and atomic recovery. This is a new proposed contract, not a relabeling of the frozen million-event workload.

The task should force the representation to express control flow, state, effects, resource limits, and failure behavior. A one-line call to a supplied whole-workflow implementation is not an authoring result. Score the program the agent actually has to construct and maintain.

The first deliverable is a small, language-neutral semantic core and a readable reference implementation. Next come a typed conventional intermediate representation and an illustrative AIN encoding of the same core. A parser/interpreter must reject malformed or ill-typed programs deterministically before any model evaluation is called an executable language study.

## Keep three language experiments separate

### Phase A: existing models and existing tokenizers

Freeze a model version and evaluate four forms without changing its weights or tokenizer:

1. Idiomatic Python using the agreed typed boundary and libraries.
2. A conventional typed IR with readable operation names, explicit effects, and control-flow/data-flow structure.
3. The same IR with a mechanical symbolic spelling. This tests renaming/compact notation separately from a new semantic design.
4. An AIN candidate with its proposed structure and composition rules.

Where forms 3 and 4 coincide, merge them and say so. Do not manufacture a difference. Supply equivalent contract content, operation catalogs, debugging feedback, and examples; count their actual context and retrieval costs. Equal semantic information does not mean equal character count or an uncharged AIN codebook.

Python, IR, and AIN must reach the same effectful primitives and pass the same conformance cases. Use shared lowering and execution where practical; document residual differences. Freeze compiler optimization settings across forms. A faster compiler pass is not evidence that a model writes a better representation.

Phase A can test usability under an existing tokenizer. It cannot establish the advantage of dedicated opcode tokens or of a model trained to think in the proposed representation.

### Phase B: matched adaptation

Only after Phase A's executable artifacts and evaluation protocol are reviewable, propose adapting matched copies of one base model. Give each representation equivalent training tasks and the same training-compute budget, tuning opportunity, context limits, and tooling. Publish the adaptation data and transformations where permitted.

Keep task families, not just event seeds, separate between training, validation, and final evaluation. Select checkpoints and hyperparameters using validation only. Freeze them before opening the final set. Include an unadapted control and an equally adapted conventional-source/IR control.

This phase is a proposal, not permission to incur training or API charges. Actual providers, supported training methods, budgets, and accounting must be agreed before execution.

### Phase C: dedicated tokens or another native model interface

A dedicated operation vocabulary changes more than surface spelling: tokenizer behavior, embeddings, model training, and possibly the interface all change. Treat it as another experiment. Document vocabulary size, parameter changes, initialization, data exposure, training compute, inference compute, and decoding constraints.

Compare with conventional representations receiving matched adaptation and compute. Report token length within each tokenizer, but do not equate a custom-token reduction with an equal reduction in compute, latency, or provider billing. Include vocabulary construction and training in any lifecycle cost claim. An unavailable model/tokenizer interface is an explicit execution limitation, not an implemented feature.

## Task and data design

Publish learning tasks and a development set. Reserve structurally different final tasks and fresh event seeds with a recorded commitment before evaluation. Keep the final set closed during language design and tuning. Public historical tasks may be reused as regression tests; they are not a fresh generalization result. No claim about a provider's pretraining-data exclusion follows from holding out our generated seeds.

Evaluate complete chains, not only initial generation:

| Stage | Example demand |
|---|---|
| Build | Implement the workflow from its contract and allowed primitives |
| Explain | Predict outputs, rejected inputs, and state transitions on supplied traces |
| Edit | Change lateness, grouping, or publication behavior without breaking other rules |
| Repair | Diagnose an injected dedupe, race, overflow, or retry defect |
| Optimize | Improve an equivalent flow under the same resource and cancellation contract |
| Handoff | Continue from another session's program and recorded evidence |

Separate spelling-only edits from semantic changes. Use deterministic adversarial traces alongside generated workloads. Include cases where an optimization is invalid, such as replacing horizon dedupe with global dedupe, accepting a false ordering assertion, or batching away required checkpoints.

Assign tasks and representation conditions in randomized, counterbalanced order. Use independent sessions for each assigned attempt so an earlier condition's solution is not silently reused. Record provider/model/version, tools, sampling settings, seeds, all attempts, exclusions, and human intervention. A model's self-reported identity is not independent provider attestation.

## Controls that make a positive result useful

- Give all arms the same operation implementations and semantic evidence. Charge discovery, documentation, examples, validation, and repair work to the arm that uses them.
- Compare against competent conventional code and a typed IR, not just a verbose or deliberately weak baseline.
- Hold optimization access constant. If an agent proposes a new flow, test its conformance and make that flow available to every arm in a separate optimization comparison.
- Keep representation and AICC reuse as separate factors. Start with equal ordinary libraries; later cross representation with ordinary/AICC binding, using the same capability bodies and contracts.
- Keep private scoring rules behind the same interface in every arm. No arm receives their source or a privileged oracle. Record what the agent, test harness, and host can each observe.
- Freeze limits and stopping rules before final evaluation. Retain failed and timed-out attempts. Do not keep sampling until one AIN program passes and compare it with one conventional attempt.
- Evaluate dynamic authority/cancellation behavior as well as equal final arithmetic. A coarser operation is eligible only if it preserves the agreed checkpoints or is explicitly a different contract.

## Measurements and decision rules

First establish conformance of the interpreter/lowering and reference controls. Then measure model authoring performance. These are separate gates.

| Question | Record |
|---|---|
| Did the assigned chain succeed? | All required stages and hidden cases; failures, timeouts, unauthorized effects, and human repairs |
| How much model work was consumed? | Actual input/output/cache tokens where available, calls, retries, retrieved context, and tool results |
| What did completion cost? | Actual applicable billing, elapsed time, human effort, setup/adaptation cost, and costs of failed attempts |
| Is editing reliable? | Regressions and repair work after each specified change |
| Is execution equivalent and practical? | Output and effect traces, runtime, peak memory, queue limits, cancellation and recovery observations |

Report per-assigned-task costs, success rate, and total measured resources divided by completed successful chains. Include consumed resources from failed attempts; report task difficulty and results by family. Printed length, token count, elapsed time, and money are different quantities. An unmeasured field stays unmeasured.

Use a separate development pilot to choose the primary metric, a practical improvement margin, an allowed success-rate difference, task count, and uncertainty method. Register those choices before the final tasks are opened. Pair representation comparisons on task families and cluster uncertainty by independently authored task/chain, not by repeated timings of one generated input. Publish estimates and uncertainty, including a result too imprecise to resolve the chosen margin. Do not derive a significance threshold from the observed min–max range of three runs.

A positive result requires the preregistered correctness/success gate and improvement margin against the strongest matched control. Fewer tokens with more failures, omitted semantics, uncharged catalog text, or a weaker baseline does not support the hypothesis. A reduction in inference work alone does not establish lower lifecycle cost after adaptation, library construction, and maintenance.

The near-term hypothesis is unsupported under the tested conditions if AIN fails conformance or misses the registered improvement rule. A precise null or adverse result can reject that specified claim. It would not prove that every future native representation is useless. Conversely, success on this one workflow cannot establish a universal language advantage.

## Next deliverables, in order

Execution record: items 1–4 now have a tested development implementation. Item 5
has a small public development pilot, not a securely closed final evaluation.
The [first execution report](../../experiments/ain_v0/FIRST_EXECUTION_REPORT.md)
records results, failed preflights, measurement limits and the next experiments.

1. Review and freeze the complex task's semantics, trace format, resource limits, and error priority.
2. Build the readable reference and shared deterministic conformance harness, including cancellation, restart, and invalid-input traces.
3. Define the smallest typed core needed by the task; implement and cross-check the conventional IR and AIN front ends.
4. Publish equivalent source/IR/AIN examples, catalogs, type errors, and lowering artifacts. Mark any incomplete construct explicitly.
5. Run the development pilot, inspect measurement overhead, and freeze the evaluation protocol and fresh task commitments.
6. Execute Phase A only with an agreed provider/budget setup; publish all attempts and raw accounting.
7. Decide from those results whether matched adaptation or dedicated tokens justify their additional cost. Register a new protocol before either phase.

Authorship: this plan was prepared by OpenAI Codex under Izik Bachar's research direction. The linked development study is same-session engineering evidence; the broader model experiments remain future work.
