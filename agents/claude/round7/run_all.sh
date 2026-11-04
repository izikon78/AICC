#!/usr/bin/env bash
# Reproduce every Round 7 result in this report. Run from the packet root (Python 3.10+).
# Token steps need tiktoken with o200k_base/cl100k_base available; see tools/README_tokenizer.md for offline setup.
set -u
sec() { echo; echo "=================================================================== $*"; }
sec "ARM A: python fixtures/test_tasks.py --submission submission.py";            python3 fixtures/test_tasks.py --submission submission.py
sec "ARM B: python fixtures/test_tasks.py --submission submission_registry.py";   python3 fixtures/test_tasks.py --submission submission_registry.py
sec "ARM C: python fixtures/test_tasks.py --python-controller controller_submission.py"; python3 fixtures/test_tasks.py --python-controller controller_submission.py
sec "ARM D: python fixtures/test_tasks.py --symbolic controller_submission.sym";  python3 fixtures/test_tasks.py --symbolic controller_submission.sym
sec "H3: python fixtures/binding_checks.py";                                      (cd fixtures && python3 binding_checks.py)
for n in zero_based by_eventid and_save; do
  sec "COUNTEREXAMPLE $n: python fixtures/test_tasks.py --submission counterexamples/submission_$n.py"
  python3 fixtures/test_tasks.py --submission counterexamples/submission_$n.py 2>&1 | python3 -c "import sys, json; raw = sys.stdin.read()
try:
    d = json.loads(raw); print(json.dumps({\"passed\": d[\"passed\"], \"total\": d[\"total\"], \"failed\": [c[\"case\"] for c in d[\"cases\"] if not c[\"pass\"]]}))
except Exception: print(raw.strip().splitlines()[-1])"
done
sec "ADVERSARIAL contract tests (held-out, black-box)";                           python3 adversarial_contract_tests.py submission.py submission_registry.py
sec "INDEPENDENT contract-only implementation through the harness";              python3 fixtures/test_tasks.py --submission contract_reimpl.py
for v in variants/v1_severity_names.py variants/v2_plus_severity_trim.py variants/v3_plus_message_split.py; do
  sec "VARIANT $v";                                                               python3 fixtures/test_tasks.py --submission $v
done
sec "DIFFERENTIAL fuzz: reused capability vs contract-only implementation";      python3 differential_fuzz.py
sec "TOKENS: python fixtures/token_measure.py (unmodified)";                     python3 fixtures/token_measure.py
sec "TOKENS + H3 payloads: python h3_payloads.py";                               python3 h3_payloads.py
sec "H2 probes: python h2_symbolic_probe.py";                                     python3 h2_symbolic_probe.py
sec "H3 trust probes: python h3_trust_probe.py";                                  python3 h3_trust_probe.py
sec "H3 binding cache prototype: python h3_binding_cache.py";                     python3 h3_binding_cache.py
