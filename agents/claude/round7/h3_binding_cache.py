"""H3 prototype (Claude, Round 7): scoped, revocable validated bindings. A research prototype, NOT a security mechanism.

Design (from my Round 5 reply): cache the *decision* "handle X fits requirement R under policy P in environment E",
keyed by digests, and re-check that key cheaply on every call through a short alias. Differences from fixtures/registry.py:
  * per-function digest of the code that will actually execute (normalised, so line shifts do not invalidate),
    compared with a manifest produced by a separate clean process (closes the file-hash vs loaded-code gap);
  * the key also covers contract text, requirement obligations, effect policy, environment and verifier version;
  * a revocation list is consulted on every call;
  * any mismatch raises StaleBinding naming the changed component (the point where a model may need to look again).
It does NOT provide signatures, isolation, or protection against code that can patch this module itself.
Run: python h3_binding_cache.py        (executes the self-test)"""
import hashlib
import json
import marshal
import os
import platform
import subprocess
import sys
import types

FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")
VERIFIER_VERSION = "h3-proto-0.1"


class StaleBinding(Exception):
    pass


def _norm_code(co):
    consts = tuple(_norm_code(c) if isinstance(c, types.CodeType) else c for c in co.co_consts)
    return co.replace(co_firstlineno=1, co_linetable=b"", co_consts=consts, co_filename="", co_qualname=co.co_name)


def code_digest(fn):
    """Digest of what will run: normalised bytecode, constants and names (no line numbers or file paths)."""
    return hashlib.sha256(marshal.dumps(_norm_code(fn.__code__))).hexdigest()


def text_digest(s):
    return hashlib.sha256(s.encode()).hexdigest()


def environment():
    return {"python": platform.python_version(), "impl": platform.python_implementation(),
            "os": platform.system(), "locale": os.environ.get("LC_ALL", os.environ.get("LANG", ""))}


def trusted_manifest():
    """Simulated publish step: a clean subprocess imports the on-disk artefacts and reports per-handle digests."""
    code = ("import json, sys; sys.path.insert(0, %r); sys.path.insert(0, %r); import registry, h3_binding_cache as h;"
            "print(json.dumps({k: h.code_digest(v[0]) for k, v in registry._CAPS.items()}))") % (FIX, os.path.dirname(os.path.abspath(__file__)))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


class Binder:
    def __init__(self, registry_module, manifest, revoked=None):
        self.reg, self.manifest, self.revoked = registry_module, manifest, revoked if revoked is not None else set()
        self.full_validations = 0

    def _key(self, handle, fn, contract, obligations, policy, env):
        return {"impl": code_digest(fn), "contract": text_digest(contract), "requirement": text_digest(json.dumps(sorted(obligations))),
                "policy": text_digest(json.dumps(sorted(policy))), "environment": text_digest(json.dumps(env, sort_keys=True)),
                "verifier": VERIFIER_VERSION}

    def validate(self, handle, contract, obligations, policy, tests):
        """Full validation, done once: manifest digest, declared effects vs policy, executable tests. Returns an alias."""
        self.full_validations += 1
        fn, effects = self.reg._CAPS[handle]
        if code_digest(fn) != self.manifest.get(handle):
            raise StaleBinding(f"{handle}: loaded code does not match the trusted manifest")
        if not effects.issubset(set(policy)):
            raise StaleBinding(f"{handle}: declared effects {sorted(effects - set(policy))} exceed policy")
        for args, expected in tests:
            if fn(*args) != expected:
                raise StaleBinding(f"{handle}: failed validation test {args}")
        decision = {"handle": handle, "key": self._key(handle, fn, contract, obligations, policy, environment())}
        binder, scope = self, {"contract": contract, "obligations": obligations, "policy": policy}

        def alias(*a, **k):
            binder.check(decision, scope)
            return binder.reg._CAPS[handle][0](*a, **k)
        alias.decision = decision
        alias.verdict = f"{handle} fit({','.join(sorted(obligations))}) valid; policy {sorted(policy) or 'pure'}; impl {decision['key']['impl'][:12]}"
        return alias

    def check(self, decision, scope, contract=None, obligations=None, policy=None):
        """Cheap per-call re-check of every key component plus revocation; never re-reads the contract into a model."""
        fn = self.reg._CAPS[decision["handle"]][0]
        now = self._key(decision["handle"], fn, contract or scope["contract"], obligations or scope["obligations"],
                        policy if policy is not None else scope["policy"], environment())
        if decision["key"]["impl"] in self.revoked:
            raise StaleBinding("revoked implementation digest")
        for part, value in decision["key"].items():
            if now[part] != value:
                raise StaleBinding(f"{part} changed since validation")


def selftest():
    sys.path.insert(0, FIX)
    import registry
    manifest = trusted_manifest()
    binder = Binder(registry, manifest)
    contract = open(os.path.join(FIX, "baseline_api.md")).read()
    obligations = ["T1 exact messages", "runs<=0 no messages"]
    tests = [((-2,), []), ((0,), []), ((2,), ["Starting controller service for 2 runs", "Restarting controller service for run 2 of 2"])]
    results = []

    def expect_stale(label, fn):
        try:
            fn(); results.append((label, "NOT DETECTED"))
        except StaleBinding as e:
            results.append((label, f"StaleBinding: {e}"))

    c = binder.validate("cap:controller.logs@1", contract, obligations, (), tests)
    outs = [c(k) for k in range(1, 21)]
    results.append(("20 alias calls after one validation", f"ok; full validations = {binder.full_validations}; last = {outs[-1][-1]!r}"))
    results.append(("model-visible verdict line", c.verdict))
    # environment change
    os.environ["LC_ALL"] = "fa_IR.UTF-8"; expect_stale("environment change (locale)", lambda: c(3)); os.environ.pop("LC_ALL")
    c(3)  # back to the validated environment: valid again
    # requirement change
    expect_stale("requirement change (new obligation)", lambda: binder.check(c.decision, {"contract": contract, "obligations": obligations + ["culture-invariant digits"], "policy": ()}))
    # policy change
    expect_stale("policy change (caller now allows filesystem.write)", lambda: binder.check(c.decision, {"contract": contract, "obligations": obligations, "policy": ("filesystem.write",)}))
    # contract text change
    expect_stale("contract text change", lambda: binder.check(c.decision, {"contract": contract + "\nNew clause.", "obligations": obligations, "policy": ()}))
    # implementation / dependency change in the running process
    original = registry._CAPS["cap:controller.logs@1"]
    registry._CAPS["cap:controller.logs@1"] = (lambda n: ["patched"], frozenset())
    expect_stale("implementation replaced in-process", lambda: c(2))
    registry._CAPS["cap:controller.logs@1"] = original
    # revocation
    binder.revoked.add(c.decision["key"]["impl"]); expect_stale("revocation of the implementation digest", lambda: c(2)); binder.revoked.clear()
    # tampered module already in memory (the probe (b) attack on the toy registry)
    fake = types.ModuleType("capabilities_fake")
    tampered = registry._CAPS["cap:controller.logs@1"]
    registry._CAPS["cap:controller.logs@1"] = (lambda n: ["Starting controller service for %d runs" % n, "EXFILTRATED"], frozenset())
    expect_stale("tampered code at validation time", lambda: binder.validate("cap:controller.logs@1", contract, obligations, (), tests))
    registry._CAPS["cap:controller.logs@1"] = tampered
    # declared-effect denial still works
    expect_stale("rollup_and_save under pure policy", lambda: binder.validate("cap:activity.rollup_and_save@1", "", ["T2"], (), []))
    # over-invalidation check: an unrelated function's digest is unaffected by changes elsewhere
    results.append(("per-function digests differ across handles", str(len(set(manifest.values())) == len(manifest))))
    for label, outcome in results:
        print(f"{label:52s} {outcome}")
    return results


if __name__ == "__main__":
    selftest()
