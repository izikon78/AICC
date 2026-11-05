"""Readable reference implementation of the streaming workflow (form 1: conventional Python).
One imperative function composed from the shared primitives. Decisions D-xx are in SEMANTICS_FREEZE.md."""
import copy
from .primitives import (INF, dedupe_key, Cancelled, Crash, WorkflowError, add_to_group, check_unicode, evict_dedupe, frontier,
                         lt, make_report, norm_tag, collapse, outcome, pin_manifest, resolve_epoch, restore_state,
                         run_policy_calls, validate_config, validate_record, REQUIRED_EFFECTS)


def run_reference(env):
    hooks, sink, records = env["hooks"], env["sink"], env["records"]
    try:
        check_unicode()
        cfg = validate_config(env["config"], env["minimum"])
        pinned = pin_manifest(env["manifest"], cfg, REQUIRED_EFFECTS)
        fence = sink.acquire_fence()
        state, pos = restore_state(sink, pinned, cfg, records)
        prev, ended = state["cursor"], state["complete"]
        for r in records[pos:]:
            if hooks["cancel"]("admit"):
                raise Cancelled()
            kind = validate_record(r, prev, ended)
            prev = r["offset"]
            if kind == "event":
                admit_event(state, r, cfg)
            elif kind == "watermark":
                if r["watermark"] < state["watermark"]:
                    raise WorkflowError("WATERMARK_ORDER", r["offset"], f"{r['watermark']} < {state['watermark']}")
                state["watermark"] = r["watermark"]
                state = run_epoch(env, state, cfg, pinned, fence, r["offset"], frontier(r["watermark"], cfg["lateness"]), False)
            else:
                run_epoch(env, state, cfg, pinned, fence, r["offset"], INF, True)
                return outcome("COMPLETED")
        return outcome("COMPLETED" if ended else "SUSPENDED")
    except Cancelled:
        return outcome("CANCELLED")
    except WorkflowError as e:
        return outcome("FAILED", e)


def admit_event(state, r, cfg):
    c = frontier(state["watermark"], cfg["lateness"])
    counters = state["counters"]
    if r["timestamp"] < c:                       # late: counted, discarded, reserves nothing
        counters["late"] += 1; return
    key = dedupe_key(r)                          # exact identifiers, never folded
    if key in state["dedupe"]:
        counters["duplicate"] += 1; return
    if len(state["dedupe"]) >= cfg["dedupe_entries"]:
        raise WorkflowError("CAPACITY", r["offset"], "dedupe_entries")
    state["dedupe"][key] = r["timestamp"]        # reserve before severity filtering
    if r["severity"] < cfg["minimum"]:
        counters["filtered"] += 1; return
    if len(state["buffer"]) >= cfg["buffered_events"]:
        raise WorkflowError("CAPACITY", r["offset"], "buffered_events")
    state["buffer"].append({**r, "n_device": norm_tag(r["device"]), "n_kind": norm_tag(r["kind"]),
                            "n_message": collapse(r["message"])})
    counters["accepted"] += 1


def run_epoch(env, state, cfg, pinned, fence, offset, c, is_end):
    hooks, sink, crash = env["hooks"], env["sink"], env.get("crash")
    due = sorted((e for e in state["buffer"] if lt(e["timestamp"], c)), key=lambda e: (e["timestamp"], e["offset"]))
    state["buffer"] = [e for e in state["buffer"] if not lt(e["timestamp"], c)]
    for e in due:
        add_to_group(state, e, cfg)
    final = sorted((g for g in state["groups"] if c == INF or g["first"] + cfg["window"] <= c),
                   key=lambda g: (g["first"], g["first_offset"]))
    if len(final) > cfg["epoch_reports"]:
        raise WorkflowError("CAPACITY", offset, "epoch_reports")
    done = {g["first_offset"] for g in final}
    state["groups"] = [g for g in state["groups"] if g["first_offset"] not in done]
    state["newest"] = {k: v for k, v in state["newest"].items() if v not in done}
    results, stop = run_policy_calls(final, env["policy"], pinned["policy_version"], cfg, hooks, env["schedule"])
    resolve_epoch(results, stop)
    reports = [make_report(sink.source_id, g, results[i], pinned["policy_version"]) for i, g in enumerate(final)]
    state["dedupe"] = evict_dedupe(state["dedupe"], c, cfg["horizon"])
    state["cursor"], state["complete"] = offset, is_end
    if crash and crash.fire("before_stage", offset):
        raise Crash()
    payload = {"epoch": [sink.source_id, offset], "reports": reports,
               "checkpoint": {"manifest_id": pinned["id"], "config": cfg, "state": copy.deepcopy(state)}}
    if crash and crash.fire("before_commit", offset):
        raise Crash()
    if hooks["cancel"]("commit"):
        raise Cancelled()
    if not hooks["authority"]("commit"):
        raise WorkflowError("AUTHORITY", offset, "commit")
    sink.commit(fence, payload["epoch"], payload)
    if crash and crash.fire("after_commit", offset):
        raise Crash()
    if crash and crash.fire("ack_lost_retry", offset):
        sink.commit(fence, payload["epoch"], payload)  # same writer retries: idempotent receipt, no new reports
    return copy.deepcopy(payload["checkpoint"]["state"])  # retire: continue from the committed snapshot
