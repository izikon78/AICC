"""One entry point for three representations with identical host services."""
from __future__ import annotations


def execute(records, mode="python", config=None, sink=None, **options):
    from .engine import Host, WorkflowError
    if mode not in ("python", "ir", "ain"):
        raise ValueError(f"Unknown execution mode: {mode!r}")
    host = None
    try:
        host = Host(records, config=config, sink=sink, **options)
        if mode == "python":
            from .reference import run
            return run(host)
        from .language import run_ir, run_ain
        from .programs import workflow_ir, workflow_ain
        catalog = host.catalog()
        if mode == "ir":
            return run_ir(workflow_ir(), catalog, [host], fuel=100_000_000)
        if mode == "ain":
            return run_ain(workflow_ain(catalog), catalog, [host], fuel=100_000_000)
    except WorkflowError as error:
        if host is None:
            return Host.error_result(error, source_id=options.get("source_id", "default"), sink=sink)
        return host.outcome(error)
