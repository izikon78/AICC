"""H2 probes on the toy symbolic language (fixtures/symbolic_runtime.py):
1. exhaustive single-token mutations of the Arm D program -> rejected / crashed / silently wrong / harmless
2. identifier-lexing hazard: names starting with R or I, or T0/T1 prefixes
3. cross-arm divergence outside the tested domain (bool input)
4. fair token comparison: Python with the same host-held templates as the symbolic program"""
import json, sys
sys.path.insert(0, "fixtures")
import symbolic_runtime as S
import tiktoken
O = tiktoken.get_encoding("o200k_base")
PROG = open("controller_submission.sym").read()
NS = [-2, 0, 1, 2, 3, 17]
REF = {n: S.execute(PROG, n) for n in NS}
toks = S.lex(PROG)
CLASSES = {"digit": [str(d) for d in range(10)], "ident": ["n", "i", "x"], "tpl": ["T0", "T1"],
           "punct": ["(", ")", "{", "}", ",", "=", "+", ":"], "op": ["R", "?", "!", "@", "I"]}
def cls(t):
    if t.isdigit(): return "digit"
    if t in ("T0", "T1"): return "tpl"
    if t in ("R", "?", "!", "@", "I"): return "op"
    if t in CLASSES["punct"]: return "punct"
    return "ident"
def judge(src):
    try: S.compile_program(src)
    except S.SyntaxErrorIR: return "rejected by grammar"
    except Exception as e: return "parser crash (non-grammar exception)"
    try: out = {n: S.execute(src, n) for n in NS}
    except Exception: return "crashed while running"
    return "harmless" if out == REF else "silently wrong"
results, examples = {}, {}
for k, t in enumerate(toks):
    for alt in CLASSES[cls(t)]:
        if alt == t: continue
        src = "".join(toks[:k] + [alt] + toks[k + 1:])
        r = judge(src); results[r] = results.get(r, 0) + 1
        if r == "silently wrong": examples.setdefault(src, f"token {k}: {t!r} -> {alt!r}")
total = sum(results.values())
print(f"1. single-token mutations of Arm D program: {total} mutants")
for r in ["rejected by grammar", "parser crash (non-grammar exception)", "crashed while running", "silently wrong", "harmless"]:
    print(f"   {r:24s} {results.get(r, 0):4d}  ({100 * results.get(r, 0) / total:.1f}%)")
crash_ex = next(("".join(toks[:k] + [alt] + toks[k + 1:]), t, alt) for k, t in enumerate(toks) for alt in CLASSES[cls(t)] if alt != t and judge("".join(toks[:k] + [alt] + toks[k + 1:])).startswith("parser crash"))
print(f"   example parser crash: {crash_ex[0]}  ({crash_ex[1]!r} -> {crash_ex[2]!r})")
print("   examples of silently wrong programs that the grammar accepts:")
for src, why in list(examples.items())[:6]: print(f"     {src:50s} ({why})")
print("\n2. identifier-lexing hazard (same program, different names):")
for p, ix in [("n", "i"), ("count", "k"), ("Runs", "i"), ("n", "Idx"), ("Items", "j"), ("T1x", "i")]:
    src = f"@1({p}:I){{R({p},{ix}){{?({ix}=0,!7(T0,{p}),!7(T1,{ix}+1,{p}))}}}}"
    try: S.compile_program(src); ok = all(S.execute(src, n) == REF[n] for n in NS); verdict = "ok" if ok else "WRONG OUTPUT"
    except S.SyntaxErrorIR as e: verdict = f"rejected: {e}"
    except Exception as e: verdict = f"parser crash: {type(e).__name__}: {e}"
    print(f"   param={p!r:8s} index={ix!r:6s} -> {verdict}   lexed as {S.lex(src)[2:4]}")
print("\n3. bool input outside the tested domain:")
for label, fn in [("Arm D symbolic runtime", lambda: S.execute(PROG, True))]:
    try: print(f"   {label}: {fn()!r}")
    except Exception as e: print(f"   {label}: raises {type(e).__name__}")
sys.path.insert(0, ".")
import importlib.util
def load(p):
    s = importlib.util.spec_from_file_location(p.replace(".", "_"), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
for label, fn in [("Arm A/B reused capability", lambda: load("submission.py").run_controller(True)), ("Arm C new Python", lambda: load("controller_submission.py").controller_logs(True))]:
    try: print(f"   {label}: {fn()!r}")
    except Exception as e: print(f"   {label}: raises {type(e).__name__}")
print("\n4. fair token comparison (o200k_base, tiktoken 0.14.0):")
fair = {"Arm D symbolic program": PROG,
        "Python, same host-held templates T0/T1": "def f(n):return[T0(n)if i==0 else T1(i+1,n)for i in range(n)]",
        "Python, templates inline (minimal)": 'def f(n):return[f"Starting controller service for {n} runs"if i==0 else f"Restarting controller service for run {i+1} of {n}"for i in range(n)]',
        "grammar documentation the author needed (symbolic_runtime.py)": open("fixtures/symbolic_runtime.py").read()}
for k, v in fair.items(): print(f"   {k:62s} bytes {len(v.encode()):5d}  tokens {len(O.encode(v)):5d}")
ns = {"T0": lambda n: f"Starting controller service for {n} runs", "T1": lambda a, b: f"Restarting controller service for run {a} of {b}"}
exec(fair["Python, same host-held templates T0/T1"], ns)
print("   fair Python variant passes the six T1 inputs:", all(ns["f"](n) == REF[n] for n in NS))
json.dump({"mutations": results, "total": total}, open("h2_probe_results.json", "w"), indent=1)
