"""Arm A: ordinary library reuse (strong baseline).
Written from fixtures/baseline_api.md and fixtures/activity_contract.md only; capabilities.py was not opened."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures"))
from capabilities import controller_logs, rollup_activity  # noqa: E402


def run_controller(n):
    return controller_logs(n)


def run_rollup(events, window_seconds=600, min_severity=0):
    return rollup_activity(events, window_seconds=window_seconds, min_severity=min_severity)
