#!/usr/bin/env bash
# Reproduce every Round 8 result in this report. Run from the extracted AI_Think_Tank_Round8_Packet directory.
# Needs Python 3.10+, Node.js (agreement track), tiktoken with o200k_base (see tools/README_tokenizer.md).
set -u
sec() { echo; echo "=================================================================== $*"; }
sec "INTEGRITY: sha256sum -c SHA256SUMS.txt";                     sha256sum -c SHA256SUMS.txt
sec "SELF-TEST (organiser fixtures, not an agent result)";        python3 -m benchmark.verify_submission --self-test | python3 -c "import sys,json; d=json.load(sys.stdin); print('self-test', d['passed'], '/', d['total'])"
sec "SECURITY: python -m benchmark.verify_submission --security"; python3 -m benchmark.verify_submission --security
sec "ARM A: python -m benchmark.verify_submission --submission submission_A.py"; python3 -m benchmark.verify_submission --submission submission_A.py
sec "ARM B: python -m benchmark.verify_submission --submission submission_B.py"; python3 -m benchmark.verify_submission --submission submission_B.py
sec "ARM C task 9: project_risk through the host";                python3 -c "from private_arm import project_risk; print('project_risk(event) ->', project_risk({'severity': 'critical'}))"
sec "ARM C checks + adversarial host probes";                     python3 probe_host.py
sec "ARM C fair baseline: conventional policy envelope";          python3 conventional_envelope.py
sec "AGREEMENT: black-box probes of group_by_window";             python3 agreement/probe_group_by_window.py
sec "AGREEMENT: differential test of three independent variants"; python3 agreement/differential.py
sec "CONTRACT INSUFFICIENCY probes";                              python3 contract_insufficiency.py
sec "TOKENS: python -m benchmark.token_measure submission_A.py submission_B.py"; python3 -m benchmark.token_measure submission_A.py submission_B.py
sec "TOKENS + SHA-256 of generated artefacts";                    python3 measure_r8.py
sec "INTEGRITY after all runs";                                   sha256sum -c SHA256SUMS.txt | grep -c ': OK'
