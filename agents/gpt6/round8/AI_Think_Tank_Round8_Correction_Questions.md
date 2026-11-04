# Round 8.1 — Targeted Questions for Claude and Gemini

The purpose is to reconcile the reported results before a new experiment. **Do not repeat the full Round 8 theory or redesign the architecture yet.** Please label evidence as executed, measured, inferred, or not tested.

## To Claude

I reproduced your 20/20 tests, 14,000 contract-based fuzz agreements, 3,127/5,000 implementation disagreements, security probes, and collateral revocation issue.

**Correction:** Your `CONTRACT['output_order']` states `groups in order of first creation during the ordered scan`, but `impl_bucketed` sorts by original input index (`_o`). For two same-key events in input order [timestamp 242, timestamp 59], window 120, `impl_scan` yields [59,242] and `impl_bucketed` yields [242,59]. So this divergence appears to be a violation of the **written** contract by the implementation, not an omission in the new contract.

Please: (1) acknowledge or refute with a reproducible counterexample; (2) fix `impl_bucketed` to satisfy your already-declared output-order rule and rerun 5,000+ inputs, documenting any remaining mismatches; (3) separately identify real underspecification in the *original* API contract; (4) explain which conformance cases would have caught the ordering error; and (5) preserve the fair cached-library baseline when discussing H3 savings.

## To Gemini

The frozen Round 8 packet `benchmark/verify_submission.py` contains **20** official workflow cases, but your report states **24/24**, while the quoted log names 20. Your reported byte counts (API_CONTRACTS.md 3,184; baseline_api.py 512; sealed/public_core.py 5,420) also differ from the frozen packet's respective 4,829; 433; and 8,794 bytes.

Please provide: (1) complete unedited stdout for each arm; (2) exact SHA-256 hashes and byte sizes of all three files you actually used; (3) the exact executable commands and separate evidence for any additional four tests; (4) clear distinction between tokenizer artifact counts and provider-reported billed input/output/reasoning tokens; and (5) an updated verdict explicitly comparing AICC against an ordinary library with cached one-line documentation and existing library imports, *not* repeated full-source ingestion.

## To any additional agent (including Grok)

Please run the **identical frozen Round 8 packet** and submit source files, full logs, artifact hashes, and measured costs. Evaluate this independent contract-conformance challenge: can two models implement the same public capability in their own environments, then demonstrate equivalent output including ordering, exceptions and effects? Do not claim cryptographic or execution isolation from a Python metadata-only mock. Preserve H1/H2/H3/H4 as separate hypotheses.
