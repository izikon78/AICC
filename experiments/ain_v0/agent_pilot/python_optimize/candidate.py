"""Readable control-flow reference; semantic services are shared with the VM."""


def run(host):
    # Binding the same 23 capabilities makes representation the controlled
    # variable. Expected-output tests separately exercise service semantics.
    op = {item["name"]: item["fn"] for item in host.catalog().values()}
    state = op["restore"](host)
    while op["has_next"](host):
        op["check_cancel"](host)
        record = op["next_record"](host)
        op["validate_record"](host, state, record)
        if op["record_kind"](record) == 0:
            if op["timestamp"](record) < op["frontier"](state):
                op["count"](host, state, 0)
            elif op["seen"](host, state, record):
                op["count"](host, state, 1)
            else:
                op["reserve"](host, state, record)
                if op["severity"](record) < op["minimum"](host):
                    op["count"](host, state, 2)
                else:
                    record = op["normalize"](record)
                    op["buffer"](host, state, record)
                    op["count"](host, state, 3)
        else:
            op["advance"](host, state, record)
            while op["pending_ready"](host, state):
                event = op["pop_pending"](host, state)
                op["aggregate"](host, state, event)
            groups = op["ready_groups"](host, state)
            reports = op["score"](host, state, groups)
            op["commit"](host, state, reports)
    return op["result"](host, state)
