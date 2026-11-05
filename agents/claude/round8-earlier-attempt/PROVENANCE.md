# Earlier Claude Round 8 attempt (the revision the GPT-6 audit and Draft 4 describe)

These 14 files were written by Claude Opus 5.5 between 16:41 and 16:48 UTC on 2026-11-03, in a Round 8 attempt that was
interrupted before delivery in the visible conversation. A later attempt in the same conversation (log from 16:51 UTC)
produced `../round8/`. The later attempt found these files in the sandbox, moved them unread to a quarantine folder and
disclosed that in `../round8/Round8_Results_Claude_Opus_5.5.md`, section 0. They are published here unchanged so the
audited claims can be checked. `SHA256SUMS.txt` lists their hashes.

Reruns on 2026-11-04 against the hash-verified frozen Round 8 packet (21/21 OK), files unmodified:
- `multiagent_contract.py`: 3,127 mismatches in 5,000 inputs, identical to the recorded figure.
- `reimpl_fuzz.py`: 14,000 of 14,000 agreements, identical to `reimpl_fuzz_results.json`.

Corrections to this draft (details in `../cross-review/CROSS_REVIEW_2026-11-04.md`):
1. The 3,127 disagreements come from `impl_bucketed` violating the output-order rule its own contract states, as the GPT-6
   audit found. The draft's claim that the contract "never fixed" output order is withdrawn.
2. The 14,000-agreement fuzz used ASCII-only device and kind strings for `group_by_window`. On the later 1,206 adversarial
   Unicode vectors, the same contract-only `group_by_window` agrees with the reference on 467 of 1,206.
3. The draft's 18/20 first run, repaired to 20/20, is this attempt's first exposure. The later attempt reached 20/20 after a
   pre-test probe of the same ambiguity (`filter_by_severity` minimum is an integer).
