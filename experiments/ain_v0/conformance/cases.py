"""Conformance cases. Expectation sources are labelled: HAND (derived by hand from COMPLEX_TASK.md and the frozen
decisions), INVARIANT (must equal an uninterrupted run), DIFFERENTIAL (forms must agree; no oracle)."""
import json, random
from ain_v0.primitives import I64
from harness import EXAMPLE


def ev(off, eid, ts, sev, tenant="t1", device="pump-1", kind="pressure", message="high pressure"):
    return {"type": "event", "offset": off, "tenant": tenant, "event_id": eid, "device": device, "kind": kind,
            "message": message, "timestamp": ts, "severity": sev}
def wm(off, w): return {"type": "watermark", "offset": off, "watermark": w}
def end(off): return {"type": "end", "offset": off}
def cfg(**kw):
    v = dict(zip(("window", "lateness", "horizon", "concurrency", "queue", "buffered_events", "dedupe_entries", "open_groups", "epoch_reports"), EXAMPLE))
    v.update(kw); return list(v.values())
def C(name, records, expect, **kw):
    return {"name": name, "records": records, "config": kw.pop("config", EXAMPLE), "minimum": kw.pop("minimum", 1), "expect": expect, **kw}

# ---- expectation helpers (each returns a list of failure strings)
def status(s, code=None, offset="any"):
    def f(o):
        out = o["outcomes"][-1]; bad = []
        if out["status"] != s: bad.append(f"status {out['status']} != {s}")
        if code and (out["error"] or {}).get("code") != code: bad.append(f"error {(out['error'] or {}).get('code')} != {code}")
        if offset != "any" and (out["error"] or {}).get("offset") != offset: bad.append(f"error offset {(out['error'] or {}).get('offset')} != {offset}")
        return bad
    return f
def reports(rows, fields=("first", "last", "count", "severity_sum", "first_offset")):
    return lambda o: [] if [[r[k] for k in fields] for r in o["published"]] == rows else [f"reports {[[r[k] for k in fields] for r in o['published']]} != {rows}"]
def checkpoint(**want):
    return lambda o: [f"checkpoint {k} {o['checkpoint'][k]} != {v}" for k, v in want.items() if o["checkpoint"] is None or o["checkpoint"][k] != v]
def commits(n):
    return lambda o: [] if sum(1 for x in o["sink_log"] if x[0] == "commit") == n else [f"commits {sum(1 for x in o['sink_log'] if x[0] == 'commit')} != {n}"]
def all_of(*fs): return lambda o: [m for f in fs for m in f(o)]

SPEC = [ev(1, "A", 100, 0), ev(2, "A", 90, 3), ev(3, "B", 200, 2), ev(4, "C", 150, 1), wm(5, 900), ev(6, "D", 779, 3),
        ev(7, "D", 780, 3), wm(8, 1500), ev(9, "A", 1400, 2), end(10)]
K = lambda eid: json.dumps(["t1", eid])
SEEDKEY = json.dumps(["t1", "pump-1", "pressure", "high pressure"], ensure_ascii=False)
def seed_group(count, sev_sum):
    return {"state": {"cursor": 1, "watermark": 0, "groups": [{"tenant": "t1", "device": "pump-1", "kind": "pressure", "message": "high pressure",
            "first": 5, "last": 5, "first_offset": 0, "count": count, "severity_sum": sev_sum}], "newest": {SEEDKEY: 0}}}
MANY = [ev(i, f"m{i}", 10 + i, 2, device=f"dev-{i}") for i in range(1, 61)] + [wm(61, 2000), end(62)]
TWO_EPOCHS = [ev(1, "a", 10, 2), ev(2, "b", 20, 2, device="d2"), wm(3, 900), ev(4, "c", 800, 2), ev(5, "d", 810, 2, device="d3"), wm(6, 2000), end(7)]

HAND = [
    C("spec_trace_10_steps", SPEC, all_of(status("COMPLETED"), commits(3), reports([[150, 200, 2, 3, 4], [780, 780, 1, 3, 7], [1400, 1400, 1, 2, 9]]),
      checkpoint(cursor=10, complete=True, dedupe=[], counters={"late": 1, "duplicate": 1, "filtered": 1, "accepted": 4}))),
    C("spec_trace_checkpoint_after_watermark_1500", SPEC[:9], all_of(status("SUSPENDED"), commits(2),
      checkpoint(cursor=8, dedupe=[[K("B"), 200], [K("D"), 780]], buffered_offsets=[], counters={"late": 1, "duplicate": 1, "filtered": 1, "accepted": 3}))),
    C("normalization_and_whitespace_set", [ev(1, "p1", 10, 1, device="Pump\u00a0 1"), ev(2, "p2", 11, 1, device="\uff30\uff35\uff2d\uff30 1"),
      ev(3, "p3", 12, 1, device="pump\u20281"), ev(4, "p4", 13, 1, device="PUMP 1"), ev(5, "p5", 14, 1, device="pump\x1c1"),
      ev(6, "s1", 15, 1, device="Stra\u00dfe 1"), ev(7, "s2", 16, 1, device="STRASSE 1"), ev(8, "v1", 17, 1, device="valve", message="High  pressure"),
      ev(9, "v2", 18, 1, device="valve", message="high pressure"), end(10)],
      all_of(status("COMPLETED"), lambda o: [] if [(r["device"], r["message"], r["count"]) for r in o["published"]] ==
             [("pump 1", "high pressure", 4), ("pump\x1c1", "high pressure", 1), ("strasse 1", "high pressure", 2), ("valve", "High pressure", 1), ("valve", "high pressure", 1)]
             else [f"groups {[(r['device'], r['message'], r['count']) for r in o['published']]}"])),
    C("anchored_window_boundary", [ev(1, "a", 0, 1), ev(2, "b", 599, 1), ev(3, "c", 600, 1), end(4)], all_of(status("COMPLETED"), reports([[0, 599, 2, 2, 1], [600, 600, 1, 1, 3]]))),
    C("rows_at_frontier_wait", [ev(1, "a", 779, 1), ev(2, "b", 780, 1), wm(3, 900)], all_of(status("SUSPENDED"), commits(1), reports([]),
      checkpoint(buffered_offsets=[2], open_groups=[[779, 1, 779, 1, 1]]))),
    C("rows_at_frontier_then_end", [ev(1, "a", 779, 1), ev(2, "b", 780, 1), wm(3, 900), end(4)], all_of(status("COMPLETED"), reports([[779, 780, 2, 2, 1]]))),
    C("equal_timestamps_ordered_by_offset", [ev(1, "a", 50, 1, device="b"), ev(2, "b", 50, 1, device="a"), end(3)],
      all_of(status("COMPLETED"), lambda o: [] if [r["device"] for r in o["published"]] == ["b", "a"] else ["order"])),
    C("lateness_zero_boundary", [wm(1, 100), ev(2, "a", 99, 1), ev(3, "b", 100, 1), end(4)], all_of(status("COMPLETED"),
      reports([[100, 100, 1, 1, 3]]), checkpoint(counters={"late": 1, "duplicate": 0, "filtered": 0, "accepted": 1})), config=cfg(lateness=0)),
    C("timestamp_max_valid", [ev(1, "a", I64, 3), wm(2, I64), end(3)], all_of(status("COMPLETED"), reports([[I64, I64, 1, 3, 1]]))),
    C("timestamp_overflow_invalid", [ev(1, "a", I64 + 1, 1)], status("FAILED", "INVALID_RECORD", 1)),
    C("timestamp_negative_invalid", [ev(1, "a", -1, 1)], status("FAILED", "INVALID_RECORD", 1)),
    C("severity_bool_invalid", [ev(1, "a", 5, True)], status("FAILED", "INVALID_RECORD", 1)),
    C("severity_four_invalid", [ev(1, "a", 5, 4)], status("FAILED", "INVALID_RECORD", 1)),
    C("extra_field_invalid", [{**ev(1, "a", 5, 1), "x": 1}], status("FAILED", "INVALID_RECORD", 1)),
    C("unpaired_surrogate_invalid", [ev(1, "a", 5, 1, message="bad\ud800")], status("FAILED", "INVALID_RECORD", 1)),
    C("empty_tenant_invalid", [ev(1, "a", 5, 1, tenant="")], status("FAILED", "INVALID_RECORD", 1)),
    C("tag_257_invalid_but_128_tenant_valid", [ev(1, "a", 5, 1, tenant="t" * 128), ev(2, "b", 5, 1, device="d" * 257)], status("FAILED", "INVALID_RECORD", 2)),
    C("malformed_duplicate_still_invalid", [ev(1, "a", 5, 1), {**ev(2, "a", 5, 1), "severity": "3"}], status("FAILED", "INVALID_RECORD", 2)),
    C("decreasing_offset", [ev(1, "a", 5, 1), ev(3, "b", 5, 1), ev(2, "c", 5, 1)], status("FAILED", "OFFSET_ORDER", 2)),
    C("equal_offset", [ev(1, "a", 5, 1), ev(1, "b", 5, 1)], status("FAILED", "OFFSET_ORDER", 1)),
    C("decreasing_watermark_after_commit", [ev(1, "a", 5, 1), wm(2, 900), wm(3, 800)], all_of(status("FAILED", "WATERMARK_ORDER", 3), commits(1), reports([[5, 5, 1, 1, 1]]))),
    C("equal_watermark_two_epochs", [wm(1, 900), wm(2, 900)], all_of(status("SUSPENDED"), commits(2))),
    C("after_end_on_restart", [ev(1, "a", 5, 1), end(2), ev(3, "b", 6, 1)], all_of(status("FAILED", "AFTER_END", 3),
      lambda o: [] if [x["status"] for x in o["outcomes"]] == ["COMPLETED", "FAILED"] else [str(o["outcomes"])]), runs=2),
    C("restart_complete_no_new_records", [ev(1, "a", 5, 1), end(2)], all_of(commits(1), lambda o: [] if [x["status"] for x in o["outcomes"]] == ["COMPLETED", "COMPLETED"] else ["statuses"]), runs=2),
    C("overflow_count", [wm(1, 0), ev(2, "x", 10, 1), wm(3, 1000)], all_of(status("FAILED", "OVERFLOW", 2), commits(0)), seed=seed_group(I64, 0)),
    C("overflow_severity_sum", [wm(1, 0), ev(2, "x", 10, 2), wm(3, 1000)], all_of(status("FAILED", "OVERFLOW", 2), commits(0)), seed=seed_group(1, I64 - 1)),
    C("capacity_buffered_events", [ev(1, "a", 5, 1), ev(2, "b", 6, 1), ev(3, "c", 7, 1)], status("FAILED", "CAPACITY", 3), config=cfg(buffered_events=2)),
    C("capacity_dedupe_entries", [ev(1, "a", 5, 0), ev(2, "b", 6, 0), ev(3, "c", 7, 0)], status("FAILED", "CAPACITY", 3), config=cfg(dedupe_entries=2)),
    C("capacity_open_groups", [ev(1, "a", 5, 1), ev(2, "b", 6, 1, device="other"), wm(3, 2000)], status("FAILED", "CAPACITY", 2), config=cfg(open_groups=1)),
    C("capacity_epoch_reports", [ev(1, "a", 5, 1), ev(2, "b", 6, 1, device="other"), wm(3, 2000)], status("FAILED", "CAPACITY", 3), config=cfg(epoch_reports=1)),
    C("config_horizon_below_window", [end(1)], status("FAILED", "INVALID_CONFIG"), config=cfg(horizon=599)),
    C("config_window_zero", [end(1)], status("FAILED", "INVALID_CONFIG"), config=cfg(window=0)),
    C("invalid_restored_checkpoint", [wm(1, 0), end(2)], status("FAILED", "INVALID_CHECKPOINT"), seed={"state": {"cursor": 1}, "wrong_config": True}),
    C("effect_denied", [end(1)], status("FAILED", "EFFECT_DENIED"), manifest={"policy_version": "risk-v3", "effects": ["source.read", "sink.read", "policy.invoke"]}),
    C("end_without_watermarks", [ev(1, "a", 5, 1), ev(2, "b", 900, 1), end(3)], all_of(status("COMPLETED"), reports([[5, 5, 1, 1, 1], [900, 900, 1, 1, 2]]))),
    C("exhausted_without_end_suspends", [ev(1, "a", 5, 1), wm(2, 900), ev(3, "b", 950, 1)], all_of(status("SUSPENDED"), commits(1), checkpoint(cursor=2, buffered_offsets=[]))),
    C("queue_saturation_limits", MANY, all_of(status("COMPLETED"), lambda o: [] if (o["policy"]["max_running"], o["policy"]["max_waiting"], len(o["published"])) == (8, 32, 60) else [str(o["policy"])])),
    C("reverse_completion_same_publication", MANY, all_of(status("COMPLETED"), lambda o: [] if [r["first_offset"] for r in o["published"]] == list(range(1, 61)) else ["order"]), scheduler="reverse"),
    C("multiple_policy_failures_lowest_index", TWO_EPOCHS, all_of(status("FAILED", "POLICY_ERROR"), commits(1), reports([[10, 10, 1, 2, 1], [20, 20, 1, 2, 2]]),
      lambda o: [] if o["outcomes"][-1]["error"]["detail"] == "group index 0" else [o["outcomes"][-1]["error"]["detail"]]),
      policy={"fail_first_offsets": [4, 5]}, scheduler="reverse"),
    C("invalid_policy_output", TWO_EPOCHS, all_of(status("FAILED", "POLICY_ERROR"), commits(1)), policy={"invalid_first_offsets": [5]}),
    C("authority_revoked_before_third_call", MANY, all_of(status("FAILED", "AUTHORITY"), commits(0), lambda o: [] if len(o["policy"]["starts"]) == 2 else ["starts"]), revoke_at={"point": "policy_start", "n": 3}),
    C("authority_revoked_before_second_commit", TWO_EPOCHS, all_of(status("FAILED", "AUTHORITY", 6), commits(1)), revoke_at={"point": "commit", "n": 2}),
    C("cancel_at_admission_mid_epoch", TWO_EPOCHS, all_of(status("CANCELLED"), commits(1), checkpoint(cursor=3)), cancel_at={"point": "admit", "n": 5}),
    C("cancel_at_third_policy_start", MANY, all_of(status("CANCELLED"), commits(0), lambda o: [] if len(o["policy"]["starts"]) == 2 else ["starts"]), cancel_at={"point": "policy_start", "n": 3}),
    C("cancel_before_first_commit", TWO_EPOCHS, all_of(status("CANCELLED"), commits(0)), cancel_at={"point": "commit", "n": 1}),
    C("cancel_beats_policy_error", TWO_EPOCHS, status("CANCELLED"), policy={"fail_first_offsets": [1]}, cancel_at={"point": "policy_start", "n": 2}),
    C("authority_beats_policy_error", TWO_EPOCHS, status("FAILED", "AUTHORITY"), policy={"fail_first_offsets": [1]}, revoke_at={"point": "policy_start", "n": 2}),
]
CRASH = [C(f"crash_{p}_epoch_{o}", SPEC, None, crash={"point": p, "offset": o}) for p in ("before_stage", "before_commit", "after_commit", "ack_lost_retry") for o in (5, 8, 10)]


def random_cases(n, seed=8):
    rng = random.Random(seed); devs = ["pump-1", "PUMP-1", "Pump\u00a01", "pump\x1c1", "Stra\u00dfe", "STRASSE", "\ufb01x", "fix", "valve"]
    msgs = ["high pressure", "High  pressure", "high\u2028pressure", "low"]; out = []
    for k in range(n):
        window = rng.choice([5, 20, 60]); lat = rng.choice([0, 3, 10]); hor = window * rng.choice([1, 2, 5])
        caps = [rng.choice([3, 6, 100]) for _ in range(5)]
        conf = [window, lat, hor, rng.choice([1, 2, 8]), rng.choice([1, 4, 32])] + [caps[0] * 10, caps[1] * 10, caps[2] * 10, caps[3] * 10]
        recs, off, t, w = [], 0, 0, 0
        for _ in range(rng.randint(5, 40)):
            off += rng.choice([1, 1, 2]); r = rng.random()
            if r < 0.15:
                w = max(w, t - rng.randint(0, 15)) if rng.random() < 0.95 else max(0, w - 1); recs.append(wm(off, w))
            else:
                t += rng.randint(0, 6); ts = max(0, t - rng.randint(0, 25))
                e = ev(off, f"id{rng.randint(0, 12)}", ts, rng.randint(0, 3), tenant=rng.choice(["t1", "t2"]), device=rng.choice(devs), message=rng.choice(msgs))
                if rng.random() < 0.02: e["severity"] = "bad"
                recs.append(e)
        if rng.random() < 0.7: recs.append(end(off + 1))
        case = {"name": f"random_{k:03d}", "records": recs, "config": conf, "minimum": rng.choice([0, 1, 2]),
                "scheduler": rng.choice(["fifo", "reverse", f"seed:{k}"]), "policy": {"kind": "hash"}}
        firsts = [x["offset"] for x in recs if x["type"] == "event"]
        if firsts and rng.random() < 0.15: case["policy"]["fail_first_offsets"] = rng.sample(firsts, min(2, len(firsts)))
        if rng.random() < 0.1: case["cancel_at"] = {"point": rng.choice(["admit", "policy_start", "commit"]), "n": rng.randint(1, 8)}
        if rng.random() < 0.1: case["revoke_at"] = {"point": rng.choice(["policy_start", "commit"]), "n": rng.randint(1, 8)}
        wms = [x["offset"] for x in recs if x["type"] in ("watermark", "end")]
        if wms and rng.random() < 0.15: case["crash"] = {"point": rng.choice(["before_stage", "before_commit", "after_commit", "ack_lost_retry"]), "offset": rng.choice(wms)}
        out.append(case)
    return out
