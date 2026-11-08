"""Extension of power_sim.py: larger designs, two-level bootstrap only, sigma = 1.0 (heavy run-to-run variance)."""
import numpy as np
exec(open("power_sim.py").read().split("N = 300")[0])
N = 150
for K, R in [(60, 10), (100, 10), (200, 5)]:
    for eff in (0.15, 0.30):
        pw = np.mean([ci_excludes_zero(*study(K, R, 1.0, eff), True)[1] for _ in range(N)])
        print(f"{K:3d} tasks x {R:2d} trials, sigma 1.0, two-level: power to detect a true {int(eff*100)}% saving = {pw:.2f}")
