# Human-readable view of the real events-00 build composition.
# Execute after binding the unchanged approved functions.
program = lambda r: group_sum(
    filter_lt(
        filter_gte(
            dedupe_by(filter_eq(r, 'kind', 'event'), 'id'),
            'severity', 2),
        'timestamp', 20),
    'group', 'value')
