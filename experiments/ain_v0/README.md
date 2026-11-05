# AIN v0: execution of the research plan's deliverables 1–4

**Executed by:** Claude Opus 5.5 (Anthropic; self-reported) on 2026-11-05, following `docs/ain/RESEARCH_PLAN.md` on branch `research/ain-language-and-study-results`.

**No model was evaluated and none was trained.** Deliverables 5–7 (development pilot, Phase A, adaptation) need an agreed provider and budget, which the plan withholds, so they were **not executed**. All results below are about the specification, implementations and representations, not about model performance.

## Plan deliverables

| # | Plan deliverable | Status | Where |
|---|---|---|---|
| 1 | Review and freeze semantics, trace format, limits, error priority | **Proposed freeze v0.1** (32 decisions, 6 open questions), awaiting owner review | `SEMANTICS_FREEZE.md` |
| 2 | Readable reference + shared deterministic conformance harness, including cancellation, restart and invalid input | **Done** | `ain_v0/reference.py`, `ain_v0/primitives.py`, `conformance/` |
| 3 | Smallest typed core; conventional IR and AIN front ends, cross-checked | **Done at operator-graph level** (see Finding 6) | `ain_v0/core.py` |
| 4 | Equivalent source/IR/AIN examples, catalogues, type errors, lowering artefacts | **Done** | `programs/`, `measurements/` |
| 5 | Development pilot; freeze the evaluation protocol | **NOT EXECUTED**: needs model runs | — |
| 6 | Phase A with an agreed provider and budget | **NOT EXECUTED** | — |
| 7 | Decide on adaptation or dedicated tokens | **NOT EXECUTED** | — |

## Results (all executed; full output in `RUN_LOG.txt`)

| Check | Result |
|---|---|
| The spec's 23-line AIN sketch, used **verbatim** | Parses, type-checks (effects: source.read, sink.read, policy.invoke, sink.commit) and runs |
| IR program vs AIN program | **Identical AST**; both round-trip through their printers |
| Hand-derived cases (spec trace, boundaries, invalid input, capacity, overflow, policy, authority, cancellation) | **47/47 pass** in all three forms; effect traces identical across forms |
| Crash before stage, before commit, after commit, and lost acknowledgement, at each of 3 epochs | **12/12**: publications equal the uninterrupted run, each epoch committed exactly once |
| Random differential traces (Unicode tags, duplicates, late rows, small limits, failures, cancels, revocations, crashes) | **400 traces, 0 differences** between Python reference, IR and AIN |
| Deliberately wrong implementations | **6/6 detected**: global dedupe, sliding window, Python whitespace, late rows reserving IDs, filter before reservation, checks only at batch entry |
| Type-error mutations through both front ends | **13/14 give the same error code**; 1 representational asymmetry (Finding 4) |
| Sink: idempotent repeat, conflicting payload, stale writer | **3/3 pass** |

## Findings

1. **The sketch is executable as written.** It needed 32 semantic decisions the contract does not make (`SEMANTICS_FREEZE.md`). Examples: what a run returns when input stops without an end marker; which of cancellation, authority and policy error wins; and that the contract's whitespace set differs from Python's.

2. **The forms agree, but the agreement is of composition.** All forms call the same shared primitives (validation, normalisation, grouping updates, executor, sink), as the plan permits. The differential tests therefore show that the reference, IR and AIN *compositions* are equivalent; they do not independently verify the primitives. Primitive correctness rests on the hand-derived cases and the mutant checks.

3. **The suite catches wrong implementations, but thinly in places.** All six mutants were caught, three of them invalid optimisations the plan names. The Python-whitespace mutant was caught by only one case, and global dedupe and late-row reservation by two each. More cases are needed before a model study relies on this suite.

4. **AIN and IR are not perfectly equivalent spellings.** AIN types parameters by position, so a mistyped parameter cannot be written; IR can write one and gets `E_PARAMS`. In AIN the nearest mutation, dropping a parameter, surfaces as `E_UNDEFINED`. Two checker codes (`E_LINEAR_UNUSED`, `E_STATIC_CONFIG`) are unreachable with the v0 catalogue, because every program is one chain from the single source.

5. **No compression advantage under an existing tokenizer.** Counts are tiktoken `o200k_base` only; not billing.

   | Form | Program bytes | Program tokens | Catalogue tokens | Total |
   |---|---:|---:|---:|---:|
   | Typed IR | 1,152 | **298** | 282 | **580** |
   | AIN (verbatim sketch) | 616 | **298** | 368 | **666** |
   | Python reference (not matched: contains operator logic) | 5,118 | 1,245 | 126 | 1,371 |

   AIN halves the bytes but not the tokens: numeric operation IDs and `%NN` references tokenise poorly, as the plan anticipated. With its codebook charged, AIN needs about 15% more tokens than the IR. In v0 the plan's forms 3 (symbolic spelling) and 4 (AIN candidate) **coincide and are merged**, as the plan instructs.

6. **The operator-graph core is too coarse for the plan's authoring tasks.** v0 programs wire 21 coarse operations whose bodies live in a library. That is enough to make the sketch executable and to compare spellings. But tasks such as "repair an injected dedupe defect", "change grouping" or "optimise a flow" mostly cannot be expressed at program level, because the logic sits inside operators. Before a pilot, the core needs expression-level operator bodies, or the authoring task must include implementing operators in every form.

7. **The sketch's typing hides state effects.** Operations 105 and 115 mutate workflow state without a State argument (D-30). Making effects explicit is a design requirement the sketch does not yet meet.

## Limitations

- Concurrency is a deterministic simulation (bounded running and waiting, pluggable completion order), not real asynchronous execution. Equal results here say nothing about races.
- The sink is an in-process reference sink. There is no real isolation, authentication or durable storage.
- **One agent (Claude) wrote the implementation and the hand-derived expectations in one session**, so a shared misreading of the spec would go unnoticed. An independent second reference and independently written expectations are needed.
- The random generator is weak in two ways visible in its outcome distribution (`RUN_LOG.txt`). 123 of 400 traces end early on an injected invalid record, which limits depth. **No random trace reached `CAPACITY` or `OVERFLOW`**, so those paths are covered only by the hand cases.
- Python 3.12.3, Unicode 15.0.0, Linux.

## Reproduce

```sh
cd experiments/ain_v0
./run_all.sh            # conformance, mutants, artefacts; writes RUN_LOG.txt and results/
```

Requires Python 3.12 with Unicode 15.0.0. Token counts additionally need `tiktoken` with `o200k_base`.

## Recommended next steps, in order

1. Owner review of `SEMANTICS_FREEZE.md`, then a second, **independently written** reference and expectation set.
2. Extend the core to expression-level operator bodies (normalisation, dedupe, grouping, finalisation), so that build, edit and repair tasks act on program text, with the IR and AIN front ends kept on one AST.
3. Add real asynchronous executor conformance, and more cases where mutants are thinly detected.
4. Only then: the development pilot (deliverable 5) with an agreed provider, budget and registered metrics.
