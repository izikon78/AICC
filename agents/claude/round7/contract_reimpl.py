"""Independent implementation written ONLY from fixtures/activity_contract.md and baseline_api.md (capabilities.py not opened).
Where the contract is silent, this file deliberately takes the most literal reading, to test whether the contract pins behaviour.
Literal choices: severity matched case-insensitively WITHOUT trimming; only INTERNAL runs of ASCII whitespace in messages are
collapsed (edges kept); output severity uses the contract's numeric scale; events type is checked before the parameters."""
import re

SCALE = {"info": 0, "warning": 1, "critical": 2}
_ASCII_WS = "[ \t\n\r\f\v]"


def run_controller(n):
    if n <= 0:
        return []
    return [f"Starting controller service for {n} runs"] + [f"Restarting controller service for run {i + 1} of {n}" for i in range(1, n)]


def _collapse_internal(msg):
    m = re.match(rf"^({_ASCII_WS}*)(.*?)({_ASCII_WS}*)$", msg, re.S)
    lead, core, trail = m.group(1), m.group(2), m.group(3)
    return lead + re.sub(rf"{_ASCII_WS}+", " ", core) + trail


def _valid(e):
    if not isinstance(e, dict):
        return None
    for k in ("event_id", "device", "kind"):
        v = e.get(k)
        if not isinstance(v, str) or not v.strip():
            return None
    if not isinstance(e.get("message"), str):
        return None
    ts = e.get("timestamp")
    if type(ts) is not int or ts < 0:
        return None
    sev = e.get("severity")
    if not isinstance(sev, str) or sev.lower() not in SCALE:
        return None
    return {"event_id": e["event_id"].strip(), "device": e["device"].strip().lower(), "kind": e["kind"].strip().lower(),
            "message": _collapse_internal(e["message"]), "timestamp": ts, "sev": SCALE[sev.lower()]}


def run_rollup(events, window_seconds=600, min_severity=0):
    if not isinstance(events, list):
        raise TypeError("events must be a list")
    if type(window_seconds) is not int or window_seconds <= 0:
        raise ValueError("window_seconds must be a positive integer")
    if type(min_severity) is not int or min_severity not in (0, 1, 2):
        raise ValueError("min_severity must be 0, 1 or 2")
    valid = [v for v in (_valid(e) for e in events) if v is not None and v["sev"] >= min_severity]
    valid.sort(key=lambda v: (v["timestamp"], v["event_id"]))
    active, groups = {}, []
    for v in valid:
        key = (v["device"], v["kind"], v["message"])
        g = active.get(key)
        if g is not None and v["timestamp"] - g["last_timestamp"] <= window_seconds:
            g["last_timestamp"] = v["timestamp"]; g["count"] += 1; g["event_ids"].append(v["event_id"])
            g["severity"] = max(g["severity"], v["sev"])
        else:
            g = {"device": key[0], "kind": key[1], "message": key[2], "first_timestamp": v["timestamp"],
                 "last_timestamp": v["timestamp"], "severity": v["sev"], "count": 1, "event_ids": [v["event_id"]]}
            active[key] = g; groups.append(g)
    groups.sort(key=lambda g: (g["first_timestamp"], g["device"], g["kind"], g["message"]))
    return groups
