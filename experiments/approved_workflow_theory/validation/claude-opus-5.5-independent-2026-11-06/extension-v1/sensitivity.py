"""EXTENSION v1 (separately versioned; NOT the frozen accounting). Sensitivity of the published conditional result
to three of its assumptions, computed with the sealed independent counter's functions on the same trace inputs."""
import json, sys
sys.path.insert(0, "/home/claude/awt/claude-independent")
import counter as K
trace = json.load(open("/home/claude/awt/AICC/experiments/approved_workflow_theory/trace-inputs.json")); cfg = trace["config"]
count = K.make_counter("/home/claude/awt/claude-independent/tokenizer.json")
def totals(ledger_fn):
    t = {}
    for e in trace["episodes"]:
        for r in ledger_fn(e):
            s = t.setdefault(e["schedule"], {"in": 0, "out": 0, "common": 0})
            s["in"] += r["input_positions"]; s["out"] += r["output_positions"]; s["common"] += r["common_input_text_tokens"]
    return t
alias = totals(lambda e: K.ledger(e, "python_aliases", cfg, count, K.Units(cfg["static_symbols"], cfg["catalog_schema"])))
ideal = totals(lambda e: K.ledger(e, "ideal_ain", cfg, count, K.Units(cfg["static_symbols"], cfg["catalog_schema"])))
nostatic = totals(lambda e: K.ledger(e, "ideal_ain", cfg, count, K.Units([], cfg["catalog_schema"])))
compact = lambda v: json.dumps(v, separators=(",", ":"))
def alias_compact_data(e):  # memory and host observations are data blobs: render as compact JSON instead of repr
    rows = K.ledger(e, "python_aliases", cfg, count, None); M = count(compact(e["incoming_memory"])) if e["incoming_memory"] else 0
    H, out = 0, []
    for i, r in enumerate(rows):
        O = count(compact(e["host_observations"][i])); r = dict(r); r["memory_input_units"] = M; r["reprocessed_history_units"] = H
        r["input_positions"] = r["common_input_text_tokens"] + r["artifact_input_units"] + M + H + r["shared_framing_positions"]
        H += r["output_positions"] + O; out.append(r)
    return out
compactdata = totals(alias_compact_data)
red = lambda a, b: 100 * (1 - (b["in"] + b["out"]) / (a["in"] + a["out"]))
print("EXTENSION v1: sensitivity analysis (not the frozen accounting)")
for s in ("resident", "inspect"):
    a, i = alias[s], ideal[s]
    noncommon = i["in"] + i["out"] - i["common"]
    k = (a["in"] + a["out"] - i["common"]) / noncommon
    print(f"\n[{s}] frozen: alias Python {a['in'] + a['out']:,} vs ideal {i['in'] + i['out']:,} -> {red(a, i):.2f}% fewer positions")
    print(f"  S1 break-even: ideal advantage vanishes if one ideal unit costs more than {k:.3f}x one text token")
    print(f"  S2 alias Python with compact-JSON memory/observations: {compactdata[s]['in'] + compactdata[s]['out']:,} -> ideal advantage {red(compactdata[s], i):.2f}%")
    print(f"  S3 ideal without the 63 workload-fitted static symbols: {nostatic[s]['in'] + nostatic[s]['out']:,} -> advantage vs alias Python {red(a, nostatic[s]):.2f}%")
json.dump({"alias": alias, "ideal": ideal, "ideal_no_static_symbols": nostatic, "alias_compact_data": compactdata}, open("extension-v1/sensitivity.json", "w"), indent=1)
