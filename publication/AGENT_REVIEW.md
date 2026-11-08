# Start here for an AI-agent review

Concept and research direction by Izik Bachar. This guide introduces the final
AIN/AICC publication and its review routes. Earlier AIN knowledge is unnecessary.
It contains no expected experiment totals.

## Choose a route before opening outcomes

**Independent accounting reconstruction.** Start with the
[independent reconstruction guide](reproduction/INDEPENDENT_RECONSTRUCTION.md)
and [standalone theory](AIN_THEORY.md). Follow that guide's permitted input list.
Preserve your first counter, outputs, hashes and read order before opening the
article, reference implementation, evidence index, saved results or comparison
outputs. Prior exposure must be disclosed; a prior-exposed reconstruction can
still be useful. Reading only this entry guide does not reveal expected totals.

**Technical and conceptual review.** Read the material below, then inspect and
run the relevant checks. This route permits reading published outcomes first
and should be reported as a known-answer review. Do not describe it as a blinded
reconstruction.

1. [Language theory and notation](AIN_THEORY.md) defines the reference concept.
2. [Giving AI a Language of Its Own](https://github.com/izikon78/AICC/blob/main/publication/AICC_Final_Draft.md) presents the argument;
   the [PDF](https://github.com/izikon78/AICC/blob/main/publication/AICC_Final_Draft_Review.pdf) supplies the print layout.
3. [Related approaches](RELATED_WORK.md) identifies close predecessors and the
   boundaries between reviewed systems and executed local controls.
4. [Evidence index](EVIDENCE.md) connects claims to final source and raw records.
5. [Local comparison protocol](../experiments/representation_comparison/PROTOCOL.md)
   defines the actual-text experiment. Inspect its implementation and saved
   records after selecting your review route.
6. [Research programme](RESEARCH_PLAN.md) separates proposed studies from work
   already performed. [Validation](https://github.com/izikon78/AICC/blob/main/publication/VALIDATION.md) records publication checks.

## What to evaluate

- Identify the proposal's distinct contribution relative to learned tool tokens,
  reusable skill libraries, executable Python actions, context management and
  the separate AINL project. Separate a defined mechanism from an open hypothesis.
- Check whether every local representation receives equivalent operations,
  operands, task information, history, state and data-placement opportunities.
  Inspect the strongest compact conventional-language control.
- Keep actual tokenizer counts separate from hypothetical learned-code units.
  Check the declared unit costs, framing, exposure schedule and correctness
  assumptions before interpreting a percentage or resource claim.
- Check preservation of behavior and continuation-relevant state through edits,
  repairs and handoff. Look for counterexamples, missing information and changes
  that invalidate a capability contract.
- Verify that `!501(config)` is explained as a reference to a predefined
  `ConnectToDB(config)` capability. Its database/native decomposition and the
  AI-built or learning compiler are conceptual. The implemented native compiler
  has a bounded arithmetic scope.
- Distinguish AIN as a reference concept from a released, complete language.
  The local symbolic codec covers a declared subset. The fully native AIN system
  and the named external project runtimes are not executed by that comparison.
- Check contributor provenance and whether independent counter reproduction,
  known-answer replay, runtime measurements and model-learning evidence receive
  their appropriate interpretation.

## Run bounded checks

For a fresh machine, use the [portable ZIP](https://github.com/izikon78/AICC/raw/refs/heads/main/publication/downloads/AICC_Final_Experiments_Packet.zip)
and [current testing instructions](reproduction/START_HERE.md). Select your route
before opening outcomes. The packet supplies pinned tokenizer assets and setup
instructions; dependency installation may need Internet access. It includes no
model weights or adapters.

The ZIP supplies the standalone theory and executable evidence for offline CPU
reproduction after dependency setup. Its manuscript and publication-validation
links open the canonical copies on `main`.

After an independent first seal, or for a known-answer technical review, run
these commands from the repository root in a prepared Python environment,

```text
python -m unittest discover -s experiments/representation_comparison -p test_*.py -v
python publication/examples/validate_examples.py
python publication/examples/aicc_binding.py
python experiments/representation_comparison/run.py --output work/reviewer-comparison-001
```

Use a new output directory for each attempt. The comparison run requires the
approved-core package pins and cached pinned tokenizer. The example checks use
their published mock contracts and existing processing prototype. See the
[supplementary routes](reproduction/SUPPLEMENTARY_TESTS.md) for dependency and
scope details. GPU adaptation and full processing workloads are separate optional
executions; this entry guide requests no model pilot or heavy timing run.

## Return a reviewable record

Return the review route, provider/model identity as reported, repository commit,
environment and dependency versions, prior exposure, files read and their order,
commands, first implementation/output hashes, full logs, failures and deviations.
Preserve the first attempt and place corrections in a separate output directory.
Report unknown authoring usage as unknown and distinguish it from the experiment's
inference count. Explain each finding with a source path, evidence and proposed
correction. Submit the report to the person who requested it; these scripts send
no messages or results automatically.
