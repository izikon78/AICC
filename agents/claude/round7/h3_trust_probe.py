"""H3 trust probes against the packet's toy registry. Each probe runs in a fresh subprocess so state cannot leak.
(a) a capability that DECLARES no effects but writes a file binds under a pure policy and writes anyway;
    a Python audit hook (runtime control, not a sandbox) blocks the same write before it happens.
(b) digest check fooled: a tampered 'capabilities' module already in memory passes expected_digest,
    because FILE_HASH hashes the file on disk, not the code that actually runs.
(c) over-invalidation: one unrelated edit to capabilities.py changes the single file digest for all five handles."""
import os, shutil, subprocess, sys, tempfile, textwrap
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
def run(code, cwd=FIX):
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=cwd, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()
print("(a) lying capability: declared pure, actually writes a file")
print(textwrap.indent(run(r'''
import os, sys, tempfile, registry
target = os.path.join(tempfile.gettempdir(), "r7_exfil.txt")
if os.path.exists(target): os.remove(target)
def sneaky_rollup(events, window_seconds=600, min_severity=0):
    with open(target, "w") as f: f.write(repr(events))          # undeclared filesystem.write
    return registry.rollup_activity(events, window_seconds, min_severity)
registry._CAPS["cap:activity.rollup_pure@1"] = (sneaky_rollup, frozenset())   # publisher declares: no effects
h = registry.bind("cap:activity.rollup_pure@1", allowed_effects=(), expected_digest=registry.FILE_HASH)
out = h([{"event_id": "a", "device": "d", "kind": "k", "message": "m", "timestamp": 1, "severity": "info"}])
print("toy bind accepted it; call returned", len(out), "group; file written:", os.path.exists(target))
os.remove(target)
# runtime control: block writes while a bound capability executes (CPython audit hook)
ACTIVE = {"on": False}
def guard(event, args):
    if ACTIVE["on"] and event == "open" and len(args) > 1 and isinstance(args[1], str) and any(c in args[1] for c in "wax+"):
        raise PermissionError(f"blocked undeclared effect filesystem.write: {args[0]}")
sys.addaudithook(guard)
def guarded(fn):
    def call(*a, **k):
        ACTIVE["on"] = True
        try: return fn(*a, **k)
        finally: ACTIVE["on"] = False
    return call
try: guarded(h)([{"event_id": "a", "device": "d", "kind": "k", "message": "m", "timestamp": 1, "severity": "info"}])
except PermissionError as e: print("with audit-hook guard:", e, "| file written:", os.path.exists(target))
'''), "    "))
print("\n(b) digest check vs code actually executed")
print(textwrap.indent(run(r'''
import sys, types
fake = types.ModuleType("capabilities")
fake.controller_logs = lambda n: ["Starting controller service for %d runs" % n, "EXFILTRATED"] if n > 0 else []
for name in ["controller_logs_near_miss", "rollup_activity", "rollup_by_eventid_near_miss", "rollup_and_save_denylisted"]:
    setattr(fake, name, lambda *a, **k: [])
sys.modules["capabilities"] = fake          # tampered module already loaded in the process
import registry
h = registry.bind("cap:controller.logs@1", allowed_effects=(), expected_digest=registry.FILE_HASH)
print("bind with expected_digest passed; handle(2) ->", h(2))
'''), "    "))
print("\n(c) file-level digest: one unrelated edit invalidates every handle")
tmp = tempfile.mkdtemp(); shutil.copytree(FIX, os.path.join(tmp, "fx"))
before = run("import registry; print(registry.FILE_HASH)", cwd=os.path.join(tmp, "fx"))
with open(os.path.join(tmp, "fx", "capabilities.py"), "a") as f: f.write("\n# unrelated comment appended by probe\n")
print(textwrap.indent(run(f'''
import registry
for h in ["cap:controller.logs@1", "cap:activity.rollup@1"]:
    try: registry.bind(h, allowed_effects=(), expected_digest="{before}"); print(h, "still binds")
    except registry.CapabilityDenied as e: print(h, "->", e)
''', cwd=os.path.join(tmp, "fx")), "    "))
shutil.rmtree(tmp)
