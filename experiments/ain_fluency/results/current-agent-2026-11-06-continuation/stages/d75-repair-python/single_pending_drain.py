def run(host):
    op = {item['name']: item['fn'] for item in host.catalog().values()}
    state = op['restore'](host)
    while op['has_next'](host):
        op['check_cancel'](host)
        record = op['next_record'](host)
        op['validate_record'](host, state, record)
        kind = op['record_kind'](record)
        if kind == 0:
            if op['timestamp'](record) < op['frontier'](state):
                op['count'](host, state, 0)
            elif op['seen'](host, state, record):
                op['count'](host, state, 1)
            else:
                op['reserve'](host, state, record)
                age = op['timestamp'](record) - op['frontier'](state)
                threshold = op['minimum'](host)
                if age < 75 and threshold < 3:
                    threshold = threshold + 1
                if op['severity'](record) < threshold:
                    op['count'](host, state, 2)
                else:
                    normalized = op['normalize'](record)
                    op['buffer'](host, state, normalized)
                    op['count'](host, state, 3)
        else:
            op['advance'](host, state, record)
            if op['pending_ready'](host, state):
                pending = op['pop_pending'](host, state)
                op['aggregate'](host, state, pending)
            groups = op['ready_groups'](host, state)
            reports = op['score'](host, state, groups)
            op['commit'](host, state, reports)
    return op['result'](host, state)
