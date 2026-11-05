import json, types
from lang import *

REF = {0: [], 1: ["Starting controller service for 1 runs"],
       3: ["Starting controller service for 3 runs", "Restarting controller service for run 2 of 3",
           "Restarting controller service for run 3 of 3"], -2: []}           # captured from the .NET 8 run
NS = [0, 1, 3, -2]
A_IFELSE = 'fn main(n:i32){for i<n{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {n}"}}}'
A_TERN = 'fn main(n:i32){for i<n{log(i==0?"Starting controller service for {n} runs":"Restarting controller service for run {i+1} of {n}")}}'
A_TPL = 'tpl t0="Starting controller service for {0} runs";tpl t1="Restarting controller service for run {0} of {1}";\nfn main(n:i32){for i<n{if i==0{log(t0(n))}else{log(t1(i+1,n))}}}'

def msgs(trace): return [t[1] for t in trace]
results = {}
for name, src in [("A_ifelse", A_IFELSE), ("A_ternary", A_TERN), ("A_templates", A_TPL)]:
    m = parse_a(src); check(m)
    ok = all(msgs(run(m, "main", [n])) == REF[n] for n in NS)
    hdr, toks = encode_b(m); m2 = decode_b(hdr, toks); check(m2)
    ok_b = all(msgs(run(m2, "main", [n])) == REF[n] for n in NS)
    rt = print_a(m2, headers=False) == print_a(m, headers=False)
    print(f"{name}: traces match C# = {ok}; B round-trip traces match = {ok_b}; A->B->A text identical = {rt}")
    print("   B tokens:", " ".join(toks), f"({len(toks)} tokens)")
    print("   B templates:", hdr["templates"], "| binary bytes:", len(b_bytes(hdr, toks)))
    results[name] = {"src": src, "b_tokens": toks, "b_templates": hdr["templates"], "b_bytes": len(b_bytes(hdr, toks))}

m = parse_a(A_IFELSE)
for n in [0, 1, 3]:
    print(f"\nTRACE n={n}:")
    for ev in run(m, "main", [n]): print("   ", ev[0], "|", ev[1])
    if not run(m, "main", [n]): print("    (no effects)")

py = proj_py(m); cs = proj_cs(m)
print("\nPython projection:\n" + py); print("\nC# projection:\n" + cs)
class Log:
    def __init__(self): self.lines = []
    def info(self, s): self.lines.append(s)
ns = {"_chk32": lambda x: x}; exec(py, ns)
ok_py = True
for n in NS:
    obj = types.SimpleNamespace(m_log=Log()); ns["main"](obj, n); ok_py &= obj.m_log.lines == REF[n]
print("\nPython projection traces match C# =", ok_py)
open("proj.cs", "w").write(cs); json.dump(results, open("a_b_results.json", "w"), indent=1)

print("\n--- BUG CASES ---")
bug1 = 'fn main(n:i32){for i in 1..<n+1{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {i}"}}}'
mb = parse_a(bug1); check(mb)
for n in [0, 1, 3]: print(f"rough-sketch semantics (1..m inclusive, 'of {{i}}') n={n}:", msgs(run(mb, 'main', [n])))
bug3 = A_IFELSE.replace("of {n}", "of {i}")
for n in [0, 1, 3]: print(f"'of {{i}}' only, n={n}:", msgs(run(parse_a(bug3), 'main', [n])))
bug4 = A_IFELSE.replace("for i<n", "for i in 1..<n+1")
for n in [0, 1, 3]: print(f"'1..m' only, n={n}:", msgs(run(parse_a(bug4), 'main', [n])))
try:
    check(parse_a(A_TPL.replace("t1(i+1,n)", "t1(i+1)")))
except LangError as e: print("A missing template argument ->", e)
m = parse_a(A_TPL); hdr, toks = encode_b(m)
for label, bad in [("drop final P0", toks[:-1]), ("drop C1 (middle)", [t for k, t in enumerate(toks) if not (t == "C1")])]:
    try:
        mm = decode_b(hdr, bad); check(mm); print("B", label, "-> accepted?!", msgs(run(mm, "main", [3])))
    except LangError as e: print("B", label, "->", e)
