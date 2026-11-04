"""Small deterministic capability registry for H1/H3 experiments."""
import hashlib
from pathlib import Path
from capabilities import (
    controller_logs, controller_logs_near_miss,
    rollup_activity, rollup_by_eventid_near_miss, rollup_and_save_denylisted,
)

FILE_HASH = hashlib.sha256(Path(__file__).with_name('capabilities.py').read_bytes()).hexdigest()
_CAPS = {
    'cap:controller.logs@1': (controller_logs, frozenset()),
    'cap:controller.logs_zero_based@1': (controller_logs_near_miss, frozenset()),
    'cap:activity.rollup@1': (rollup_activity, frozenset()),
    'cap:activity.rollup_by_eventid@1': (rollup_by_eventid_near_miss, frozenset()),
    'cap:activity.rollup_and_save@1': (rollup_and_save_denylisted, frozenset({'filesystem.write'})),
}

class CapabilityDenied(Exception):
    pass

class UnknownCapability(Exception):
    pass


def bind(identifier: str, allowed_effects=(), expected_digest: str | None = None):
    """Simulates validation + a reusable bound handle; no LLM is called."""
    if identifier not in _CAPS:
        raise UnknownCapability(identifier)
    if expected_digest is not None and expected_digest != FILE_HASH:
        raise CapabilityDenied('artifact digest changed')
    function, effects = _CAPS[identifier]
    if not effects.issubset(set(allowed_effects)):
        raise CapabilityDenied(f'denied effects: {sorted(effects.difference(allowed_effects))}')
    return function
