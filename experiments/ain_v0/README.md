# AIN v0: first executable development study

This implements the [AIN plan](../../docs/ain/RESEARCH_PLAN.md)'s first engineering
gate on the [transactional streaming task](../../docs/ain/COMPLEX_TASK.md).
It is a prototype language and a local reference host, not a language-trained AI.

**Results: [first execution report](FIRST_EXECUTION_REPORT.md).** 69 engineering
tests pass, 27 processing workers agree, and all six one-submission agent edits
pass their judges. Numeric AIN is 22.5%–46.5% slower than Python by workload
execution medians in this instrumented interpreter. No economic saving is shown.

The matched controls are direct Python, a readable typed register IR, and AIN v0's
numeric serialization of **that same IR**. The symbolic spelling control and AIN
candidate coincide in this version. All reach the same 23 host primitives.
Language-level programs own the record loop, late/duplicate/filter branches,
buffer drain, and effect sequencing. The host owns anchored aggregation,
bounded asynchronous fixture policy, authority checks and transactional storage.
This division limits what a representation comparison can establish.

The sink is an in-memory reference implementation with atomic payload updates,
receipts and fencing under a lock. Fault/restart tests simulate crash boundaries;
they do not establish filesystem durability, distributed consensus or process
isolation. Private scoring rules are deterministic local fixtures.

## Reproduce

Use Python 3.12 with Unicode 15.0.0. Core code and tests use the standard library.
Run these from this directory:

```powershell
python -m unittest discover -s tests -v
python export_programs.py
python run_study.py --output results/my-run --events 20000 --repetitions 3
```

The recorded run is `results/development-002`; the aborted first attempt remains
in `results/development-001`. The agent pilot's instructions, negative controls,
submissions and judge logs are in `agent_pilot/`. Each submission must be judged
in a fresh CLI process, for example `python pilot_tools.py judge --cell ain_repair`.
The one-attempt submissions have already ended; rerunning a judge is a
reproduction check, not a fresh agent attempt. Figures can be regenerated with
`summarize_study.py` and `make_report.py` using optional Matplotlib dependencies.

Use a new output path: existing runs are never overwritten. Program examples
and the catalog are under `programs/`. The VM uses exact integers, strict JSON
and a typed validator before invoking capabilities. It does not execute Python
source from AIN programs. Fuel bounds VM instructions, not time inside a trusted
host call. It is a cooperative capability interface, not a hostile-code sandbox.

See [DEVELOPMENT_PROTOCOL.md](DEVELOPMENT_PROTOCOL.md) for the recorded scope and
[DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) for material failures and revisions.
Measurements include instrumentation overhead; no billed-token, monetary,
training or energy savings are inferred from source length or local timings.

Authorship: implemented and tested by OpenAI Codex and collaboration agents under
Izik Bachar's research direction. This is same-session engineering evidence.
