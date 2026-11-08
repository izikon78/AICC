"""Independent Python variant written from group_by_window.contract.yaml (not from the sealed reference)."""
import unicodedata


class ContractError(Exception):
    def __init__(self, code): super().__init__(code); self.code = code


def _collapse(s): return " ".join(s.split())
def _norm(s): return _collapse(unicodedata.normalize("NFKC", s).casefold())


def group_by_window(events, window):
    if not isinstance(events, list): raise ContractError("E_TYPE")
    if type(window) is not int or window <= 0: raise ContractError("E_WINDOW")
    for ev in events:
        if not isinstance(ev, dict) or any(not isinstance(ev.get(f), str) for f in ("device", "kind", "message")): raise ContractError("E_TYPE")
        if type(ev.get("timestamp")) is not int: raise ContractError("E_TYPE")
    groups, open_by_key = [], {}
    for ev in sorted(events, key=lambda x: x["timestamp"]):
        k = (_norm(ev["device"]), _norm(ev["kind"]), _collapse(ev["message"]))
        g = open_by_key.get(k)
        if g is not None and ev["timestamp"] - g["first"] < window:
            g["last"] = ev["timestamp"]; g["count"] += 1
        else:
            g = {"device": k[0], "kind": k[1], "message": k[2], "first": ev["timestamp"], "last": ev["timestamp"], "count": 1}
            open_by_key[k] = g; groups.append(g)
    return groups
