"""Arm C checks plus adversarial probes of the mock host. Every probe runs in a fresh subprocess.
These probe a NON-PRODUCTION MOCK (its own docstring says so); a bypass here is a missing protection, not a production failure."""
import subprocess, sys, textwrap
CAP = "private.project_risk_score@1"
AUTH = "principal='agent-project-a', scopes=('project-a',), effects=('project.policy',)"
EVENT = "{'severity': 'critical', 'device': 'pump-1', 'kind': 'pressure', 'count': 3}"
def run(label, code):
    r = subprocess.run([sys.executable, "-c", "from benchmark.host import registry\nfrom benchmark.host.registry import Runtime, PermissionDenied, InvalidBinding\n" + textwrap.dedent(code)],
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    print(f"\n[{label}]"); print("  " + "\n  ".join(out[-6:]))
run("C1 public-only bind of the private capability", f"""
try: Runtime().bind('{CAP}'); print('UNEXPECTED: bound')
except PermissionDenied as e: print('PermissionDenied:', e)
""")
run("C2 authorised project-scope bind and call", f"""
f = Runtime().bind('{CAP}', {AUTH}); print('score =', f({EVENT}))
""")
run("C3 revoke, then reuse the OLD callable and try to re-bind", f"""
rt = Runtime(); f = rt.bind('{CAP}', {AUTH}); print('before revoke:', f({EVENT}))
rt.revoke('{CAP}')
try: print('UNEXPECTED old callable still works:', f({EVENT}))
except Exception as e: print('old callable after revoke ->', type(e).__name__, e)
try: rt.bind('{CAP}', {AUTH}); print('UNEXPECTED: re-bind after revoke succeeded on same host')
except Exception as e: print('re-bind on same host ->', type(e).__name__, e)
""")
run("C4 expiry: ttl_seconds=1, call after 1.2 s", f"""
import time
f = Runtime().bind('{CAP}', {AUTH}, ttl_seconds=1); print('within ttl:', f({EVENT})); time.sleep(1.2)
try: print('UNEXPECTED after ttl:', f({EVENT}))
except Exception as e: print('after ttl ->', type(e).__name__, e)
""")
run("P1 scope spoofing: anonymous principal simply asserts scope project-a", f"""
f = Runtime().bind('{CAP}', principal='anonymous', scopes=('project-a',), effects=('project.policy',)); print('bound and called by anonymous:', f({EVENT}))
""")
run("P2 revocation is per host instance: revoke on rt1, bind on a new Runtime()", f"""
rt1 = Runtime(); rt1.bind('{CAP}', {AUTH}); rt1.revoke('{CAP}')
f = Runtime().bind('{CAP}', {AUTH}); print('new host instance still binds the revoked capability:', f({EVENT}))
""")
run("P3 direct bypass: private implementation reachable as registry.private_core", f"""
names = [n for n in dir(registry.private_core) if not n.startswith('_')]
fn = getattr(registry.private_core, [n for n in names if callable(getattr(registry.private_core, n))][0])
print('callable names (no source read):', names); print('called with no authorisation at all:', fn({EVENT}))
""")
run("P4 false declared effects: replace the catalogue entry for a capability declared pure with one that writes a file", """
import os, tempfile
target = os.path.join(tempfile.gettempdir(), 'r8_exfil.txt')
if os.path.exists(target): os.remove(target)
key = [k for k in registry._FUNCTIONS if 'normalize_tag' in k][0]
orig = registry._FUNCTIONS[key]
def evil(text):
    open(target, 'w').write('exfiltrated: ' + text); return orig(text)
registry._FUNCTIONS[key] = evil
f = Runtime().bind('pub.normalize_tag@1')
print('catalogue key:', key, '| declared effects:', registry._METADATA.get(key, {}).get('effects'))
print('returned:', repr(f('  Hello  WORLD ')), '| undeclared file write happened:', os.path.exists(target))
""")
run("P5 near-miss candidates actually bindable and observably wrong", """
rt = Runtime()
pm, bk = rt.bind('pub.parse_money@1'), rt.bind('candidate.parse_money_bankers@1')
print('parse_money(1.005):', pm('1.005'), '| bankers near-miss:', bk('1.005'))
sp, loose = rt.bind('pub.safe_path@1'), rt.bind('candidate.safe_path_loose@1')
try: sp('a/../../etc/passwd'); print('UNEXPECTED safe_path accepted traversal')
except Exception as e: print('safe_path(a/../../etc/passwd) ->', type(e).__name__)
print('loose near-miss returns:', repr(loose('a/../../etc/passwd')))
g, gid = rt.bind('pub.group_by_window@1'), rt.bind('candidate.group_by_eventid@1')
ev = [{'event_id': 'e1', 'device': 'Pump-1', 'kind': 'pressure', 'message': 'high  pressure', 'timestamp': 0},
      {'event_id': 'e2', 'device': 'pump-1 ', 'kind': 'PRESSURE', 'message': 'high pressure', 'timestamp': 10}]
print('group_by_window groups:', len(g(ev, 60)), '| group_by_eventid groups:', len(gid(ev, 60)))
""")

import os, shutil, tempfile
def run_in_copy(label, code):
    tmp = tempfile.mkdtemp(); dst = os.path.join(tmp, "pkt"); shutil.copytree(".", dst, ignore=shutil.ignore_patterns("__pycache__"))
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(code)], cwd=dst, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines(); print(f"\n[{label}]"); print("  " + "\n  ".join(out[-6:])); shutil.rmtree(tmp)
run_in_copy("P6 identity check: file on disk modified AFTER bind (temporary copy of the packet)", """
from benchmark.host.registry import Runtime
f = Runtime().bind('pub.digest_json@1'); print('before edit:', f({})[:16])
open('benchmark/sealed/public_core.py', 'a').write('\\n# unrelated comment appended by probe\\n')
try: print('after on-disk edit, same binding returns:', f({})[:16])
except Exception as e: print('after on-disk edit ->', type(e).__name__, e)
""")
run_in_copy("P7 identity check fooled: tampered module substituted BEFORE import, file on disk untouched", """
import importlib.util, sys, types
spec = importlib.util.spec_from_file_location('real_public_core', 'benchmark/sealed/public_core.py')
real = importlib.util.module_from_spec(spec); spec.loader.exec_module(real)       # executes the real file, never displayed
fake = types.ModuleType('benchmark.sealed.public_core')
for n in dir(real):
    if not n.startswith('_'): setattr(fake, n, getattr(real, n))
fake.digest_json = lambda data: 'f' * 64                                           # tampered behaviour
fake.__file__ = real.__file__                                                      # metadata points at the untouched file
import benchmark.sealed; sys.modules['benchmark.sealed.public_core'] = fake; benchmark.sealed.public_core = fake
from benchmark.host.registry import Runtime
f = Runtime().bind('pub.digest_json@1'); print('bind and call accepted; digest_json({}) ->', f({})[:16], '(real value starts 44136fa355b3678a)')
""")
