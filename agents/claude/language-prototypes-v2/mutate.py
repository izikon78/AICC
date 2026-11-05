import random, signal, types, math, string, json, contextlib
from lang import *
TESTS = [0, 1, 2, 3, 5, -1]
A_SRC = 'fn main(n:i32){for i<n{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {n}"}}}'
PY_SRC = open("progs/main.py").read()
REF = [[t[1] for t in run(parse_a(A_SRC), "main", [n])] for n in TESTS]     # equals the .NET traces
CLS = {"lower": string.ascii_lowercase, "upper": string.ascii_uppercase, "digit": string.digits,
       "punct": "()[]{}:;,.<>=+-*/%!?\"'&|_@#^~"}
def cls_of(c):
    for k, v in CLS.items():
        if c in v: return k
    return None
def mutable_positions(src):
    pos, in_str, in_hole = [], False, False
    for k, c in enumerate(src):
        if c == '"' and not in_hole:
            pos.append(k); in_str = not in_str; continue
        if in_str and c == "{" and not in_hole: in_hole = True; pos.append(k); continue
        if in_str and c == "}" and in_hole: in_hole = False; pos.append(k); continue
        if (not in_str or in_hole) and not c.isspace() and cls_of(c): pos.append(k)
    return pos
class Timeout(Exception): pass
@contextlib.contextmanager
def limit(sec=1):
    def h(*a): raise Timeout()
    old = signal.signal(signal.SIGALRM, h); signal.alarm(sec)
    try: yield
    finally: signal.alarm(0); signal.signal(signal.SIGALRM, old)
class Log:
    def __init__(self): self.lines = []
    def info(self, s): self.lines.append(s)
def eval_py(src):
    try: code = compile(src, "m", "exec")
    except (SyntaxError, ValueError): return "rejected before running"
    try:
        ns = {}
        with limit(): exec(code, ns)
        fn = ns.get("main")
        if not callable(fn): return "crashed while running"
        outs = []
        for n in TESTS:
            obj = types.SimpleNamespace(m_log=Log())
            with limit(): fn(obj, n)
            outs.append(obj.m_log.lines)
    except Exception: return "crashed while running"
    return "harmless" if outs == REF else "silently wrong"
def eval_mod(m):
    try:
        outs = [[t[1] for t in run(m, "main", [n])] for n in TESTS]
    except Exception: return "crashed while running"
    return "harmless" if outs == REF else "silently wrong"
def eval_a(src):
    try: m = parse_a(src); check(m)
    except LangError: return "rejected before running"
    return eval_mod(m)
def eval_b(hdr, toks):
    try: m = decode_b(hdr, toks); check(m)
    except LangError: return "rejected before running"
    return eval_mod(m)
def mutate_text(src, rng):
    k = rng.choice(mutable_positions(src)); c = src[k]
    return src[:k] + rng.choice([x for x in CLS[cls_of(c)] if x != c]) + src[k + 1:]
def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = p + z * z / (2 * n); r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - r) / d, (c + r) / d
CATS = ["rejected before running", "crashed while running", "silently wrong", "harmless"]
def report(name, outcomes):
    n = len(outcomes); row = {}
    print(f"{name} (n={n}):")
    for c in CATS:
        k = outcomes.count(c); lo, hi = wilson(k, n); row[c] = [k, n, round(100 * k / n, 1), round(100 * lo, 1), round(100 * hi, 1)]
        print(f"   {c:26s} {100 * k / n:5.1f}%  [{100 * lo:4.1f}, {100 * hi:4.1f}]")
    return row
N = 4000; out = {}
rng = random.Random(20261102)
assert eval_py(PY_SRC) == "harmless" and eval_a(A_SRC) == "harmless"
out["Python (character, same class)"] = report("Python (character, same class)", [eval_py(mutate_text(PY_SRC, rng)) for _ in range(N)])
out["Language A (character, same class)"] = report("Language A (character, same class)", [eval_a(mutate_text(A_SRC, rng)) for _ in range(N)])
hdr, toks = encode_b(parse_a(A_SRC), inline_strings=True)
assert eval_b(hdr, toks) == "harmless"
op_pos = [k for k, t in enumerate(toks) if isinstance(t, str)]
def mut_b(same_class):
    k = rng.choice(op_pos); t = toks[k]
    if same_class:
        pool = next(v for v in CLASSES.values() if t in v) if any(t in v for v in CLASSES.values()) else STRUCT
    else:
        pool = [v for v in VOCAB if not v.startswith("X")]
    new = list(toks); new[k] = rng.choice([x for x in pool if x != t]); return new
out["Language B (opcode, same class)"] = report("Language B (opcode, same class)", [eval_b(hdr, mut_b(True)) for _ in range(N)])
out["Language B (opcode, any opcode)"] = report("Language B (opcode, any opcode)", [eval_b(hdr, mut_b(False)) for _ in range(N)])
print("mutable sites: Python", len(mutable_positions(PY_SRC)), "| A", len(mutable_positions(A_SRC)), "| B opcodes", len(op_pos))
json.dump(out, open("mutation_results.json", "w"), indent=1)
