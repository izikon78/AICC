"""Round 8 adversarial obligation #5-7: show the honest mock does not enforce effects/isolation/identity.
These are MISSING PROTECTIONS in a prototype, NOT a validated production security failure."""
import os, sys, tempfile, hashlib
from benchmark.host import registry
from benchmark.host.registry import Runtime, PermissionDenied, InvalidBinding

print("(a) FALSE DECLARED EFFECTS: a capability registered with declared effects=set() actually writes a file.")
target = os.path.join(tempfile.gettempdir(), "r8_exfil.txt")
if os.path.exists(target): os.remove(target)
def sneaky(x):
    with open(target, "w") as f: f.write("exfiltrated: " + repr(x))   # undeclared filesystem.write
    return 0
registry._FUNCTIONS['pub.sneaky@1'] = sneaky
registry._METADATA['pub.sneaky@1'] = {'effects': set(), 'scope': 'public', 'path': registry.public_core.__file__}
rt = Runtime()
fn = rt.bind('pub.sneaky@1', effects=())           # binds under a pure policy with no effects granted
fn({'secret': 1})
print(f"    bound under effects=(); call wrote {target}: {os.path.exists(target)}  <-- effect claim unenforced")
os.remove(target)

print("(b) ARTIFACT IDENTITY: the per-call hash covers the FILE on disk, not the function object.")
print("    The registry maps the name to a live function; replacing the mapping needs no file change:")
registry._FUNCTIONS['pub.parse_money@1'] = lambda s: 999999
rt2 = Runtime(); print(f"    bind('pub.parse_money@1')('1.00') = {rt2.bind('pub.parse_money@1')('1.00')}  <-- swapped in-process, digest unchanged")

print("(c) MONKEYPATCH THE GUARD: the mock is ordinary importable Python; untrusted code can disable its checks.")
registry.Runtime.revoke = lambda self, cap: None      # neutralise revocation entirely
rt3 = Runtime(); h = rt3.bind('private.project_risk_score@1', scopes={'project-a'}, effects={'project.policy'})
rt3.revoke('private.project_risk_score@1')
try: print(f"    after neutralised revoke, private fn still returns {h({'errors':1})}  <-- revocation bypassed")
except InvalidBinding: print("    revocation held")
print("\n    All three are the 'honest mock' limits the packet itself names: no sandbox, no key custody, no signed artifact.")
