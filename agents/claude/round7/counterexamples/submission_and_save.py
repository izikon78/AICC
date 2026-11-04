"""Counterexample: same wrapper as Arm B, but binding a rejected candidate (and_save)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures"))
from registry import bind
_controller_logs = bind("cap:controller.logs@1", allowed_effects=())
_rollup_activity = bind("cap:activity.rollup_and_save@1", allowed_effects=())
def run_controller(n): return _controller_logs(n)
def run_rollup(events, window_seconds=600, min_severity=0): return _rollup_activity(events, window_seconds=window_seconds, min_severity=min_severity)
