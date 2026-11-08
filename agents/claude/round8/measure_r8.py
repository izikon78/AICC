"""Artefact token counts (tiktoken o200k_base). Text artefacts only: NOT model input/output/reasoning telemetry."""
import hashlib, json, os, tiktoken
O = tiktoken.get_encoding("o200k_base")
FILES = ["benchmark/public/API_CONTRACTS.md", "benchmark/public/TASKS.md", "submission_A.py", "submission_B.py", "private_arm.py",
         "conventional_envelope.py", "agreement/group_by_window.contract.yaml", "agreement/alt_python.py", "agreement/alt_js_naive.js",
         "agreement/alt_js_faithful.js", "agreement/tables/python_whitespace.json", "agreement/tables/casefold_full.json",
         "agreement/conformance_vectors.json"]
res = {}
for f in FILES:
    b = open(f, "rb").read(); res[f] = {"bytes": len(b), "o200k": len(O.encode(b.decode("utf-8"))), "sha256": hashlib.sha256(b).hexdigest()}
    print(f"{f:44s} bytes {len(b):8d}  o200k {res[f]['o200k']:7d}  sha256 {res[f]['sha256'][:16]}")
contract_row = next(l for l in open("benchmark/public/API_CONTRACTS.md").read().splitlines() if l.startswith("| `group_by_window"))
for label, text in [("shared contract row for group_by_window", contract_row),
                    ("Arm A import of one capability", "from benchmark.public.baseline_api import group_by_window"),
                    ("Arm B bind of one capability", 'group_by_window = _rt.bind("pub.group_by_window@1")')]:
    res[label] = {"bytes": len(text.encode()), "o200k": len(O.encode(text))}; print(f"{label:44s} bytes {res[label]['bytes']:8d}  o200k {res[label]['o200k']:7d}")
json.dump(res, open("token_results_r8.json", "w"), indent=1)
