"""Tokenizer measurements (tiktoken o200k_base) of the artefacts each approach requires. Text artefacts only:
NOT model-billed input/output/reasoning tokens."""
import json, tiktoken
O = tiktoken.get_encoding("o200k_base")
R8 = "/home/claude/r8/AI_Think_Tank_Round8_Packet/"; R7 = "/home/claude/r7/AI_Think_Tank_Round7_Test_Packet/"
f = lambda p: open(p, encoding="utf-8").read()
items = [
 ("A conventional", "R8 tasks 1-8 solution (submission_A.py)", f(R8 + "submission_A.py")),
 ("A conventional", "R8 shared docs read (API_CONTRACTS.md + TASKS.md)", f(R8 + "benchmark/public/API_CONTRACTS.md") + f(R8 + "benchmark/public/TASKS.md")),
 ("B AICC", "R8 tasks 1-8 solution (submission_B.py)", f(R8 + "submission_B.py")),
 ("B AICC", "R8 docs read (same shared docs; no smaller cards exist in the packet)", f(R8 + "benchmark/public/API_CONTRACTS.md") + f(R8 + "benchmark/public/TASKS.md")),
 ("A conventional", "R7 controller in Python (controller_submission.py)", f(R7 + "controller_submission.py")),
 ("A conventional", "R7 controller, Python with the same host-held templates", "def f(n):return[T0(n)if i==0 else T1(i+1,n)for i in range(n)]"),
 ("C symbolic", "R7 controller in toy symbolic grammar (.sym)", f(R7 + "controller_submission.sym")),
 ("C symbolic", "R7 grammar documentation the author read (symbolic_runtime.py)", f(R7 + "fixtures/symbolic_runtime.py")),
 ("C symbolic", "v2 Language A controller (if/else)", 'fn main(n:i32){for i<n{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {n}"}}}'),
 ("C symbolic", "v2 Language A reference sheet (per session)", f("/home/claude/sym/spec_a.txt")),
]
rows = []
for arm, label, text in items:
    rows.append({"arm": arm, "artefact": label, "bytes": len(text.encode()), "o200k_tokens": len(O.encode(text))})
    print(f"  {arm:15s} {label:72s} bytes {rows[-1]['bytes']:6d}  tokens {rows[-1]['o200k_tokens']:5d}")
print("  D symbolic+AICC  NOT EXECUTED: neither toy grammar can express the R8 tasks (no dicts, lists, sorting or library calls)")
json.dump(rows, open("token_table.json", "w"), indent=1)
