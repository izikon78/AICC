import json, dataclasses
from tok import count, COLS
from lang import parse_a, encode_b
R = json.load(open("a_b_results.json"))
P = lambda f: open(f"progs/{f}").read().rstrip("\n")
S0, S1 = "Starting controller service for {} runs", "Restarting controller service for run {} of {}"
TABLE = 'T0="Starting controller service for {} runs"\nT1="Restarting controller service for run {} of {}"\n'
SPEC = open("spec_a.txt").read()
def b_text(name):
    r = R[name]; hdr = "".join(f'TPL "{t}"\n' for t in r["b_templates"]); return hdr + " ".join(r["b_tokens"])
def ast_json(src):
    m = parse_a(src)
    def conv(o):
        if dataclasses.is_dataclass(o): return {"k": type(o).__name__, **{f.name: conv(getattr(o, f.name)) for f in dataclasses.fields(o)}}
        if isinstance(o, (list, tuple)): return [conv(x) for x in o]
        if isinstance(o, dict): return {k: conv(v) for k, v in o.items()}
        return o
    return json.dumps(conv(m.fns[0]), separators=(",", ":"))
reps = {
 "C# original": P("main.cs"), "C# minified": P("main_min.cs"),
 "Python": P("main.py"), "Python minified": P("main_min.py"),
 "Brief rough sketch (buggy)": '<-/n_m(i.m){_f_i=1..m->_i(i=0)->..log($"Starting controller service for {m} runs")_ls->..log($"Restarting controller service for run {i+1} of {i}")}',
 "Brief @1 syntax, code only": "@1(n:I){R(i:0<n){?(i=0):!7(T0,n):!7(T1,i+1,n)}}",
 "Brief @1 syntax + template table": TABLE + "@1(n:I){R(i:0<n){?(i=0):!7(T0,n):!7(T1,i+1,n)}}",
 "A, if/else, inline strings": R["A_ifelse"]["src"], "A, ternary, inline strings": R["A_ternary"]["src"],
 "A, interned templates": R["A_templates"]["src"],
 "B as mnemonic text (existing tokenizer)": b_text("A_ifelse"),
 "Forth (gforth-verified)": P("main.fs"), "APL (dfn, not executed)": P("main.apl"), "Racket": P("main.rkt"),
 "WAT, code only (strings in host)": P("main.wat"), "CPython disassembly text": P("main.dis"),
 "JSON AST (compact)": ast_json(R["A_ifelse"]["src"]),
 "Strings alone (content floor)": S0 + "\n" + S1,
 "Language A spec (in-context, per session)": SPEC,
}
res = count(reps)
# B with a dedicated vocabulary: opcode tokens are 1 each; templates use the base tokenizer + 2 delimiters each
tpl_only = count({"t": "\n".join(R["A_ifelse"]["b_templates"])})["t"]
for v, label in [("A_ifelse", "B dedicated vocab, if/else"), ("A_ternary", "B dedicated vocab, ternary")]:
    n_ops = len(R[v]["b_tokens"])
    res[label] = {c: (n_ops + tpl_only[c] + 4 if c not in ("chars", "bytes") else "-") for c in COLS}
    res[label]["bytes"] = R[v]["b_bytes"]
json.dump(res, open("token_results.json", "w"), indent=1)
w = max(len(k) for k in res) + 2
print("name".ljust(w) + "".join(c.rjust(11) for c in COLS))
for k, v in res.items(): print(k.ljust(w) + "".join(str(v[c]).rjust(11) for c in COLS))
