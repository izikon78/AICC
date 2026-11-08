"""Account for every recorded attempt in the frozen current-agent AIN pilot.

Normalized costs are hypothetical resource weights, never invoices. A missing
counter stays unknown. Reasoning-output tokens are retained, not added to output.
The primary denominator is a complete, genuine three-stage development chain.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MODES = ("python", "ir", "ain")
LABELS = {"python": "Python", "ir": "Readable IR", "ain": "Numeric AIN"}
STAGES = ("build", "change", "repair")
DELTAS = (30, 75)
COUNTERS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
WEIGHTS = {
    "primary": (0.1, 5), "cache_neutral": (1, 5),
    "output_1": (0.1, 1), "output_10": (0.1, 10),
    "cache_neutral_output_1": (1, 1), "cache_neutral_output_10": (1, 10),
}


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _counter(value):
    return type(value) is int and value >= 0


def _attempts(record):
    for kind in ("preparation_call", "task_call"):
        call = record.get(kind)
        if isinstance(call, dict):
            for attempt in call.get("attempts", []):
                yield kind, attempt


def _tools(attempt):
    value = attempt.get("tool_violations", [])
    return bool(value)


def _stage_passed(record):
    return bool(record.get("stage_passed") is True
                and record.get("preparation_passed") is True
                and record.get("fluency_passed") is True
                and record.get("judge", {}).get("passed") is True
                and not record.get("harness_failure")
                and not any(_tools(attempt) for _, attempt in _attempts(record)))


def _resources(records, assignments_complete, call_kinds=("preparation_call", "task_call")):
    attempts = [(kind, attempt) for record in records for kind, attempt in _attempts(record)
                if kind in call_kinds]
    totals = {key: 0 for key in COUNTERS}
    missing = {key: 0 for key in COUNTERS}
    issues = []
    elapsed = 0
    missing_elapsed = 0
    missing_calls = sum(not isinstance(record.get(kind), dict)
                        or not record[kind].get("attempts")
                        for record in records for kind in call_kinds)
    for index, (_, attempt) in enumerate(attempts):
        usage = attempt.get("usage")
        usage = usage if isinstance(usage, dict) else {}
        for key in COUNTERS:
            value = usage.get(key)
            if _counter(value):
                totals[key] += value
            else:
                missing[key] += 1
        if (_counter(usage.get("input_tokens")) and _counter(usage.get("cached_input_tokens"))
                and usage["cached_input_tokens"] > usage["input_tokens"]):
            issues.append(f"attempt {index}: cached input exceeds input")
        if _number(attempt.get("elapsed_seconds")):
            elapsed += attempt["elapsed_seconds"]
        else:
            missing_elapsed += 1
    complete = assignments_complete and not missing_calls and not issues and not any(missing.values())
    # Preserve known subtotals separately; a partly known total is never called complete.
    public_totals = {key: totals[key] if not missing[key] and not missing_calls
                     and assignments_complete else None for key in COUNTERS}
    costs = {key: None for key in WEIGHTS}
    for key, (cached, output) in WEIGHTS.items():
        needed = ("input_tokens", "output_tokens") if cached == 1 else (
            "input_tokens", "cached_input_tokens", "output_tokens")
        ready = (assignments_complete and not missing_calls
                 and not any(missing[field] for field in needed)
                 and (cached == 1 or not issues))
        if ready:
            costs[key] = (totals["input_tokens"] + output * totals["output_tokens"]
                          if cached == 1 else totals["input_tokens"]
                          - totals["cached_input_tokens"] + cached * totals["cached_input_tokens"]
                          + output * totals["output_tokens"])
    result = {
        "complete": complete, "attempts": len(attempts),
        "preparation_attempts": sum(kind == "preparation_call" for kind, _ in attempts),
        "task_attempts": sum(kind == "task_call" for kind, _ in attempts),
        "timeouts": sum(attempt.get("timed_out") is True for _, attempt in attempts),
        "tool_violating_attempts": sum(_tools(attempt) for _, attempt in attempts),
        "nonzero_exit_attempts": sum(attempt.get("exit_code") not in (None, 0)
                                     for _, attempt in attempts),
        "usage_totals": public_totals, "known_usage_subtotals": totals,
        "missing_counters_by_attempt": missing, "missing_calls": missing_calls,
        "elapsed_seconds": elapsed if not missing_elapsed and not missing_calls
                           and assignments_complete else None,
        "known_elapsed_subtotal_seconds": elapsed,
        "missing_elapsed_attempts": missing_elapsed, "issues": issues,
        "normalized_costs": costs,
        "costs_complete": {key: value is not None for key, value in costs.items()},
    }
    if len(call_kinds) == 2:
        result["by_call_kind"] = {kind: _resources(records, assignments_complete, (kind,))
                                  for kind in call_kinds}
    return result


def _harness_issues(record):
    judge = record.get("judge", {})
    issues = []
    if record.get("fallback"):
        issues.append("canonical fallback: no genuine primary-chain repair")
    if record.get("stage") == "repair" and not record.get("genuine_handoff"):
        issues.append("no verified genuine handoff")
    if any(case.get("oracle_manual_gate") is False for case in judge.get("details", [])):
        issues.append("oracle manual gate failed")
    if record.get("harness_failure"):
        issues.append("runner classified a harness failure")
    if judge.get("error") in {"JUDGE_TIMEOUT", "INVALID_JUDGE_OUTPUT", "ARTIFACT_LOAD_OR_JUDGE_ERROR"}:
        # The last category is intentionally ambiguous: malformed participant
        # artifacts and judge faults need inspection, rather than automatic blame.
        issues.append("judge error requires classification: " + judge["error"])
    return issues


def build_summary(run_dir):
    """Read manifest + stage records, returning only derived, serializable data."""
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    paths = sorted((run_dir / "stages").glob("*/stage.json"))
    records = []
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("mode") not in MODES:
            raise ValueError(f"Unknown mode in {path}: resource accounting would be incomplete")
        records.append(record)
    by_key = {}
    for record in records:
        key = (record["mode"], record.get("delta"), record.get("stage"))
        by_key.setdefault(key, []).append(record)
    expected = {(mode, delta, stage) for mode in MODES for delta in DELTAS for stage in STAGES}
    missing = sorted(expected - set(by_key))
    unexpected = sorted(set(by_key) - expected, key=str)
    duplicates = [key for key, items in by_key.items() if len(items) != 1]
    modes = {}
    for mode in MODES:
        selected = [record for record in records if record["mode"] == mode]
        mode_complete = (len(selected) == 6 and not any(key[0] == mode
                         for key in missing + unexpected + duplicates))
        resources = _resources(selected, mode_complete)
        chains = []
        for delta in DELTAS:
            chain_records = [by_key.get((mode, delta, stage), []) for stage in STAGES]
            unique = all(len(items) == 1 for items in chain_records)
            chain = [items[0] for items in chain_records] if unique else []
            successful = (unique and all(_stage_passed(record) for record in chain)
                          and not any(record.get("fallback") for record in chain)
                          and chain[-1].get("genuine_handoff") is True)
            chains.append({"delta": delta, "complete": unique,
                           "successful": successful,
                           "stage_successes": sum(_stage_passed(record) for record in chain),
                           "genuine_repair": bool(unique and chain[-1].get("genuine_handoff")),
                           "fallback": any(record.get("fallback") for record in chain)})
        successes = sum(chain["successful"] for chain in chains)
        costs = resources["normalized_costs"]
        modes[mode] = {
            "label": LABELS[mode], "assigned_chains": 2, "assigned_stages": 6,
            "observed_stages": len(selected), "assignments_complete": mode_complete,
            "preparation_passes": sum(record.get("preparation_passed") is True for record in selected),
            "fluency_passes": sum(record.get("fluency_passed") is True for record in selected),
            "functional_passes": sum(record.get("judge", {}).get("passed") is True for record in selected),
            "stage_passes": sum(_stage_passed(record) for record in selected),
            "diagnostic_repair_passes": sum(record.get("stage") == "repair"
                                            and record.get("judge", {}).get("passed") is True
                                            for record in selected),
            "fallback_stages": sum(bool(record.get("fallback")) for record in selected),
            "successful_chains": successes, "chains": chains, "resources": resources,
            "cost_per_assigned_stage": {key: value / 6 if value is not None else None
                                         for key, value in costs.items()},
            "cost_per_successful_chain": {key: value / successes
                                           if successes and value is not None else None
                                           for key, value in costs.items()},
        }
    comparisons = {}
    for baseline in ("python", "ir"):
        comparisons[baseline] = {}
        for weight in WEIGHTS:
            ain_cost = modes["ain"]["cost_per_successful_chain"][weight]
            base_cost = modes[baseline]["cost_per_successful_chain"][weight]
            comparisons[baseline][weight] = (1 - ain_cost / base_cost
                                             if ain_cost is not None and base_cost
                                             else None)
    stage_scores = [{"id": record.get("id"), "mode": record["mode"],
                     "delta": record.get("delta"), "stage": record.get("stage"),
                     "preparation_passed": record.get("preparation_passed"),
                     "fluency_passed": record.get("fluency_passed"),
                     "functional_passed": record.get("judge", {}).get("passed"),
                     "stage_passed": _stage_passed(record),
                     "genuine_handoff": record.get("genuine_handoff"),
                     "harness_failure": bool(record.get("harness_failure")),
                     "fallback": bool(record.get("fallback")),
                     "harness_notes": _harness_issues(record)} for record in records]
    return {
        "protocol": "AIN current-agent fluency pilot v1", "manifest": manifest,
        "scope": "In-context familiarity, not native model training; two paired workflow variants.",
        "cost_unit": "hypothetical normalized resource units; not dollars",
        "weights": {key: {"uncached_input": 1, "cached_input": cached, "output": output}
                    for key, (cached, output) in WEIGHTS.items()},
        "assigned_chains": 6, "assigned_stages": 18, "planned_calls": 36,
        "observed_stages": len(records), "missing_assignments": missing,
        "unexpected_assignments": unexpected, "duplicate_assignments": duplicates,
        "modes": modes, "ain_saving_fraction_per_successful_chain": comparisons,
        "stages": stage_scores,
    }


def _fmt(value, digits=1):
    return "undefined / incomplete" if value is None else f"{value:,.{digits}f}"


def _percent(value):
    return "undefined / incomplete" if value is None else f"{value * 100:+.1f}%"


def _charts(summary, run_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return [], "matplotlib unavailable; no figures generated"
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    figures = []
    labels = [LABELS[mode] for mode in MODES]
    colors = ["#52677F", "#2A8C82", "#BF652E"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")
    values = [summary["modes"][mode]["cost_per_assigned_stage"]["primary"] for mode in MODES]
    axes[0].bar(labels, [value or 0 for value in values], color=colors)
    axes[0].set_ylabel("Hypothetical normalized units / assigned stage")
    axes[0].set_title("All preparation, replay and failed attempts included")
    for i, value in enumerate(values):
        axes[0].annotate("incomplete" if value is None else f"{value:,.0f}",
                         (i, value or 0), xytext=(0, 4), textcoords="offset points", ha="center")
    success = [summary["modes"][mode]["successful_chains"] for mode in MODES]
    axes[1].bar(labels, success, color=colors)
    axes[1].set_ylim(0, 2.35); axes[1].set_yticks([0, 1, 2])
    axes[1].set_ylabel("Successful genuine chains / 2 assigned")
    axes[1].set_title("Build + change + genuine repair; all fluency gates")
    for i, value in enumerate(success):
        axes[1].text(i, value + .06, f"{value}/2", ha="center")
    fig.suptitle("Current-agent AIN pilot: resource use and correctness", fontsize=13)
    name = "resource-and-success.svg"; fig.savefig(run_dir / name); plt.close(fig); figures.append(name)

    fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
    names = ("output_1", "primary", "output_10")
    for mode, color in zip(MODES, colors):
        values = [summary["modes"][mode]["cost_per_successful_chain"][key] for key in names]
        if all(value is not None for value in values):
            ax.plot([1, 5, 10], values, marker="o", label=LABELS[mode], color=color)
        else:
            ax.plot([], [], label=LABELS[mode] + ": undefined / incomplete", color=color)
    ax.set_xlabel("Hypothetical output-token weight (input 1, cached input 0.1)")
    ax.set_ylabel("Hypothetical units / successful chain")
    ax.set_xticks([1, 5, 10]); ax.grid(alpha=.2); ax.legend()
    ax.set_title("Sensitivity; zero successful chains have no cost-per-success estimate")
    name = "cost-sensitivity.svg"; fig.savefig(run_dir / name); plt.close(fig); figures.append(name)
    return figures, None


def write_report(run_dir, charts=True):
    run_dir = Path(run_dir)
    summary = build_summary(run_dir)
    figures, chart_note = _charts(summary, run_dir) if charts else ([], "figures disabled")
    summary["figures"] = figures
    summary["chart_note"] = chart_note
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest = summary["manifest"]
    lines = ["# AIN current-agent fluency pilot: measured results", "",
             "This measures in-context preparation and controller development by a current agent. "
             "It does not test a model trained to know AIN natively. There are only two paired "
             "workflow variants per form; these are descriptive results, not population evidence.", "",
             f"Requested model: `{manifest.get('model', 'unrecorded')}`; effort: "
             f"`{manifest.get('effort', 'unrecorded')}`. Requested identity is not independent snapshot attestation.",
             f"Published plan: `{manifest.get('plan_commit', 'unrecorded')}`. Harness: "
             f"`{manifest.get('harness_commit', 'unrecorded')}`.", "",
             "## Correctness and denominators", "",
             "A primary chain needs all three stages, all preparation/fluency gates, hidden correctness, "
             "no participant tools, and a genuine predecessor-derived repair. Fallback repairs are diagnostics.", "",
             "| Form | Stages observed / assigned | Preparation passes | Functional passes | Full stage passes | Successful chains / assigned | Fallback stages |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for mode in MODES:
        row = summary["modes"][mode]
        lines.append(f"| {row['label']} | {row['observed_stages']}/6 | {row['preparation_passes']}/6 | "
                     f"{row['functional_passes']}/6 | {row['stage_passes']}/6 | {row['successful_chains']}/2 | {row['fallback_stages']} |")
    if summary["missing_assignments"] or summary["unexpected_assignments"] or summary["duplicate_assignments"]:
        lines += ["", "**Assignment inventory is incomplete or inconsistent.** See summary.json for missing, duplicate or unexpected records."]
    lines += ["", "## All-attempt resource accounting", "",
              "Every recorded preparation and task attempt is included, including retries, failures, "
              "timeouts and fallback work. Cached input is part of input. Reasoning output is displayed "
              "separately and is not added to output. Missing counters stay unknown; known subtotals "
              "remain available in summary.json but are not represented as complete totals.", "",
              "| Form | Prep / task attempts | Input | Cached input | Output | Reasoning output (not additive) | Seconds | Timeouts |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for mode in MODES:
        row = summary["modes"][mode]; resource = row["resources"]; tokens = resource["usage_totals"]
        lines.append(f"| {row['label']} | {resource['preparation_attempts']} / {resource['task_attempts']} | "
                     + " | ".join(_fmt(tokens[key], 0) for key in COUNTERS)
                     + f" | {_fmt(resource['elapsed_seconds'])} | {resource['timeouts']} |")
    lines += ["", "Preparation is measured separately below; its transcript is also replayed in the "
              "task call and that replay belongs to task input. Both call types remain in all totals.", "",
              "| Form | Preparation input / output | Task input / output | Preparation primary units | Task primary units |",
              "|---|---:|---:|---:|---:|"]
    for mode in MODES:
        row = summary["modes"][mode]
        prep = row["resources"]["by_call_kind"]["preparation_call"]
        task = row["resources"]["by_call_kind"]["task_call"]
        pair = lambda resource: " / ".join(_fmt(resource["usage_totals"][key], 0)
                                            for key in ("input_tokens", "output_tokens"))
        lines.append(f"| {row['label']} | {pair(prep)} | {pair(task)} | "
                     f"{_fmt(prep['normalized_costs']['primary'])} | {_fmt(task['normalized_costs']['primary'])} |")
    lines += ["", "## Hypothetical cost sensitivity", "",
              "These are normalized resource units, **not dollar charges or realized savings**. Primary "
              "weights are uncached input 1, cached input 0.1 and output 5. Cache-neutral uses all input "
              "at 1 and output at 5. Other output weights are sensitivity assumptions. Elapsed time "
              "includes service variability and does not measure compiler speed or isolated model compute.", "",
              "| Form | Total primary units | Units / assigned stage | Units / successful chain | Cache-neutral units / successful chain |",
              "|---|---:|---:|---:|---:|"]
    for mode in MODES:
        row = summary["modes"][mode]
        lines.append(f"| {row['label']} | {_fmt(row['resources']['normalized_costs']['primary'])} | "
                     f"{_fmt(row['cost_per_assigned_stage']['primary'])} | "
                     f"{_fmt(row['cost_per_successful_chain']['primary'])} | "
                     f"{_fmt(row['cost_per_successful_chain']['cache_neutral'])} |")
    lines += ["", "AIN saving per successful chain is `1 - (AIN total / AIN successes) / "
              "(baseline total / baseline successes)`. Zero successful chains gives an undefined "
              "estimate, never zero cost.", "",
              "| Baseline | Primary AIN saving | Cache-neutral | Output weight 1 | Output weight 10 |",
              "|---|---:|---:|---:|---:|"]
    for mode in ("python", "ir"):
        values = summary["ain_saving_fraction_per_successful_chain"][mode]
        lines.append(f"| {LABELS[mode]} | " + " | ".join(_percent(values[key]) for key in
                     ("primary", "cache_neutral", "output_1", "output_10")) + " |")
    lines += ["", "The frozen neutral prediction was 0% net saving versus readable IR; the optimistic "
              "10–20% scenarios were conditional assumptions, not confidence intervals. These observations "
              "do not estimate native-training savings or prove an internal reasoning mechanism.", ""]
    for name in figures:
        lines += [f"![{name.removesuffix('.svg').replace('-', ' ')}]({name})", ""]
    if chart_note:
        lines += [f"Figure status: {chart_note}.", ""]
    notes = [(record["id"], note) for record in summary["stages"] for note in record["harness_notes"]]
    if notes:
        lines += ["## Handoff and judge limitations", ""]
        lines += [f"- `{identifier}`: {note}." for identifier, note in notes]
        lines += [""]
    lines += ["## Stage inventory", "",
              "| ID | Preparation | Fluency | Hidden correctness | Full stage | Genuine handoff | Fallback |",
              "|---|---|---|---|---|---|---|"]
    for row in summary["stages"]:
        show = lambda value: "pass" if value is True else "fail" if value is False else "unknown"
        yes_no = lambda value: "yes" if value is True else "no" if value is False else "unknown"
        lines.append(f"| `{row['id']}` | " + " | ".join(show(row[key]) for key in
                     ("preparation_passed", "fluency_passed", "functional_passed", "stage_passed"))
                     + " | " + " | ".join(yes_no(row[key]) for key in ("genuine_handoff", "fallback")) + " |")
    lines += ["", "Raw stage records, exact responses, usage events and source artifacts accompany this "
              "report. Inspect ambiguous judge errors and unsupported mutation cases before attributing "
              "failure to a model. No significance test or population confidence interval is justified.", ""]
    (run_dir / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--no-charts", action="store_true")
    args = parser.parse_args()
    report = write_report(args.run_dir, charts=not args.no_charts)
    print(json.dumps({"summary": str(args.run_dir / "summary.json"),
                      "report": str(args.run_dir / "RESULTS.md"),
                      "figures": report["figures"]}))
