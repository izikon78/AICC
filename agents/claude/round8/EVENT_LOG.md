# Round 8 event log (files opened, inspections, retries)
2026-11-03T16:51:21Z  sha256sum -c SHA256SUMS.txt: all 21 files OK (fixture unchanged)
2026-11-03T16:51:21Z  Read: 00_SEND_TO_ALL_AGENTS.md, README.md, 01_EXPERIMENT_PROTOCOL.md, 02_RESULTS_TEMPLATE.md, ROUND7_LESSONS.md, ARTICLE_ADDENDUM.md, ARCHITECTURE_RECOMMENDATION.md (identical to the uploaded copy)
2026-11-03T16:51:21Z  Read (public, common to both arms): benchmark/public/API_CONTRACTS.md, benchmark/public/TASKS.md, benchmark/public/baseline_api.py
2026-11-03T16:51:48Z  Selection decisions recorded before tests (SELECTION_DECISIONS_BEFORE_TESTS.md)
2026-11-03T16:51:48Z  API introspection of benchmark.host.registry: names, signatures, docstrings only (no source printed)
2026-11-03T16:52:22Z  INSPECT (black-box probe, no source): called filter_by_severity with 'warning', 2, 'WARNING' because the contract does not state the type of 'minimum' (UNKNOWN).
2026-11-03T16:53:44Z  Arm A 20/20, Arm B 20/20, first attempt, 0 retries, 0 sealed files opened.
2026-11-03T16:54:27Z  --self-test 20/20 (organiser fixtures, not an agent result); --security 3/3.
2026-11-03T16:54:28Z  Arm C checks and host probes run (probe_host.py). private_core names listed via dir(); no sealed source printed.
2026-11-03T16:55:34Z  Corrected probes P4, P6, P7 (catalogue injection; on-disk edit after bind in temp copy; pre-import module substitution in temp copy). Fixture files unchanged.
2026-11-03T16:56:03Z  Incidental exposure: P7 traceback printed one registry.py line (_METADATA built from public_core.__file__). No sealed source printed.
2026-11-03T16:56:50Z  18 black-box probes of group_by_window (agreement track), no source.
2026-11-03T16:56:54Z  18 black-box probes of group_by_window (agreement track), no source.
2026-11-03T19:27:11Z  Agreement-track differential run (reference vs alt_python, alt_js_naive, alt_js_faithful).
2026-11-03T19:27:46Z  Contract-insufficiency probes run (gzip, canonical_json, make_query, toposort, png_dimensions, normalize_tag).
2026-11-03T19:28:15Z  Conventional policy-envelope baseline run.
2026-11-03T19:28:31Z  Read benchmark/token_measure.py (measurement script).
2026-11-03T19:31:47Z  Found 14 files dated 16:41-16:48 UTC from an earlier, interrupted attempt in this sandbox (before this log began at 16:51). Not opened in this session; moved unread to ../_quarantine_earlier_attempt/ except for the draft report's first 12 lines, viewed to identify it. Not used.
2026-11-03T19:32:58Z  Report written; deliverables packaged (fixture and quarantined files excluded).
