# Approved-core workflow theory test

6 November 2026. Theory and research direction by Izik Bachar. Experiment implementation and review by Codex with collaboration agents.

The experiment adopts the requested premise that an optimized short representation, fluent agents and fully approved reusable core code already exist. It fixes composition correctness through oracle agents and executes their artifacts and tool actions. This isolates the conditional resource demand of composing, changing, repairing and handing off workflows.

Under the frozen equal-cost-per-position assumption, ideal AIN uses 24.0% fewer total positions than short-alias Python in the resident-data schedule and 12.8% fewer in the inspect-data schedule. This is a conditional accounting result. The Python columns contain measured text-token counts, while the ideal columns contain modeled semantic code units plus the same common input text. Actual inference latency and trained agent efficiency require separate measurements.

## Complete workflow ledger

Each schedule contains 18 chains, 72 stages and 216 logical agent requests. Shared requirements and business parameters are charged at every request. Predecessor artifacts, persisted memory and all accumulated action/tool history are counted at every reuse. Total positions include input and output, with equal position cost. Output includes one response-end position. Every schedule's 72 stages passed independent result checks.

| Data schedule | Representation | Input positions | Output positions | Total positions | Reduction versus short-alias Python |
|---|---|---|---|---|---|
| resident | Python approved calls | 36,222 | 6,066 | 42,288 | -4.1% |
| resident | Python short aliases | 34,686 | 5,928 | 40,614 | 0.0% |
| resident | Ideal AIN | 27,144 | 3,714 | 30,858 | 24.0% |
| resident | Ideal readable IR | 27,144 | 3,714 | 30,858 | 24.0% |
| resident | Ideal Python interface | 27,144 | 3,714 | 30,858 | 24.0% |
| inspect | Python approved calls | 72,006 | 6,066 | 78,072 | -2.2% |
| inspect | Python short aliases | 70,470 | 5,928 | 76,398 | 0.0% |
| inspect | Ideal AIN | 62,928 | 3,714 | 66,642 | 12.8% |
| inspect | Ideal readable IR | 62,928 | 3,714 | 66,642 | 12.8% |
| inspect | Ideal Python interface | 62,928 | 3,714 | 66,642 | 12.8% |

Generated output falls from 5,928 measured Python text positions to 3,714 modeled ideal positions, a 37.3% conditional reduction. Total savings are smaller because shared task inputs and tool history also consume positions.

Ideal readable IR and ideal Python attain the same counts as ideal AIN under the same learned vocabulary and interface assumptions. This supports the shared mechanism of compact learned composition. The vocabulary label supplies no additional reduction in this experiment.

## Executed work and reuse

The workflows perform event filtering/deduplication/grouping, cache version selection with expiry/deletion, and idempotent publication/retry simulation. Each artifact composes five generic approved functions. Build writes a composition, change edits one parameter, repair edits one injected defect, and fresh-context handoff uses the saved artifact and memory. Working records and persisted memory are stored by the executed host actions. Checks run against separate fixture oracles before submission.

The approved core contains 10 public functions, 4 explicit for loops, 1 while loop and 7 comprehensions. Its stored Python source measures 603 text tokens. Approval and fluent core knowledge are given to every condition, so shared function bodies incur zero repeated generation cost in the primary comparison. Functions and loops run inside those approved components. Agent-authored artifacts specify their composition and arguments.

Resident data stays in host storage and is referenced through a handle. The agent receives task rules, parameters and schema, and tools expose status acknowledgements. The private judge checks complete business results. The inspect schedule also includes all records in each request context. Literal values remain in the saved fixtures and host-data byte ledger under both schedules.

## Fixed representation model

The illustrative vocabulary has 65,536 entries. Of these, 32,768 encode fifteen-bit payloads, eight encode type/atom tags and a frozen finite set encode public interface symbols. Approved signatures supply operand order and types. A program length and each operation reference cost one unit. Small signed integer operands cost one unit. Known public field references cost one unit. New strings and larger values carry type, length and packed UTF-8 payload charges. Lists and memory records carry framing and every operand/key/value. This is a fixed accounting proxy for the existing optimized-language premise.

Python text is tokenized using the cached Qwen2.5-1.5B tokenizer at the pinned revision recorded in accounting.py. A short-alias control gives approved functions and tools fixed single-letter names. Ideal controls give every representation the same compact semantic interface. Requirements use identical common text in every arm. A fixed framing charge adds four input positions per request and three per previous action/observation pair. No model inference or new language training is performed by this test.

The auxiliary `byte_fallback_units` field is a raw payload-byte diagnostic. Its call-stream integer tally supplies decimal byte lengths and is unused by the primary fifteen-bit encoding and result tables.

## Setup and repeated use

Approval, reusable core availability and fluent vocabulary knowledge are premises. An additional AIN-specific setup cost, if introduced, is an unknown fixed cost F. The table below gives the maximum additional setup positions recoverable from the conditional resident-data saving, under the same equal-cost assumption. It supplies a break-even boundary for an entered setup cost.

| Repeated four-stage chains | Additional setup positions recoverable |
|---|---|
| 1 | 542 |
| 10 | 5,420 |
| 100 | 54,200 |
| 1,000 | 542,000 |

For positive F, the corresponding break-even count is F divided by the saving per chain. Training hours, financial cost, power consumption and maintenance cost have separate units and would require their own measured conversion.

## Limits and audit

The 18 chains are six parameter/data variants of three fixed composition templates. The two schedules replay the same tasks. They establish executable accounting cases. Core approval alone leaves planning uncertain, so this experiment adds a perfect-composer assumption to isolate resource demand. New functions and arbitrary new control-flow implementations require further cases. Actual trained-agent correctness, inference speed and success-adjusted compute remain open measurements.

The manifest freezes codebook, aliases, source hashes, fixture hash and assumptions before measurement. The accompanying tests check fixture behavior and accounting. Reproduction-harness outcomes are recorded in the rerun test log. This report verifies frozen hashes and replays every saved artifact. The raw episodes preserve input contexts, all actions, host observations, working records, persisted memory, business-data bytes and per-request ledgers. Timing of shared host execution is retained as a separate diagnostic.
