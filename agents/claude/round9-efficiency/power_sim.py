"""SIMULATION under stated assumptions (not measurement): false-positive rate and power of the primary metric
(B/A ratio of amortized cost per successful task) for the protocol's pilot (12 tasks x 3 trials) and expanded
(30 x 10) designs. Cost per trial ~ task_mean * exp(N(0, sigma)); task means vary log-normally (sd 0.5); success ~ Bernoulli(0.8).
sigma 1.0 roughly reflects the heavy run-to-run spread reported by Bai et al. (up to 30x on the same task); sigma 0.5 is milder.
Two analyses: naive bootstrap over tasks only vs two-level bootstrap (tasks, then trials within task)."""
import numpy as np
rng = np.random.default_rng(2026)
def study(K, R, sigma, effect):
    m = np.exp(rng.normal(0, 0.5, K))[:, None]
    ca = m * np.exp(rng.normal(0, sigma, (K, R))); cb = m * np.exp(rng.normal(0, sigma, (K, R))) * (1 - effect)
    sa = rng.random((K, R)) < 0.8; sb = rng.random((K, R)) < 0.8
    return ca, sa, cb, sb
def ci_excludes_zero(ca, sa, cb, sb, two_level, B=400):
    K, R = ca.shape
    ti = rng.integers(0, K, (B, K))                                   # resample tasks
    if two_level:
        ja = rng.integers(0, R, (B, K, R)); jb = rng.integers(0, R, (B, K, R))   # resample trials within each task
        CA = ca[ti[..., None], ja]; SA = sa[ti[..., None], ja]; CB = cb[ti[..., None], jb]; SB = sb[ti[..., None], jb]
    else:
        CA, SA, CB, SB = ca[ti], sa[ti], cb[ti], sb[ti]
    cpa = CA.sum((1, 2)) / np.maximum(SA.sum((1, 2)), 1); cpb = CB.sum((1, 2)) / np.maximum(SB.sum((1, 2)), 1)
    lo, hi = np.percentile(cpb / cpa - 1, [2.5, 97.5])
    return hi < 0 or lo > 0, hi < 0
N = 300
print(f"{'design':10s} {'sigma':>5s} {'analysis':12s} {'false-positive rate (no true effect)':>38s} {'power to detect a true 15% saving':>36s}")
for K, R in [(12, 3), (30, 10)]:
    for sigma in (0.5, 1.0):
        for two in (False, True):
            fp = np.mean([ci_excludes_zero(*study(K, R, sigma, 0.0), two)[0] for _ in range(N)])
            pw = np.mean([ci_excludes_zero(*study(K, R, sigma, 0.15), two)[1] for _ in range(N)])
            print(f"{K:3d}x{R:<6d} {sigma:5.1f} {'two-level' if two else 'tasks-only':12s} {fp:38.2f} {pw:36.2f}")
