# Start here for an independent reproduction

This package lets an AI agent recreate the approved-core workflow theory test
from a fresh checkout. Prior AIN knowledge is unnecessary. It supports an exact
rerun of the reference implementation and an independent reconstruction of the
accounting from the published specification and semantic trace inputs.

Begin with [AIN_LANGUAGE_AND_THEORY.md](AIN_LANGUAGE_AND_THEORY.md) for the
language theory, abstract program structure, function/loop reuse and links to
the implemented prototype's concrete syntax. Then follow this guide and
`REPLICATION_SPEC.md` for the current test.

AIN means **AI Native Language**, the working name for Izik Bachar's proposed
machine-oriented programming representation. The central idea is that agents
could learn a concise executable representation before using it on tasks. AICC
means **AI Computational Commons**, the related architecture for sharing approved
reusable capabilities. Every condition here receives the same approved core.

The user asked us to assume that a short, optimized AIN and fully approved core
code already exist. The test takes fluent knowledge and core approval as premises.
It also supplies correct composition plans, holding planning correctness fixed
so that resource accounting can be examined directly. Executing the plans checks
the behavior of the accounting examples.

## What the test contains

There are eighteen chains across three domains, with six parameter/data variants
per domain. Each chain has build, change, repair and fresh-context handoff stages.
The seventy-two stages compose approved functions for event processing,
versioned cache resolution and simulated publication/retry. The core contains
real functions, `for` loops and a bounded `while` loop. Every pipeline composes
five generic capabilities.

Build creates a composition. Change patches one argument. Repair fixes one
injected defect. Handoff reuses the stored artifact and memory. Each stage records
working information, checks execution, persists memory and submits a result.
Independent fixture oracles check the outputs. There are 216 logical agent
requests per data schedule, with three requests per stage.

The resident-data schedule keeps business records in host storage and gives the
agent a handle. The inspect-data schedule also includes records in the agent's
context. Reprocessed task context, previous artifacts, memory, actions and tool
observations are charged each time they appear in a request.

Practical Python counts use the pinned Qwen text tokenizer for approved calls,
with both descriptive names and fixed short aliases. Ideal AIN uses a declared
65,536-entry accounting vocabulary, learned operation references and explicit
operand charges. Ideal IR and ideal Python receive the same semantic interface.
Totals combine common input text and ideal code units under equal cost per
position. The run performs CPU execution and tokenization, with zero model
inference calls.

## Get the package and create an environment

Clone the package branch and record the exact revision.

```text
git clone --branch research/approved-core-replication --single-branch https://github.com/izikon78/AICC.git
cd AICC
git rev-parse HEAD
```

Use Python 3.12 and the pinned CPU dependencies in `requirements-reproduce.txt`.
The initial setup downloads tokenizer files for `Qwen/Qwen2.5-1.5B` at revision
`8faed761d45a263340a0528343f099c05c9a4323` when absent from the cache.

On Windows in PowerShell,

```powershell
python -m venv work/.venv-reproduce
& .\work\.venv-reproduce\Scripts\python.exe -m pip install -r experiments\approved_workflow_theory\requirements-reproduce.txt
```

On Linux or macOS,

```bash
python3.12 -m venv work/.venv-reproduce
work/.venv-reproduce/bin/python -m pip install -r experiments/approved_workflow_theory/requirements-reproduce.txt
```

Before independent reconstruction, fetch and verify just the tokenizer assets.
This preparation step leaves the reference accounting and totals unopened.

```text
PATH_TO_ENV_PYTHON experiments/approved_workflow_theory/reproduce.py --prepare-tokenizer
```

Use the environment's Python executable from the setup commands above.

## Independent reconstruction

This mode is intended for an agent's independent article review. Start with this
file, then read [REPLICATION_SPEC.md](REPLICATION_SPEC.md) and the supplied
`trace-inputs.json`. Implement the frozen accounting, Python rendering and
per-request history recurrence in a new directory. Use the published semantic
inputs and pinned tokenizer. Keep the implementation independent of the
reference `accounting.py`, `run.py` and `report.py`.

Produce and preserve your own ledgers before opening the reference aggregate
tables or running the reference pipeline. Record your implementation hash,
environment and input hashes. Then compare your result with the reference files
under `results/approved-core-2026-11-06/`. Report the earliest differing field
when counts disagree. Preserve discrepancies as evidence and explain their cause.
Any accounting change belongs in a separately versioned extension.

Reference numbers and code are public. This workflow provides an auditable order
of work and avoids tuning an implementation to expected totals. Your report
should disclose which reference materials you consulted before implementation.

A separate-agent validation archive is provided under
`validation/codex-independent-2026-11-06/`. Consult it after preserving your own
initial implementation and ledger, together with the other reference evidence.

After preserving the independent results, use
[ARTICLE_REPRODUCTION_BRIEF.md](ARTICLE_REPRODUCTION_BRIEF.md) for the original
aggregate observations and the article's intended claim. Review
[README.md](README.md), [workloads.py](workloads.py), [accounting.py](accounting.py)
and [run.py](run.py) to explain implementation differences.

## Exact reference rerun

This mode verifies that the published reference implementation runs correctly in
your environment. Use a fresh output directory for every attempt.

On Windows,

```powershell
& .\work\.venv-reproduce\Scripts\python.exe experiments\approved_workflow_theory\reproduce.py --output work\approved-workflow-replication\agent-name
```

On Linux or macOS,

```bash
work/.venv-reproduce/bin/python experiments/approved_workflow_theory/reproduce.py --output work/approved-workflow-replication/agent-name
```

Replace `agent-name` with a unique run name. The command prepares the pinned
tokenizer, runs checks, creates fresh observations, generates a report and writes
`comparison.json`. The deterministic comparison covers raw observations and
counts, with source paths normalized across platforms. Host timings are retained
separately. After the tokenizer is cached, `--offline` uses cached tokenizer files.

Preserve failed attempts and investigate the recorded reason before using a new
output directory. Report the exact Git commit, Python and package versions,
tokenizer revision, source/fixture hashes, check outcome, comparison outcome and
every deviation. Keep raw files with the independent report.

## Pasteable task for a new agent

```text
Recreate the approved-core workflow theory test in this repository for an
independent article review. Begin with
experiments/approved_workflow_theory/AGENT_START_HERE.md. Assume I have provided
no other background about AIN. Read the premises before measuring anything.

Use independent reconstruction mode first. Read REPLICATION_SPEC.md and the
published semantic trace-inputs.json. Implement your own counter and renderer in
a new directory using the pinned tokenizer. Keep your implementation independent
of reference accounting.py, run.py and report.py. Preserve your code hash and
own per-request ledgers before opening expected aggregate tables or executing
the reference pipeline. Disclose any reference materials seen before this point.

Then compare your exact integer counts with the published reference, explain
the earliest discrepancy and retain your original results. Use the exact-rerun
wrapper afterward to check environment compatibility. Give the Git revision,
environment, input/source hashes, tests, comparison outcome and raw files in your
report. Clearly distinguish measured Python text tokens from assumed ideal code
units, and state the equal-position-cost and perfect-composition assumptions.

After exact reproduction, assess the assumptions. Put changes to vocabulary,
workloads, framing, tokenizer or model-based evaluation in a separate version.
Deliver your independent report and fresh raw observations for article comparison.
```
