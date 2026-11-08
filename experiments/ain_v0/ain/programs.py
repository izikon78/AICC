"""Language-authored control flow for the matched streaming workflow."""
from __future__ import annotations


def workflow_ir():
    registers = {
        "h": "host", "s": "state", "r": "record", "nr": "record",
        "kind": "int", "frontier": "int", "stamp": "int", "minimum": "int",
        "sev": "int", "b": "bool", "g": "groups", "p": "reports",
        "ret": "result", "c0": "int", "c1": "int", "c2": "int", "c3": "int",
    }

    def call(fn, args, dest=None):
        out = {"op": "call", "fn": fn, "args": args}
        if dest is not None:
            out["dest"] = dest
        return out

    def jump(target):
        return {"op": "jump", "target": target}

    def branch(yes, no):
        return {"op": "branch", "cond": "b", "then": yes, "else": no}

    def block(label, instructions, terminator):
        return {"label": label, "instructions": instructions, "terminator": terminator}

    blocks = [
        block("entry", [call("restore", ["h"], "s")] + [
            {"op": "const", "dest": f"c{i}", "value": i} for i in range(4)
        ], jump("loop")),
        block("loop", [call("has_next", ["h"], "b")], branch("read", "done")),
        block("read", [call("check_cancel", ["h"]),
                       call("next_record", ["h"], "r"),
                       call("validate_record", ["h", "s", "r"]),
                       call("record_kind", ["r"], "kind"),
                       {"op": "eq", "dest": "b", "left": "kind", "right": "c0"}],
              branch("event", "control")),
        block("event", [call("timestamp", ["r"], "stamp"),
                        call("frontier", ["s"], "frontier"),
                        {"op": "lt", "dest": "b", "left": "stamp", "right": "frontier"}],
              branch("late", "dedupe")),
        block("late", [call("count", ["h", "s", "c0"])], jump("loop")),
        block("dedupe", [call("seen", ["h", "s", "r"], "b")],
              branch("duplicate", "reserve")),
        block("duplicate", [call("count", ["h", "s", "c1"])], jump("loop")),
        block("reserve", [call("reserve", ["h", "s", "r"]),
                          call("normalize", ["r"], "nr"),
                          call("severity", ["nr"], "sev"),
                          call("minimum", ["h"], "minimum"),
                          {"op": "lt", "dest": "b", "left": "sev", "right": "minimum"}],
              branch("filtered", "accept")),
        block("filtered", [call("count", ["h", "s", "c2"])], jump("loop")),
        block("accept", [call("buffer", ["h", "s", "nr"]),
                         call("count", ["h", "s", "c3"])], jump("loop")),
        block("control", [call("advance", ["h", "s", "r"])], jump("drain")),
        block("drain", [call("pending_ready", ["h", "s"], "b")], branch("pop", "finalize")),
        block("pop", [call("pop_pending", ["h", "s"], "nr"),
                      call("aggregate", ["h", "s", "nr"])], jump("drain")),
        block("finalize", [call("ready_groups", ["h", "s"], "g"),
                           call("score", ["h", "s", "g"], "p"),
                           call("commit", ["h", "s", "p"])], jump("loop")),
        block("done", [call("result", ["h", "s"], "ret")],
              {"op": "return", "value": "ret"}),
    ]
    return {"version": 0, "registers": registers, "parameters": ["h"],
            "return_type": "result", "entry": "entry", "blocks": blocks}


def workflow_ain(catalog=None):
    from .language import encode_ain
    if catalog is None:
        from .engine import Host
        catalog = Host([]).catalog()
    return encode_ain(workflow_ir(), catalog)
