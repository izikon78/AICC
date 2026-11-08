"""Runtime-overhead measurements (no LLM involved). Python 3.12, single process unless stated.
E1 per-call cost of an AICC-style validated binding (Round 8 mock host) vs direct import vs an ordinary wrapper.
E2 cost of process isolation (spawn per call; persistent worker over pipes) vs in-process call.
E3 interpretive overhead of the toy symbolic languages vs native Python.
Method: warm-up, then REPS repetitions of N calls; per-call time = repetition time / N; report median and p95 over repetitions."""
import json, os, statistics, subprocess, sys, time
R8 = "/home/claude/r8/AI_Think_Tank_Round8_Packet"; R7 = "/home/claude/r7/AI_Think_Tank_Round7_Test_Packet/fixtures"; V2 = "/home/claude/sym"
sys.path[:0] = [R8, R7, V2]
REPS = 15
def bench(fn, n, reps=REPS):
    for _ in range(max(1, n // 10)): fn()
    per = []
    for _ in range(reps):
        t0 = time.perf_counter_ns()
        for _ in range(n): fn()
        per.append((time.perf_counter_ns() - t0) / n)
    per.sort()
    return {"median_ns": statistics.median(per), "p95_ns": per[min(len(per) - 1, int(0.95 * len(per)))], "n_per_rep": n, "reps": reps}
results = {}
def record(group, label, r):
    results.setdefault(group, {})[label] = r
    print(f"  {label:58s} median {r['median_ns']/1000:10.2f} us   p95 {r['p95_ns']/1000:10.2f} us")
# ---------------- E1: binding overhead ----------------
print("E1 per-call overhead of validated bindings (Round 8 mock host)")
from benchmark.public import baseline_api as A
from benchmark.host.registry import Runtime
rt = Runtime()
events = [{"device": f"pump-{i % 5}", "kind": "pressure", "message": "high  pressure", "timestamp": i * 7} for i in range(50)]
cases = {"normalize_tag": (("  Hello  WORLD  ",), 20000), "digest_json": (({"a": [1, 2, 3], "b": "x"},), 20000),
         "group_by_window": ((events, 60), 2000)}
import functools
def ordinary_wrapper(fn):                       # ordinary policy wrapper: revocation set + expiry, no per-call file hash
    revoked, expiry = set(), time.monotonic() + 600
    @functools.wraps(fn)
    def call(*a):
        if "x" in revoked or time.monotonic() > expiry: raise PermissionError
        return fn(*a)
    return call
for name, (args, n) in cases.items():
    direct = getattr(A, name); bound = rt.bind(f"pub.{name}@1"); wrapped = ordinary_wrapper(direct)
    record("E1", f"{name}: direct import", bench(lambda: direct(*args), n))
    record("E1", f"{name}: ordinary policy wrapper", bench(lambda: wrapped(*args), n))
    record("E1", f"{name}: AICC mock binding (per-call revalidation)", bench(lambda: bound(*args), n))
record("E1", "bind() itself (one-time, per capability)", bench(lambda: Runtime().bind("pub.normalize_tag@1"), 2000))
# ---------------- E2: isolation boundary ----------------
print("E2 process isolation cost for one normalize_tag call")
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iso_worker.py")
open(WORKER, "w").write(f"import sys, json; sys.path.insert(0, {R8!r})\nfrom benchmark.public.baseline_api import normalize_tag\n"
                        "for line in sys.stdin:\n    print(json.dumps(normalize_tag(json.loads(line))), flush=True)\n")
proc = subprocess.Popen([sys.executable, WORKER], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def via_worker():
    proc.stdin.write(json.dumps("  Hello  WORLD  ") + "\n"); proc.stdin.flush(); return json.loads(proc.stdout.readline())
assert via_worker() == "hello world"
record("E2", "in-process direct call", bench(lambda: A.normalize_tag("  Hello  WORLD  "), 20000))
record("E2", "persistent isolated worker process (JSON over pipes)", bench(via_worker, 2000))
spawn = lambda: subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {R8!r}); from benchmark.public.baseline_api import normalize_tag; print(normalize_tag('  Hello  WORLD  '))"], capture_output=True, text=True, check=True)
record("E2", "spawn a fresh Python process per call", bench(spawn, 3, reps=10))
proc.stdin.close(); proc.wait()
# ---------------- E3: symbolic-language execution ----------------
print("E3 executing the Round 7 controller task (n runs) in each representation")
import symbolic_runtime as S
import lang as L
SYM = "@1(n:I){R(n,i){?(i=0,!7(T0,n),!7(T1,i+1,n))}}"
A_SRC = 'fn main(n:i32){for i<n{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {n}"}}}'
modA = L.parse_a(A_SRC); L.check(modA); hdr, toksB = L.encode_b(modA, inline_strings=True)
def native(n): return [f"Starting controller service for {n} runs"] + [f"Restarting controller service for run {i + 1} of {n}" for i in range(1, n)] if n > 0 else []
ns_proj = {}; exec(L.proj_py(modA), {"_chk32": lambda x: x}, ns_proj)
class _O:
    class m_log:
        out = []
        @staticmethod
        def info(s): pass
for n in (3, 1000):
    reps_n = 20000 if n == 3 else 200
    assert S.execute(SYM, n) == native(n) and [t[1] for t in L.run(modA, "main", [n])] == native(n)
    record("E3", f"n={n}: native Python", bench(lambda: native(n), reps_n))
    record("E3", f"n={n}: Language A projected to Python (compiled once)", bench(lambda: ns_proj["main"](_O, n), reps_n))
    record("E3", f"n={n}: Round 7 symbolic runtime (parse + interpret each call)", bench(lambda: S.execute(SYM, n), reps_n // 4))
    record("E3", f"n={n}: Language A AST interpreter (parsed once)", bench(lambda: L.run(modA, "main", [n]), reps_n // 4))
    record("E3", f"n={n}: Language B decode + interpret each call", bench(lambda: L.run(L.decode_b(hdr, toksB), "main", [n]), reps_n // 4))
json.dump(results, open("runtime_results.json", "w"), indent=1)
