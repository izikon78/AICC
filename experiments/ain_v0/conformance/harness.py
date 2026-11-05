"""Shared deterministic conformance harness. Every form runs against the same records, policy fixtures, scheduler,
cancellation/authority triggers, crash plan and reference sink, and is compared on its full visible effect trace."""
import hashlib, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ain_v0 import core, primitives as P
from ain_v0.reference import run_reference

HERE = os.path.dirname(os.path.abspath(__file__))
PROGRAMS = os.path.join(os.path.dirname(HERE), "programs")
MANIFEST = {"policy_version": "risk-v3", "interfaces": {"policy": "score(group)->(int,int)", "sink": "txn-v1"},
            "effects": sorted(P.REQUIRED_EFFECTS)}
EXAMPLE = [600, 120, 1200, 8, 32, 100000, 200000, 100000, 100000]


# ---------------------------------------------------------------- program rendering (config literals are part of the program)
def render(form, values, minimum):
    text = open(os.path.join(PROGRAMS, "workflow." + form)).read()
    lit = ", ".join(map(str, EXAMPLE)) if form == "ir" else ",".join(map(str, EXAMPLE))
    new = ", ".join(map(str, values)) if form == "ir" else ",".join(map(str, values))
    assert lit in text
    text = text.replace(lit, new)
    return text.replace("(normalized, 1, config)", f"(normalized, {minimum}, config)") if form == "ir" else text.replace("!105(%07,1,%00)", f"!105(%07,{minimum},%00)")


def form_runner(form):
    if form == "reference":
        return lambda env, case: run_reference(env)
    def run(env, case):
        ast = (core.parse_ir if form == "ir" else core.parse_ain)(render(form, case["config"], case["minimum"]))
        return core.run(ast, env)
    return run


# ---------------------------------------------------------------- fixtures
class PolicyFixture:
    def __init__(self, spec):
        self.kind, self.fail = spec.get("kind", "constant"), set(spec.get("fail_first_offsets", ()))
        self.invalid = set(spec.get("invalid_first_offsets", ()))
    def __call__(self, g, version):
        if g["first_offset"] in self.fail:
            raise P.PolicyFailure("declared")
        if g["first_offset"] in self.invalid:
            return (1001, 1)
        if self.kind == "constant":
            return (500, 1)
        h = int(hashlib.sha256(P.canonical([g["tenant"], g["device"], g["kind"], g["message"], g["first"], g["count"], version]).encode()).hexdigest(), 16)
        return (h % 1001, sorted(P.REASONS)[h % len(P.REASONS)])


def scheduler(name):
    if name == "fifo":
        return lambda running: running[0]
    if name == "reverse":
        return lambda running: running[-1]
    rng = random.Random(int(name.split(":")[1]))
    return lambda running: rng.choice(running)


class Hooks(dict):
    def __init__(self, case):
        super().__init__(log=[], stats={"starts": [], "completions": [], "max_running": 0, "max_waiting": 0})
        self.cancel_at, self.revoke_at = case.get("cancel_at"), case.get("revoke_at")
        self.n = {}; self.cancelled = False; self.revoked = False
        self["cancel"], self["authority"] = self._cancel, self._authority
    def _count(self, kind, point):
        k = (kind, point); self.n[k] = self.n.get(k, 0) + 1; return self.n[k]
    def _cancel(self, point):
        i = self._count("cancel", point)
        if self.cancel_at and self.cancel_at["point"] == point and i >= self.cancel_at["n"]:
            self.cancelled = True
        self["log"].append(["cancel", point, i, self.cancelled]); return self.cancelled
    def _authority(self, point):
        i = self._count("authority", point)
        if self.revoke_at and self.revoke_at["point"] == point and i >= self.revoke_at["n"]:
            self.revoked = True
        self["log"].append(["authority", point, i, not self.revoked]); return not self.revoked


class CrashPlan:
    def __init__(self, spec): self.spec, self.fired = spec, False
    def fire(self, point, offset):
        if self.spec and not self.fired and self.spec["point"] == point and self.spec["offset"] == offset:
            self.fired = True; return True
        return False


def seeded_checkpoint(case):
    """Build a valid restored checkpoint (same manifest/config) with injected state, for overflow/limit tests."""
    cfg = P.validate_config(case["config"], case["minimum"])
    pinned = P.pin_manifest(MANIFEST, cfg, P.REQUIRED_EFFECTS)
    state = P.new_state(); state.update(case["seed"]["state"])
    if case["seed"].get("wrong_config"):
        cfg = {**cfg, "window": cfg["window"] + 1}
    return {"manifest_id": pinned["id"], "config": cfg, "state": state}


def execute(form, case):
    runner = form_runner(form); sink = P.Sink(case.get("source_id", "src-1"))
    if case.get("seed"):
        sink.checkpoint = seeded_checkpoint(case)
    hooks = Hooks(case); crash = CrashPlan(case.get("crash")); outcomes = []
    for _ in range(case.get("runs", 1)):
        for attempt in range(4):
            env = {"records": case["records"], "sink": sink, "manifest": case.get("manifest", MANIFEST),
                   "policy": PolicyFixture(case.get("policy", {})), "schedule": scheduler(case.get("scheduler", "fifo")),
                   "hooks": hooks, "crash": crash, "config": case["config"], "minimum": case["minimum"]}
            try:
                outcomes.append(runner(env, case)); break
            except P.Crash:
                outcomes.append({"status": "CRASH"})
    st = hooks["stats"]
    return {"outcomes": outcomes, "published": sink.published, "sink_log": sink.log,
            "checkpoint": P.observable_checkpoint(sink.checkpoint), "hook_log": hooks["log"],
            "policy": {"starts": st["starts"], "completions": st["completions"], "max_running": st["max_running"], "max_waiting": st["max_waiting"]}}
