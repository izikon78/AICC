# Conventional Python API reference — Arm A

This is the **strong baseline**. Do not read `capabilities.py` unless a specific inspection trigger is recorded. You may import these compiled/implemented functions normally. This baseline already benefits from reuse and does not require code regeneration.

`from capabilities import controller_logs, rollup_activity`

- `controller_logs(runs:int) -> list[str]`: for `runs <= 0`, emits no messages. For `runs > 0`, produces exactly `runs` strings in order: first `Starting controller service for {runs} runs`; subsequent positions `i=1..runs-1` have `Restarting controller service for run {i+1} of {runs}`. Decimal formatting. No external effects. Errors in logger not modeled (function returns list).
- `rollup_activity(events:list[dict], window_seconds:int=600, min_severity:int=0) -> list[dict]`: documented behavior is in `activity_contract.md`; use that document if necessary. No external I/O. Raises ValueError for non-positive/noninteger window or severity outside 0..2; TypeError for non-list input.

The source implementation may be inspected if the API documentation is insufficient for an important property, but record an `INSPECT_SOURCE` event.
