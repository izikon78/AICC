"""Arm B: registry reuse through validated handles, pure-only policy.
Written from fixtures/capability_cards.md and the contracts it references; capabilities.py and registry.py were not opened."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"))
from registry import bind  # noqa: E402

_controller_logs = bind("cap:controller.logs@1", allowed_effects=())
_rollup_activity = bind("cap:activity.rollup@1", allowed_effects=())


def run_controller(n):
    return _controller_logs(n)


def run_rollup(events, window_seconds=600, min_severity=0):
    return _rollup_activity(events, window_seconds=window_seconds, min_severity=min_severity)
