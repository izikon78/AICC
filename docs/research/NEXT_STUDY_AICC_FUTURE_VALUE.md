# AICC: next study on reuse across agents, projects, and time

Prepared 4 November 2026. Research proposal, not an article revision, approved architecture change, or completed economic study.

## Recommended research question

**Can AICC make a validated capability and the evidence for using it portable across new tasks, agent sessions, and software changes, while preserving correctness and reducing total work?**

First-use cost is an outcome to measure. Discovery, contract preparation, conformance testing, packaging, and binding can add setup cost. Large existing capabilities might also save work immediately. Neither a first-use loss nor later savings should be assumed.

The possible longer-term value is cumulative: a new agent or project can reuse an implementation together with precise evidence about its behavior, environment, permissions, and validity. Changing requirements or software should trigger the appropriate revalidation. That is the claim to test next.

## What we can support now

The earlier import verification established that ordinary and registry-based reuse both pass the small official tasks. That establishes feasibility on those fixtures, not AICC superiority.

Two existing prototypes were rerun in temporary copies on 4 November 2026 to check which future-facing claims have an executable starting point. The historical sources were not edited.

| Claim | Current evidence | Boundary |
|---|---|---|
| Existing code can be invoked through compact references | Round 7/8 official-suite reruns passed for available submissions | Ordinary package reuse also passes; no economic advantage established |
| Precise semantics can support different runtime implementations | Existing `group_by_window` Python and table-assisted JavaScript implementations each matched 1,206/1,206 supplied cases; naive JavaScript matched 559/1,206 | One function, one original author, same existing test pool; not independent agent authoring or universal equivalence |
| A host can retain a scoped validation decision | Existing H3 prototype made 20 alias calls after one full validation | Finished-code demonstration, not measured agent familiarity or cross-session cost saving |
| A prototype can notice specified changes | Supplied tests detected changes to requirement, policy, contract, environment, implementation, and revocation; additional tampered-code and declared-effect checks rejected their supplied cases | In-process prototype without production isolation, authenticated identity, complete dependency assurance, or a general security guarantee |
| AICC reduces billed cost, development time, or defects at scale | Not established | Requires a new controlled study |
| A trained AI-native language improves authoring | Not tested | Keep as a separate future study; punctuation examples do not test a trained operation-token model |

Fresh rerun outputs are preserved in the [prototype recheck record](evidence/2026-11-04-prototype-recheck.json), with [provenance and limitations](evidence/README.md). They rerun existing programs and inputs. They add reproduction evidence, not a new independent scientific replication or a paid model benchmark.

## Future value worth investigating

| Opportunity | What would matter to users | Evidence required |
|---|---|---|
| Transfer between agents and sessions | Another agent can continue with a capability's valid evidence and reuse decision | Fresh sessions/providers reuse correctly with less qualification work than equally equipped conventional agents |
| Stable behavior across implementations | A workflow moves between runtimes/providers without silent semantic changes | Independently written variants pass hidden checks for outputs, errors, ordering, numeric/Unicode behavior, and effects |
| Maintenance as software changes | Unchanged work remains usable while affected bindings are revalidated | Correct handling of relevant and irrelevant changes; fewer unnecessary rechecks without accepting stale behavior |
| Shared validation effort | Projects reuse trustworthy tests/contracts instead of repeating all preparation | Measured curation cost amortized over observed reuse, including failures and maintenance |
| Public/private composition | Reusable public capabilities can work alongside protected owner-controlled logic | Authenticated execution and real isolation/effect controls tested against hostile cases |
| A future AI-native authoring interface | Agents express genuinely new logic and compose capabilities efficiently | Equal-budget trained/adapted-model comparison with conventional code and constrained typed representations |

These are prospective benefits, not current product capabilities or proof that the proposal is novel in every respect.

## Why ordinary reuse is a demanding baseline

Anthropic's [code-execution-with-MCP article](https://www.anthropic.com/research/code-execution-with-mcp) already describes loading definitions on demand, keeping intermediate data outside model context, persisting state, and saving reusable code. AICC must be evaluated against agents with these abilities, rather than an agent that repeatedly reads or regenerates everything.

The [enterprise operation-resolver study](https://aclanthology.org/2026.emnlp-industry.179/) reports better success and lower token use/latency on its large internal API benchmark. This supports studying agent architecture at catalog scale; it is not an AICC result and does not establish an advantage for AICC's proposed shared validation records.

[CompactionBench](https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/) studies persistent software-evolution sessions and cache-preserving compaction. This makes lifecycle workflows a useful setting and compaction a relevant baseline capability.

The [agent token-consumption study](https://arxiv.org/abs/2604.22750) reports substantial run-to-run variation and weak model predictions of their own usage. Use actual telemetry and repeated trials; do not ask a model to estimate savings and call the estimate a measurement.

These primary-source pages were checked for this proposal. This is targeted related-work checking, not an exhaustive novelty review.

## Proposed next task

Working name: **AICC reuse across agents and software changes — pilot**.

The [execution plan](../../experiments/lifecycle-pilot/README.md), [protocol](../../experiments/lifecycle-pilot/PROTOCOL.md), and [task checklist](../../experiments/lifecycle-pilot/TASKS.md) turn this brief into the next implementation task.

### 1. Freeze one capability record and a small capability set

Describe identity/version, observable behavior, tests and assurance scope, loaded artifact and dependencies, supported environments, caller requirements/policy, principal/scope, and validity/revocation conditions. Keep runtime authority separate from the agent's assertion that a capability is suitable.

Start with a few realistic workflows rather than only tiny helper functions. Candidate families from the existing research agenda:

- Event ingestion, normalization, deduplication, and time-window grouping.
- Large-file streaming, checksums, bounded-memory processing, and cleanup.
- Bounded worker queues, cancellation, retries, ordering, and idempotency.

The study must include genuinely new application logic. AICC supplies reusable operations; the experiment should also test whether agents compose them correctly for changing tasks.

### 2. Compare three well-equipped approaches

| Arm | Equipment | Question |
|---|---|---|
| A: conventional | Same implementations, good package docs, discovery, code execution, prompt caching, persistent notes/code, version locks, and the same execution permissions | What do competent existing agents achieve? |
| A+: conventional with equal evidence | A plus the same conformance vectors, manifests, and semantic evidence supplied to AICC | Does better evidence explain the benefit without a registry/binding standard? |
| B: AICC | Same implementations/evidence plus shared versioned capability records and host-validated portable bindings | What incremental value comes from AICC's organization and transfer mechanism? |

Allow ordinary agents to cache and persist useful information. Keep the underlying host security boundary equivalent. If A+ achieves the same result as B, report that the evidence/standardization helped without attributing an extra benefit to the registry name or handle syntax.

### 3. Evaluate a sequence of uses

Use five stages per project:

1. **Cold start:** discover, qualify, and compose the capabilities for the first task; include setup costs.
2. **Warm reuse:** extend the project with requirements that preserve the existing bindings' validity.
3. **Handoff:** a fresh agent session, including another provider where available, continues from the permitted project records.
4. **Relevant change:** change semantics, version, dependency, policy, environment, expiry, or authorization so an affected decision must be revisited.
5. **Unrelated change and new use:** introduce a change that should not invalidate an unrelated capability, then test legitimate reuse and a separate unauthorized reuse attempt.

Randomize matched changes and task order where possible. Include valid, incompatible, and insufficiently specified candidates whose defects are not advertised in their names. Use new held-out grading cases; the published Round 7/8 fixtures are already known.

Three independent project runs per workflow/arm would be a descriptive engineering pilot, not a powered demonstration of broad economic superiority. Freeze models, configurations, budgets, and supplied information. Choose the larger study size from measured variance and a preregistered effect target.

### 4. Measure reliability and economics separately

- Correct tasks and false reuse decisions, including silent wrong outputs and stale acceptance.
- Required invalidations versus unnecessary invalidations; qualification and repair work.
- Unauthorized executions in the specified test cases, reported with the actual boundary tested.
- Model uncached/cached input, output/reasoning and available cache-write telemetry; provider-billed charges, all retries, and failed/incomplete attempts.
- Agent wall time, model/tool/verification time, CPU/memory, and human preparation work.
- Registry creation, contract curation, assurance, hosting, and maintenance costs in addition to per-use runtime/inference costs.

Use cost per correctly completed project sequence, not just cost per successful function invocation. Report cold start, warm reuse, transfer, and change handling separately.

### 5. Report an observed break-even curve

For N completed tasks/projects at a clearly defined unit of reuse:

```text
Total cost(N) = preparation + all task attempts + verification + maintenance + infrastructure
Net saving(N) = conventional total cost(N) - AICC total cost(N)
```

Compute this for both A and A+. Count shared setup only once, and amortize it over observed uses. Show any excluded cost assumptions. If a study is too short to observe break-even, say so rather than extrapolating it as established fact.

Under a simplified constant-cost model with a positive incremental per-use saving:

```text
break-even uses > extra AICC setup cost / incremental saving per use
```

Update costs change this threshold. If the incremental saving is zero or negative, repetition alone creates no break-even. This equation does not supply a numerical threshold without measured inputs.

## What would make a useful article result

A concrete transfer-and-change case study would be valuable even if first-use cost rises: show exactly what another agent reused, what evidence remained valid, which change forced a recheck, which unrelated work remained usable, and the total cost/correctness consequences against A and A+.

Support a capability claim only for the tested conditions. An observed compatibility or invalidation failure is also useful evidence if the article explains the boundary and a falsifiable improvement. Avoid presenting the proposal as having transferred learned model weights, eliminated reasoning, established production security, or guaranteed a universal saving.

The article can frame AICC as a proposal for **accumulating reusable computational behavior together with evidence about when it is valid**. Whether this produces a net advantage is the experiment's question.

## Deliverables for the next task

1. Frozen record/schema and change scenarios.
2. Runnable conventional, equal-evidence, and AICC paths with comparable permissions.
3. New correctness/change/authorization grading cases kept separate from authoring context.
4. Telemetry schema and complete raw trial records.
5. An observed lifecycle cost and failure analysis, with an article-ready explanation of supported claims and remaining limits.

This brief prepares that work. No paid API runs, model training, production host, or article revision was launched by preparing it.
