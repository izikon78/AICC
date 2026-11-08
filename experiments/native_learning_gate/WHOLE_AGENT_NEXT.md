# Whole-agent pilot after the local learning gate

Prepared 6 November 2026 under Izik Bachar's research direction. This is a
proposed extension of the trained-native protocol. Run configuration, budgets
and final-case commitments must be frozen before training or final evaluation.

The local learning gate checks executable program learning, GPU memory fit and
throughput. The next pilot compares complete observable agent episodes, including
working records, persistent memory, tools, executable artifacts and handoff.

## Matched conditions

Start each adaptation from the same checkpoint and tokenizer revision. Train
Python, readable typed IR and numeric AIN sequentially on the same GPU. Generate
paired episodes from one semantic task specification. Give each condition the
same semantic episodes, presentation counts, initial project state and capability
implementations. Include an unadapted checkpoint evaluation. Report pretrained
language exposure and actual computation separately from presentation counts.

Numeric AIN uses `experiments/ain_v0/ain/language.py` and its existing encoding of
the typed IR. Extend the trusted capability catalog equally across conditions
where agent operations require host access. Preserve type and effect checking.
Python calls the same catalog functions through a restricted host interface.
Publish the catalog schema, implementation hashes and all representation adapters.

## Observable episode contract

Each episode starts with task requirements and a fresh workspace. Every model
turn emits a bounded executable action program in its condition's representation.
The host records that program, validates it, executes allowed effects and returns
the resulting observation. The fixed language manual is absent at evaluation.
New task data and private capability contracts remain explicit input.

Expose the same primitive capabilities for reading project files, writing or
patching candidate artifacts, running public checks, reading and writing bounded
memory, and submitting a result. Add no capability that solves an entire scored
task. Limit effects to an episode-local workspace and memory store. Judges and
final cases live outside the workspace and tool namespace.

Working records and persistent memory are model-authored values in the selected
representation. Memory entries can hold executable fragments, typed state and
literal task data. The host validates and stores these values without generating
descriptive content for one condition. Log every read, write, byte count and
subsequent context inclusion. If the model receives a compacted memory view,
apply the same deterministic policy and limits to all conditions.

A handoff starts a fresh inference context with only the frozen task/project
inputs, committed artifact and explicitly persisted memory. Record exactly what
crosses this boundary. Optional human-readable rendering is requested by a frozen
schedule, with translation and inference work charged at each occurrence.

## Three compositional domains

| Domain | Authored rules and required boundary cases |
|---|---|
| Temporal event processing | Filtering, deduplication, watermark finalization and late arrivals, with frontier equality and trailing records after completion |
| Versioned state and caches | Version comparison, invalidation, bounded capacity, restore and conflicting updates, with malformed restored state |
| Publication and retry | Cancellation, retry scheduling, idempotent commits and recovery, with interacting failures and effect ordering |

Use bounded containers, explicit state and generic scalar operations. Shared
normalization or storage capabilities expose equal contracts. Include tasks whose
required composition has no matching reusable whole-task capability. Distinguish
deterministic asynchronous simulations from tests using real asynchronous I/O.

Each assigned chain contains construction, a semantic change, an interacting
defect repair and a fresh-context handoff. Freeze permitted feedback and attempt
limits. Reserve structures, compositions and families before generating seeds.
Development cases remain separate from final cases. Hash and independently
review the generator, expected traces, judges, splits and final commitments.

## Resource ledger and ceilings

Log every model request and generated action, including malformed output,
timeouts, failed checks, failed repairs, retries and interrupted runs. Record
input/output units, prefill and decode time, CUDA timing where valid, wall time,
peak memory, tool execution, parsing, validation, compilation, artifact execution,
memory traffic and optional rendering. Preserve raw observations and the judge's
reason for each failure. Report training, data generation and tuning separately.

Before launch, fill a run manifest with checkpoint and source hashes, training
seeds, semantic exposures, context and output limits, memory capacity, attempts,
per-chain timeout, tuning allowance, GPU-hour ceiling and any cash ceiling. Use
the local throughput measurement to choose an attainable bounded schedule.
Terminate a run on its declared ceiling, CUDA exhaustion or nonfinite training
loss, and retain its partial ledger. Any material protocol change creates a new
version and fresh final commitments.

## Advancement criteria

Freeze a minimum chain success rate, a correctness tolerance, a practical
resource improvement margin and an uncertainty rule before final evaluation.
Compute total inference and tool work across all assigned attempts divided by
correctly completed chains. Report success rate beside that value, and report an
undefined ratio when no chain succeeds. Use paired tasks and uncertainty that
respects task families and independent training seeds.

Proceed to a larger study only when correctness and the declared resource margin
pass against the strongest matched control within the frozen budget. An
inconclusive or failed pilot pauses scaling and preserves all observations.
Gains shared by readable IR and AIN address the broad learned-representation
hypothesis. Additional AIN gains require a separate supported comparison.
Evaluate AICC reuse and the AI implementation language in later experiments.
