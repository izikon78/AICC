"""MODEL, not measurement. Upper bound on what removing D context tokens from every turn could save, in base-input-token
equivalents, with and without prompt caching. Multipliers from provider documentation as summarised in the report
(Anthropic: 5-min cache write 1.25x, cache read 0.1x; some newer models read at 0.05x). Output/reasoning tokens unaffected."""
D = 1682            # measured: shared contract + task text in the Round 8 pilot (tiktoken o200k)
print(f"{'turns':>6} {'no caching':>12} {'cached r=0.10':>14} {'cached r=0.05':>14}   (savings if those {D} tokens vanished from every turn)")
for T in (5, 20, 50, 100):
    nocache = D * T
    c10 = D * (1.25 + 0.10 * (T - 1)); c05 = D * (1.25 + 0.05 * (T - 1))
    print(f"{T:6d} {nocache:12,.0f} {c10:14,.0f} {c05:14,.0f}")
