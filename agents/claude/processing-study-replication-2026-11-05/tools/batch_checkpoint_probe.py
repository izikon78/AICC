"""Post-replication probe (Claude): what revocation, expiry and cancellation observe when authority is checked per call
versus only at batch entry. Deterministic: a fake clock advances 1 ms per element. Uses the frozen Runtime unchanged."""
import json, sys
sys.path.insert(0, "/home/claude/ps/AICC/experiments/processing_study")
from aicc_processing.runtime import Runtime, CapabilityError
N, K = 1000, int(sys.argv[1]) if len(sys.argv) > 1 else 300
STATE = {"count": 0, "clock": 0.0, "at": None, "action": None, "cancel": False}
def clock(): return STATE["clock"]
def tick():
    STATE["count"] += 1; STATE["clock"] += 0.001
    if STATE["at"] == STATE["count"] and STATE["action"]: STATE["action"]()
def step(value):
    tick(); return (value * 17 + 3) % 65521
def batch_steps(count):
    total = 0
    for v in range(count):
        tick(); total += (v * 17 + 3) % 65521
    return total
def chunk_steps(start, size):
    total = 0
    for v in range(start, start + size):
        tick(); total += (v * 17 + 3) % 65521
    return total
def host():
    STATE.update(count=0, clock=0.0, at=None, action=None, cancel=False)
    h = Runtime(environment={"probe": "batch-checkpoints"}, clock=clock)
    for name, fn in (("step", step), ("batch", batch_steps), ("chunk", chunk_steps)): h.register(name, fn)
    return h
def run(path, event, chunk=100):
    h = host(); ttl = 0.3 if event == "expiry" else 600
    alias = h.bind({"split": "step", "batch": "batch", "chunked": "chunk"}[path], ttl_seconds=ttl)
    if event == "revocation": STATE["at"], STATE["action"] = K, (lambda: h.revoke({"split": "step", "batch": "batch", "chunked": "chunk"}[path]))
    if event == "cancellation": STATE["at"], STATE["action"] = K, (lambda: STATE.update(cancel=True))
    error = None
    try:
        if path == "split":
            for i in range(N):
                if STATE["cancel"]: break                      # caller-level checkpoint between calls
                alias(i)
        elif path == "batch":
            alias(N)                                            # one entry check, no checkpoint inside
        else:
            for s in range(0, N, chunk):
                if STATE["cancel"]: break
                alias(s, min(chunk, N - s))
    except CapabilityError as e: error = type(e).__name__
    after = max(0, STATE["count"] - K) if event in ("revocation", "cancellation") else max(0, STATE["count"] - int(0.3 / 0.001))
    return {"path": path, "event": event, "elements_processed": STATE["count"], "elements_after_event": after, "stopped_by": error or ("caller checkpoint" if STATE["cancel"] and STATE["count"] < N else None)}
rows = [run(p, e) for e in ("revocation", "expiry", "cancellation") for p in ("split", "chunked", "batch")]
print(f"N = {N} elements, event at element {K} (expiry: TTL 0.3 s with 1 ms per element); chunked path uses 100-element chunks")
print(f"{'event':13s} {'path':8s} {'processed':>9s} {'after event':>11s}  stopped by")
for r in rows: print(f"{r['event']:13s} {r['path']:8s} {r['elements_processed']:9d} {r['elements_after_event']:11d}  {r['stopped_by']}")
json.dump(rows, open(f"/home/claude/ps/agent_logs/batch_checkpoint_probe_K{K}.json", "w"), indent=1)
