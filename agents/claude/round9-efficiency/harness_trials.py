"""10 randomized-order trials per executable arm. Each trial is a fresh Python process (trial_wrapper.py). No LLM involved:
these time the HARNESS executing artefacts authored earlier in this conversation, not agent development time."""
import json, random, subprocess, sys, time, datetime
R8 = "/home/claude/r8/AI_Think_Tank_Round8_Packet"; R7 = "/home/claude/r7/AI_Think_Tank_Round7_Test_Packet"
ARMS = {
 ("A", "R8-composition-T1..T8"): (R8, "benchmark.verify_submission", ["--submission", "submission_A.py"]),
 ("B", "R8-composition-T1..T8"): (R8, "benchmark.verify_submission", ["--submission", "submission_B.py"]),
 ("B-security", "R8-private-scope-checks"): (R8, "benchmark.verify_submission", ["--security"]),
 ("A", "R7-T1-controller"): (R7, "fixtures/test_tasks.py", ["--python-controller", "controller_submission.py"]),
 ("C", "R7-T1-controller"): (R7, "fixtures/test_tasks.py", ["--symbolic", "controller_submission.sym"]),
}
order = [k for k in ARMS for _ in range(10)]; random.Random(9).shuffle(order)
rows, counters = [], {k: 0 for k in ARMS}
for k in order:
    cwd, mod, args = ARMS[k]; counters[k] += 1
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    r = subprocess.run([sys.executable, "/home/claude/r9/trial_wrapper.py", cwd, mod] + args, capture_output=True, text=True)
    m = json.loads(r.stderr.strip().splitlines()[-1])
    rows.append({"arm": k[0], "task": k[1], "trial": counters[k], "ts": ts, **m})
json.dump(rows, open("harness_trials.json", "w"), indent=1)
import statistics as st
for k in ARMS:
    rs = [r for r in rows if (r["arm"], r["task"]) == k]
    w = sorted(r["wall_ms"] for r in rs); c = sorted(r["cpu_ms"] for r in rs); m = [r["peak_rss_mb"] for r in rs]
    print(f"  {k[0]:11s} {k[1]:26s} pass {rs[0]['passed']}/{rs[0]['total']} x{len(rs)}  wall p50 {st.median(w):7.1f} ms p95 {w[-1]:7.1f}  cpu p50 {st.median(c):7.1f} ms  peak RSS p50 {st.median(m):5.1f} MB")
