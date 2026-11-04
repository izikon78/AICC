"""Fair baseline for Arm C (protocol: 'compare using the SAME policy envelope, not a bare unsafe import').
An ordinary decorator gives scopes, effects, expiry and revocation, with revocation shared across instances and processes
through a plain file (ordinary caching). Same in-process trust model as the mock host: no sandbox, no signatures."""
import functools, json, os, tempfile, time

REVOCATIONS = os.path.join(tempfile.gettempdir(), "r8_conventional_revocations.json")


class PermissionDenied(Exception): pass
class InvalidBinding(Exception): pass


def _revoked():
    try: return set(json.load(open(REVOCATIONS)))
    except (OSError, ValueError): return set()


def revoke(cap):
    json.dump(sorted(_revoked() | {cap}), open(REVOCATIONS, "w"))


def envelope(cap, required_scope, required_effects=(), ttl_seconds=600):
    def deco(fn):
        def bind(scopes=(), effects=()):
            if required_scope not in scopes: raise PermissionDenied("scope")
            if not set(required_effects) <= set(effects): raise PermissionDenied("effects")
            if cap in _revoked(): raise PermissionDenied("revoked")
            expiry = time.monotonic() + ttl_seconds
            @functools.wraps(fn)
            def call(*a, **k):
                if cap in _revoked(): raise InvalidBinding("revoked")
                if time.monotonic() > expiry: raise InvalidBinding("expired")
                return fn(*a, **k)
            return call
        return bind
    return deco


@envelope("private.toy_score@1", "project-a", ("project.policy",), ttl_seconds=1)
def toy_score(event):            # stand-in for private logic; the private implementation itself is never imported here
    return len(event)


if __name__ == "__main__":
    import subprocess, sys
    if os.path.exists(REVOCATIONS): os.remove(REVOCATIONS)
    def check(label, fn):
        try: print(f"{label:58s} -> {fn()!r}")
        except Exception as e: print(f"{label:58s} -> {type(e).__name__}: {e}")
    check("C1 public-only bind", lambda: toy_score())
    f = toy_score(scopes=("project-a",), effects=("project.policy",))
    check("C2 authorised bind and call", lambda: f({"a": 1, "b": 2}))
    check("C4 call after ttl (1 s)", lambda: (time.sleep(1.2), f({"a": 1}))[1])
    g = toy_score(scopes=("project-a",), effects=("project.policy",))
    revoke("private.toy_score@1")
    check("C3 old binding after revoke", lambda: g({"a": 1}))
    check("P2 revocation seen by a separate PROCESS", lambda: subprocess.run([sys.executable, "-c",
          "import conventional_envelope as c\ntry: c.toy_score(scopes=('project-a',), effects=('project.policy',)); print('bound')\nexcept Exception as e: print(type(e).__name__, e)"],
          capture_output=True, text=True).stdout.strip())
    check("P1 scope spoofing (caller asserts project-a)", lambda: "same as mock: scopes are caller-asserted, no authentication")
    check("P3 direct bypass", lambda: "same as mock: toy_score.__wrapped__ or the undecorated module is reachable in-process")
    os.remove(REVOCATIONS)
    print("\nlines of code in this baseline:", sum(1 for l in open(__file__) if l.strip() and not l.strip().startswith("#")))
