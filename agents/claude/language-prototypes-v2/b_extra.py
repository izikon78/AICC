import json, math
from tok import count
from lang import *
R = json.load(open("a_b_results.json"))
# --- B with inline strings: STRB <text tokens> <hole opcodes> ... STRE ; text pieces use the base tokenizer
ops_if = ["FN1","TI32","TUNIT","FOR","P0","IF","EQ","L0","C0","EFF","K0","STRB","<t1>","P0","<t2>","STRE",
          "EFF","K0","STRB","<t3>","ADD","L0","C1","<t4>","P0","STRE"]
ops_tern = ["FN1","TI32","TUNIT","FOR","P0","EFF","K0","SEL","EQ","L0","C0","STRB","<t1>","P0","<t2>","STRE",
            "STRB","<t3>","ADD","L0","C1","<t4>","P0","STRE"]
pieces = {"<t1>": "Starting controller service for ", "<t2>": " runs", "<t3>": "Restarting controller service for run ", "<t4>": " of "}
pc = count(pieces)
for label, ops in [("B inline strings, if/else", ops_if), ("B inline strings, ternary", ops_tern)]:
    tot = {c: sum(pc[o][c] if o in pieces else 1 for o in ops) for c in ["o200k", "cl100k", "llama3", "qwen25", "deepseekv3", "gemma3"]}
    print(label, "opcode tokens:", sum(1 for o in ops if o not in pieces), "| total by tokenizer:", tot)
print("text pieces:", {k: v["o200k"] for k, v in pc.items()})

# --- constrained decoding: how many tokens are legal at each position of the B program?
def legal_sets(header, toks, ptypes):
    caps = header["caps"]; ntpl = len(header["templates"]); ar = [tpl_arity(t) for t in header["templates"]]
    stack = [("fn",)]; out = []
    def expr_tokens(ty, nb):
        s = set()
        if ty in ("i32", "fmt"):
            s |= set(OPS[:5]) | set(f"C{i}" for i in range(16)) | {"CI32"} | {f"L{k}" for k in range(nb)}
            s |= {f"P{k}" for k, t in enumerate(ptypes) if t == "i32"}
        if ty in ("bool", "fmt"):
            s |= set(OPS[5:]) | set(BOOLS) | {f"P{k}" for k, t in enumerate(ptypes) if t == "bool"}
        if ty in ("str", "fmt"):
            s |= {f"TP{k}" for k in range(ntpl)} | {f"P{k}" for k, t in enumerate(ptypes) if t == "str"}
        return s | {"SEL"}
    for t in toks:
        slot = stack.pop()
        if slot[0] == "fn": legal = {"FN0", "FN1", "FN2", "FN3"}
        elif slot[0] == "type": legal = set(TYPEV) - ({"TUNIT"} if slot[1] == "param" else set())
        elif slot[0] == "stmt": legal = {"BLK", "FOR", "FORR", "IF", "IF1", "EFF"}
        elif slot[0] == "cap": legal = {f"K{k}" for k in range(len(caps))}
        elif slot[0] == "expr": legal = expr_tokens(slot[1], slot[2])
        out.append((t, len(legal), t in legal))
        if slot[0] == "fn":
            k = int(t[2:]); stack += [("stmt", 0)] + [("type", "ret")] + [("type", "param")] * k
        elif slot[0] == "stmt":
            nb = slot[1]
            if t == "FOR": stack += [("stmt", nb + 1), ("expr", "i32", nb)]
            elif t == "IF": stack += [("stmt", nb), ("stmt", nb), ("expr", "bool", nb)]
            elif t == "EFF": stack += [("cap",)]; pending_nb = nb
        elif slot[0] == "cap":
            sig = caps[int(t[1:])][2]; stack += [("expr", "str", pending_nb)] * len(sig)
        elif slot[0] == "expr":
            nb = slot[2]
            if t in OPS[:5]: stack += [("expr", "i32", nb)] * 2
            elif t in OPS[5:11]: stack += [("expr", "i32", nb)] * 2
            elif t in ("AND", "OR"): stack += [("expr", "bool", nb)] * 2
            elif t == "SEL": stack += [("expr", slot[1], nb)] * 2 + [("expr", "bool", nb)]
            elif t.startswith("TP"): stack += [("expr", "fmt", nb)] * ar[int(t[2:])]
    return out
for v in ["A_ifelse", "A_ternary"]:
    m = parse_a(R[v]["src"]); hdr, toks = encode_b(m)
    ls = legal_sets(hdr, toks, ["i32"])
    assert all(ok for _, _, ok in ls), ls
    bits = sum(math.log2(n) for _, n, _ in ls)
    print(f"\n{v}: {len(toks)} opcodes; legal choices per position:", " ".join(f"{t}:{n}" for t, n, _ in ls))
    print(f"   sum log2(legal) = {bits:.1f} bits vs unconstrained {len(toks) * math.log2(len(VOCAB)):.1f} bits ({len(VOCAB)}-token vocabulary); "
          f"median legal set {sorted(n for _, n, _ in ls)[len(ls)//2]}")
