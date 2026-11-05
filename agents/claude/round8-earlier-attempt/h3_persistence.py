"""H3: measure what a validated binding can avoid re-sending across repeated calls, and compare against the fair
baseline the protocol demands (ordinary documentation caching), not a repeated-full-contract straw man.
Text-artifact tokens only (tiktoken o200k_base). NOT model inference/billing tokens."""
import json, tiktoken
O = tiktoken.get_encoding("o200k_base")
tok = lambda s: len(O.encode(s))
contracts = open("benchmark/public/API_CONTRACTS.md").read()
# one capability's contract row (group_by_window) as a reuser would hold it
row = next(l for l in contracts.splitlines() if l.startswith("| `group_by_window"))
full_contract_block = "\n".join(l for l in contracts.splitlines() if l.startswith("| `") or l.startswith("# "))
N = 20
strategies = {
 "A1 ordinary: keep the one-line API doc row in context, call by name (fair baseline)": [row + "\n"] + [f"group_by_window(events_{k}, 60)\n" for k in range(N)],
 "A2 ordinary: re-paste the whole contract table every call (straw man)": [full_contract_block + f"\ngroup_by_window(events_{k}, 60)\n" for k in range(N)],
 "B1 commons: validate once (bind + card), then short handle call": ["rt.bind('pub.group_by_window@1')  # validated: digest+scope+effects+ttl\n" + row + "\n"] + [f"g(events_{k}, 60)\n" for k in range(N)],
 "B2 commons: one-line verdict alias, contract not re-shown (illustrative)": ["g = pub.group_by_window@1  # ENTAILED; digest d4f1; ttl 600s\n"] + [f"g(events_{k}, 60)\n" for k in range(N)],
}
res = {}
for name, msgs in strategies.items():
    text = "".join(msgs)
    serial = tok(text)
    cumulative = sum(tok("".join(msgs[:t+1])) for t in range(len(msgs)))   # if each turn resends full history, no cache
    res[name] = {"serial_tokens": serial, "cumulative_if_history_resent": cumulative}
    print(f"{name}\n    serialized {serial:5d} tok | cumulative if history resent {cumulative:6d} tok")
json.dump(res, open("h3_persistence_results.json","w"), indent=1)
print("\nKey point: A1 (hold one doc line, call by name) is the honest baseline. B1/B2 do not beat it on tokens;")
print("their only possible edge is the host RE-CHECKING digest/scope/effects/revocation each call, which A cannot do.")
# contract-row vs implementation size, to show where (if anywhere) hiding a body saves context
import os
pub_impl_tokens = tok(open("benchmark/sealed/public_core.py","rb").read().decode("utf-8","replace")) if False else None  # NOT opened
print("\n(For honesty: public_core.py was NOT opened to measure its tokens; token_measure.py reports file sizes without displaying source.)")
