"""H3 payload accounting: exact serialized payloads for 20 invocations of Arm B's two validated handles.
Measures text artifacts only (tiktoken o200k_base and cl100k_base). It does NOT measure model inference tokens.
Payload files are written to h3_payloads/ so anyone can re-tokenize them."""
import json, os, re
import tiktoken
O, C = tiktoken.get_encoding("o200k_base"), tiktoken.get_encoding("cl100k_base")
cards = open("fixtures/capability_cards.md").read()
api = open("fixtures/baseline_api.md").read()
card_ctrl = next(l for l in cards.splitlines() if l.startswith("- `cap:controller.logs@1`"))
card_roll = next(l for l in cards.splitlines() if l.startswith("- `cap:activity.rollup@1`"))
api_ctrl = next(l for l in api.splitlines() if l.startswith("- `controller_logs("))
CONTRACT = {"ctrl": card_ctrl + "\n" + api_ctrl + "\n", "roll": card_roll + "\n" + open("fixtures/activity_contract.md").read()}
HANDLE = {"ctrl": "cap:controller.logs@1", "roll": "cap:activity.rollup@1"}
def call_full(h, k):
    return (f'bind("{HANDLE[h]}", allowed_effects=())(runs={k})' if h == "ctrl"
            else f'bind("{HANDLE[h]}", allowed_effects=())(events=batch_{k}, window_seconds=600, min_severity=1)') + "\n"
def call_alias(h, k): return (f"c({k})" if h == "ctrl" else f"r(batch_{k}, 600, 1)") + "\n"
ALIAS = 'c = bind("cap:controller.logs@1", allowed_effects=())\nr = bind("cap:activity.rollup@1", allowed_effects=())\n'
VERDICT = ("c = cap:controller.logs@1 fit(T1) valid, policy pure, digest sha256:<artifact>\n"
           "r = cap:activity.rollup@1 fit(T2) valid, policy pure, digest sha256:<artifact>\n")
calls = [("ctrl" if k % 2 else "roll", k) for k in range(1, 21)]
msgs = {
 "1_repeat_contract_every_call": [CONTRACT[h] + call_full(h, k) for h, k in calls],
 "2_contract_once_then_alias": [CONTRACT["ctrl"] + CONTRACT["roll"] + ALIAS + call_alias(*calls[0])] + [call_alias(h, k) for h, k in calls[1:]],
 "2b_contract_once_full_handles": [CONTRACT["ctrl"] + CONTRACT["roll"] + call_full(*calls[0])] + [call_full(h, k) for h, k in calls[1:]],
 "3_verdict_lines_then_alias (illustrative)": [VERDICT + ALIAS + call_alias(*calls[0])] + [call_alias(h, k) for h, k in calls[1:]],
}
os.makedirs("h3_payloads", exist_ok=True); res = {}
for name, ms in msgs.items():
    text = "".join(ms); fn = "h3_payloads/" + re.sub(r"[^a-z0-9_]+", "_", name.lower()).strip("_") + ".txt"
    open(fn, "w").write(text)
    o_turns = [len(O.encode(m)) for m in ms]
    cum = sum(sum(o_turns[:t + 1]) for t in range(len(o_turns)))   # if every turn re-sent the whole history
    res[name] = {"file": fn, "bytes": len(text.encode()), "o200k": len(O.encode(text)), "cl100k": len(C.encode(text)),
                 "cumulative_o200k_if_history_resent": cum}
    print(f"{name:44s} bytes {res[name]['bytes']:6d}  o200k {res[name]['o200k']:6d}  cl100k {res[name]['cl100k']:6d}  cumulative(history resent) {cum:7d}")
artifacts = {"submission.py (Arm A)": "submission.py", "submission_registry.py (Arm B)": "submission_registry.py",
             "controller_submission.py (Arm C)": "controller_submission.py", "controller_submission.sym (Arm D)": "controller_submission.sym",
             "contract ctrl (card + API bullet)": None, "contract rollup (card + activity_contract.md)": None}
print()
for label, fn in artifacts.items():
    text = open(fn).read() if fn else (CONTRACT["ctrl"] if "ctrl" in label else CONTRACT["roll"])
    res[label] = {"bytes": len(text.encode()), "o200k": len(O.encode(text)), "cl100k": len(C.encode(text))}
    print(f"{label:44s} bytes {res[label]['bytes']:6d}  o200k {res[label]['o200k']:6d}  cl100k {res[label]['cl100k']:6d}")
core_py = "\n".join(l for l in open("controller_submission.py").read().splitlines() if l.strip() and not l.strip().startswith(('"""', "Contamination", "#")) and "Contamination" not in l)
res["Arm C function only (no docstring)"] = {"bytes": len(core_py.encode()), "o200k": len(O.encode(core_py)), "cl100k": len(C.encode(core_py))}
print(f"{'Arm C function only (no docstring)':44s} bytes {res['Arm C function only (no docstring)']['bytes']:6d}  o200k {res['Arm C function only (no docstring)']['o200k']:6d}  cl100k {res['Arm C function only (no docstring)']['cl100k']:6d}")
sym = open("controller_submission.sym").read()
print("\nsymbolic program token pieces (o200k):", [O.decode([t]) for t in O.encode(sym)])
json.dump(res, open("token_results_r7.json", "w"), indent=1)
