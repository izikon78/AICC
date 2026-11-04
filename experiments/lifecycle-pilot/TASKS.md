# Ordered next steps and acceptance checks

Planning owner: Izik Bachar. Contributors and provider/model assignments will be recorded in the study configuration when selected. No agents are assigned or launched by this checklist.

## Prepared in this change

- [x] Define the future-value research question and comparison arms.
- [x] Specify the project sequence, reporting boundaries, and completion criteria.
- [x] Provide configuration and measurement templates.
- [x] Preserve the existing prototype recheck output with its limitations.

## 0. Freeze scope and study inputs

- [ ] Select the event-processing workflow as the first engineering milestone.
- [ ] Record capability, contract, dependency, runtime, grading-set, and tool versions with file hashes.
- [ ] Record the exact model/provider configuration, trial limits, and spending cap before paid trials.
- [ ] Designate fresh grading inputs separate from authoring context; do not reuse published Round 7/8 cases as unseen evidence.
- [ ] Record the historical missing Claude revision as an unresolved article-source issue. It need not block a newly designed pilot, but its numbers must not be mixed into the new dataset.

**Done when:** one versioned scope/configuration manifest identifies the experimental inputs, open decisions, and permitted costs. The main question and outcome measures are fixed before results are inspected.

## 1. Specify the capability and its validity conditions

- [ ] Specify inputs, outputs, errors, ordering, numeric/Unicode rules, side effects, and supported environments.
- [ ] Define artifact/dependency identity, caller obligations, policy/principal/scope, validity period, and revocation conditions.
- [ ] Define compatible, incompatible, and insufficient-evidence outcomes. Insufficient evidence must lead to escalation or rejection of reuse, rather than assumed compatibility.
- [ ] Document which checks are mechanical conformance checks and which depend on an execution boundary.

**Done when:** the record explains both when reuse is allowed and when the decision becomes stale. Its assurance statements identify the tested conditions and do not imply universal correctness.

## 2. Build the event workflow and fair comparisons

- [ ] Implement A with good package documentation, discovery, code execution, caching, persistent notes/code, and version locks.
- [ ] Implement A+ with the same tests, manifests, and semantic evidence supplied to B.
- [ ] Implement B using shared versioned records and host-checked bindings over the same underlying capability implementations.
- [ ] Keep host permissions, isolation, task requirements, and available tools comparable across arms.
- [ ] Ensure the task includes new application logic in addition to reusable operations.

**Done when:** all three paths can execute the same documented workflow. Any correctness failure is visible in logs. No arm is forced to repeatedly read full source or documentation while another is allowed to cache.

## 3. Exercise handoff and change handling

- [ ] Create the five-stage project sequence described in the protocol.
- [ ] Add relevant changes to behavior, dependencies, requirements, policy, environment, expiry, and revocation.
- [ ] Add an unrelated change that should leave an unaffected capability usable.
- [ ] Include invalid candidates without revealing their defects in their names.
- [ ] Include unauthorized reuse using synthetic resources under the same host boundary in all arms.
- [ ] Start a fresh session for the handoff and record exactly which project artifacts it receives.

**Done when:** expected valid/stale/unknown outcomes are specified before grading, and the harness records false reuse and unnecessary invalidation. A security failure disqualifies the current implementation version from agent-trial readiness; retain the failed run and use a new version for any repair.

## 4. Verify measurement collection

- [ ] Record task/chain/stage identity, seeds, all attempts, errors, repairs, and final correctness.
- [ ] Collect available provider usage and billing records without storing credentials or private input content.
- [ ] Distinguish actual billing, static tokenizer counts, timing, and estimates; use null plus a status for unavailable measurements.
- [ ] Include preparation/curation, failed trials, maintenance, and infrastructure in cost accounting; apply shared evidence costs consistently to A+ and B.
- [ ] Exercise the logger on explicitly labeled synthetic fixtures before a real trial.

**Done when:** records can be traced to raw usage/test logs and no absent measurement appears as a zero. Synthetic logger checks are kept outside the real trial dataset.

## 5. Run the descriptive pilot

- [ ] Freeze the protocol version and the complete configurations before model runs.
- [ ] Attempt all planned project chains, including failures and incomplete runs.
- [ ] Balance matched model/provider sequences across arms and randomize arm order/assigned seeds as specified in the protocol.
- [ ] Report any reduced scope explicitly; do not silently replace unavailable providers or omit failed chains.

**Done when:** all planned attempts are accounted for and deviations are listed. With the full proposed scope, that means 27 chains and 135 stage executions, not 135 independent project replications.

## 6. Analyze and prepare article evidence

- [ ] Compare B with A and separately with A+ for correctness, false reuse, handoff/revalidation work, and total cost per successful project sequence.
- [ ] Separate cold start, warm reuse, transfer, relevant change, and unrelated change results.
- [ ] Plot the observed cumulative cost difference and any observed break-even; label any extrapolation as a model.
- [ ] Report provider/workflow differences and every failed/incomplete chain.
- [ ] Use pilot variance and a chosen practical effect size to plan a larger preregistered study.
- [ ] Prepare an article case study distinguishing demonstrated results, implementation limits, and future hypotheses.

**Done when:** a reader can reproduce the calculations and see both favorable and unfavorable outcomes. A null or negative result is a completed pilot result; it is not a reason to change thresholds after seeing the data.
