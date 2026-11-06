"""Post-hoc descriptive accounting for the completed amended AIN pilot.

This does not replace the frozen primary report. Missing attempts stay unknown.
Nonnegative resource costs permit lower cost bounds, and (with a complete
baseline and valid success denominators) upper bounds on hypothetical savings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MODES = ("python", "ir", "ain")
LABELS = {"python": "Python", "ir": "Readable IR", "ain": "Numeric AIN"}
STAGES = ("build", "change", "repair")
DELTAS = (30, 75)
COUNTERS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
WEIGHTS = {"primary": (0.1, 5), "cache_neutral": (1, 5),
           "output_1": (0.1, 1), "output_10": (0.1, 10)}


def _integer(value):
    return type(value) is int and value >= 0


def _attempts(record):
    for kind in ("preparation_call", "task_call"):
        call = record.get(kind)
        if not isinstance(call, dict) or not call.get("attempts"):
            raise ValueError(f"Missing assigned {kind} in {record.get('id')}")
        for attempt in call["attempts"]:
            yield kind, attempt


def _successful_chains(records):
    successes = 0
    for delta in DELTAS:
        chain = [next(record for record in records
                      if record["delta"] == delta and record["stage"] == stage)
                 for stage in STAGES]
        successful = all(record.get("stage_passed") is True
                         and record.get("preparation_passed") is True
                         and record.get("fluency_passed") is True
                         and record.get("judge", {}).get("passed") is True
                         and not record.get("fallback")
                         and not record.get("harness_failure")
                         and not any(attempt.get("tool_violations")
                                     for _, attempt in _attempts(record))
                         for record in chain)
        successes += bool(successful and chain[-1].get("genuine_handoff") is True)
    return successes


def _cost(usage, cached_weight, output_weight):
    """Return known full-attempt cost, conservative bound, and completeness.

    For a partial usage record enforce 0 <= cached <= input. If input alone is
    known, all of it might be cached; if cached alone is known, input is at least
    that value. This prevents an invalid bound from silently treating a missing
    cache category as zero. Whole missing records contribute a lower bound of 0,
    without declaring their actual usage zero.
    """
    usage = usage if isinstance(usage, dict) else {}
    inp = usage.get("input_tokens")
    cache = usage.get("cached_input_tokens")
    out = usage.get("output_tokens")
    inp, cache, out = (value if _integer(value) else None for value in (inp, cache, out))
    if inp is not None and cache is not None and cache > inp:
        raise ValueError("Cached input exceeds input; no trustworthy cost bound")
    needed = (inp, out) if cached_weight == 1 else (inp, cache, out)
    complete = all(value is not None for value in needed)
    output_bound = output_weight * out if out is not None else 0
    if cached_weight == 1:
        input_bound = inp if inp is not None else cache if cache is not None else 0
    elif inp is not None and cache is not None:
        input_bound = inp - cache + cached_weight * cache
    elif inp is not None:
        input_bound = cached_weight * inp
    elif cache is not None:
        input_bound = cached_weight * cache
    else:
        input_bound = 0
    lower = input_bound + output_bound
    return {"complete": complete, "known_metered_subtotal": lower if complete else 0,
            "lower_bound": lower}


def analyze(run_dir):
    """Read a completed amended dataset; do not write or invoke any model."""
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "complete_amended_continuation":
        raise ValueError("Post-hoc analysis requires status complete_amended_continuation")
    records = [json.loads(path.read_text(encoding="utf-8"))
               for path in sorted((run_dir / "stages").glob("*/stage.json"))]
    keys = [(record.get("mode"), record.get("delta"), record.get("stage")) for record in records]
    expected = {(mode, delta, stage) for mode in MODES for delta in DELTAS for stage in STAGES}
    if len(keys) != 18 or len(set(keys)) != 18 or set(keys) != expected:
        raise ValueError("All 18 unique frozen assignments are required; no selected subset")
    modes = {}
    for mode in MODES:
        selected = [record for record in records if record["mode"] == mode]
        attempts = [(kind, attempt) for record in selected for kind, attempt in _attempts(record)]
        totals = {key: 0 for key in COUNTERS}
        missing = {key: 0 for key in COUNTERS}
        wholly_missing = 0
        for _, attempt in attempts:
            usage = attempt.get("usage")
            usage = usage if isinstance(usage, dict) else {}
            wholly_missing += not any(_integer(usage.get(key)) for key in COUNTERS)
            for key in COUNTERS:
                value = usage.get(key)
                if _integer(value):
                    totals[key] += value
                else:
                    missing[key] += 1
        costs = {}
        successes = _successful_chains(selected)
        for name, (cached, output) in WEIGHTS.items():
            values = [_cost(attempt.get("usage"), cached, output) for _, attempt in attempts]
            complete = all(value["complete"] for value in values)
            subtotal = sum(value["known_metered_subtotal"] for value in values)
            lower = sum(value["lower_bound"] for value in values)
            costs[name] = {"complete": complete, "exact_total": lower if complete else None,
                           "known_metered_subtotal": subtotal, "cost_lower_bound": lower,
                           "incompletely_metered_attempts": sum(not value["complete"] for value in values),
                           "exact_cost_per_successful_chain": lower / successes
                           if complete and successes else None,
                           "cost_per_successful_chain_lower_bound": lower / successes
                           if successes else None,
                           "exact_cost_per_assigned_stage": lower / 6 if complete else None,
                           "cost_per_assigned_stage_lower_bound": lower / 6}
        modes[mode] = {"label": LABELS[mode], "assigned_chains": 2,
                       "assigned_stages": 6,
                       "functional_stage_passes": sum(record.get("judge", {}).get("passed") is True
                                                       for record in selected),
                       "full_stage_passes": sum(record.get("stage_passed") is True for record in selected),
                       "fallback_stages": sum(bool(record.get("fallback")) for record in selected),
                       "successful_chains": successes, "attempts": len(attempts),
                       "preparation_attempts": sum(kind == "preparation_call" for kind, _ in attempts),
                       "task_attempts": sum(kind == "task_call" for kind, _ in attempts),
                       "wholly_unmetered_attempts": wholly_missing,
                       "known_token_subtotals": totals, "missing_category_attempts": missing,
                       "exact_token_totals": {key: totals[key] if not missing[key] else None
                                              for key in COUNTERS},
                       "costs": costs}
    bounds = {}
    assigned_bounds = {}
    for baseline in ("python", "ir"):
        bounds[baseline] = {}
        assigned_bounds[baseline] = {}
        for weight in WEIGHTS:
            ain_lower = modes["ain"]["costs"][weight]["cost_per_successful_chain_lower_bound"]
            base_exact = modes[baseline]["costs"][weight]["exact_cost_per_successful_chain"]
            upper = 1 - ain_lower / base_exact if ain_lower is not None and base_exact else None
            bounds[baseline][weight] = {
                "savings_upper_bound_fraction": upper,
                "point_savings_estimate": None,
                "reason_if_undefined": None if upper is not None else
                "A complete positive-cost baseline and positive successful-chain denominators are required."}
            ain_assigned = modes["ain"]["costs"][weight]["cost_per_assigned_stage_lower_bound"]
            base_assigned = modes[baseline]["costs"][weight]["exact_cost_per_assigned_stage"]
            assigned_upper = 1 - ain_assigned / base_assigned if base_assigned else None
            assigned_bounds[baseline][weight] = {
                "savings_upper_bound_fraction": assigned_upper, "point_savings_estimate": None,
                "denominator": "all 6 assigned stages per form; not adjusted for successful chains"}
    return {"analysis_type": "Post-hoc descriptive known-usage accounting and mathematical bounds",
            "primary_report_replaced": False, "dataset_status": manifest["status"],
            "plan_commit": manifest.get("plan_commit"), "harness_commit": manifest.get("harness_commit"),
            "continuation_commit": manifest.get("continuation_commit"),
            "cost_unit": "Hypothetical normalized resource units, not dollars",
            "weights": {key: {"uncached_input": 1, "cached_input": cached, "output": output}
                        for key, (cached, output) in WEIGHTS.items()},
            "modes": modes, "ain_savings_upper_bounds_per_primary_chain": bounds,
            "ain_savings_upper_bounds_per_assigned_stage": assigned_bounds,
            "limits": [
                "Missing request usage stays unknown; a known subtotal is not an all-attempt point estimate.",
                "Bounds assume all omitted resource costs are nonnegative and cached input is a subset of input.",
                "A positive savings upper bound does not establish any saving; actual saving may be lower or negative.",
                "These are hypothetical token weights, not invoices or realized dollar savings.",
                "The resumed dataset reuses original observations and includes a multi-hour service break.",
                "A fallback can make a primary chain ineligible because of mutator support, even when every model submission is correct.",
                "Only two paired workflow variants per form; no significance claim or native-training conclusion."]}


def _fmt(value):
    return "undefined" if value is None else f"{value:,.1f}"


def _percent(value):
    return "undefined" if value is None else f"{value * 100:+.1f}%"


def _charts(result, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 11, "svg.fonttype": "none"})
    colors = ["#52677F", "#2A8C82", "#BF652E"]
    labels = [LABELS[mode] for mode in MODES]
    fig, ax = plt.subplots(figsize=(9, 5.4), layout="constrained")
    values = [result["modes"][mode]["costs"]["primary"]["cost_lower_bound"] for mode in MODES]
    bars = ax.bar(labels, values, color=colors, edgecolor="#333333", linewidth=.8)
    top = max(values) or 1
    ax.set_ylim(0, top * 1.32)
    for index, mode in enumerate(MODES):
        cost = result["modes"][mode]["costs"]["primary"]
        missing = cost["incompletely_metered_attempts"]
        text = f"{values[index]:,.0f}"
        if not cost["complete"]:
            bars[index].set_hatch("///")
            text = f"≥ {text}\n+{missing} unmetered requests; lower bound"
        else:
            text += "\ncomplete measured counters"
        ax.annotate(text, (index, values[index]), xytext=(0, 7),
                    textcoords="offset points", ha="center", fontsize=10)
    ax.set_ylabel("Hypothetical normalized units; all known attempts")
    ax.set_title("Known resource cost: incomplete AIN total can only be bounded")
    fig.supxlabel("Input 1, cached input 0.1, output 5; not dollar charges", fontsize=10)
    figures = []
    for extension in ("svg", "png"):
        name = "known-normalized-cost." + extension
        fig.savefig(output / name, dpi=180); figures.append(name)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5.2), layout="constrained")
    for ax, key, title in zip(axes, ("input_tokens", "output_tokens"),
                              ("Input tokens (including cached subset)", "Output tokens")):
        values = [result["modes"][mode]["known_token_subtotals"][key] for mode in MODES]
        bars = ax.bar(labels, values, color=colors, edgecolor="#333333", linewidth=.8)
        ax.set_ylim(0, (max(values) or 1) * 1.23)
        for i, mode in enumerate(MODES):
            unknown = result["modes"][mode]["missing_category_attempts"][key]
            if unknown: bars[i].set_hatch("///")
            ax.annotate(("≥ " if unknown else "") + f"{values[i]:,}", (i, values[i]),
                        xytext=(0, 5), textcoords="offset points", ha="center", fontsize=10)
        ax.set_title(title); ax.set_ylabel("Known token subtotal")
    fig.suptitle("All preparation and task attempts with reported usage", fontsize=13)
    fig.supxlabel("Hatched bars omit unknown request usage; reasoning output is not added to output", fontsize=10)
    for extension in ("svg", "png"):
        name = "known-token-counts." + extension
        fig.savefig(output / name, dpi=180); figures.append(name)
    plt.close(fig)
    return figures


def write_analysis(run_dir, output=None, charts=True):
    result = analyze(run_dir)
    output = Path(output) if output is not None else Path(run_dir) / "analysis"
    output.mkdir(parents=True, exist_ok=True)
    figures = _charts(result, output) if charts else []
    result["figures"] = figures
    (output / "known-usage.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    ain = result["modes"]["ain"]
    lines = ["# Known usage and bounds: post-hoc descriptive analysis", "",
             "This is a secondary analysis of the completed amended continuation. The original "
             "primary report stays intact. Its all-attempt AIN cost and exact savings remain undefined "
             "where request usage is missing. Known calls provide useful measurements without "
             "turning unknown counters into zero.", "",
             f"AIN has {ain['wholly_unmetered_attempts']} wholly unmetered request(s). "
             "All known preparation and task attempts, including any metered failures, are included. "
             "Original copied observations are counted once; this continuation is not a replication.", "",
             "| Form | Attempts | Unmetered requests | Known input | Known cached input | Known output |",
             "|---|---:|---:|---:|---:|---:|"]
    for mode in MODES:
        row = result["modes"][mode]; tokens = row["known_token_subtotals"]
        lines.append(f"| {row['label']} | {row['attempts']} | {row['wholly_unmetered_attempts']} | "
                     f"{tokens['input_tokens']:,} | {tokens['cached_input_tokens']:,} | {tokens['output_tokens']:,} |")
    lines += ["", "Correctness and primary-chain eligibility are separate outcomes. A canonical fallback "
              "caused by an unsupported mutation layout is a harness limitation; it does not establish "
              "an incorrect model submission. The primary chain rule still excludes such a chain.", "",
              "| Form | Hidden functional stage passes / 6 | Full stage passes / 6 | Genuine primary chains / 2 | Fallback stages |",
              "|---|---:|---:|---:|---:|"]
    for mode in MODES:
        row = result["modes"][mode]
        lines.append(f"| {row['label']} | {row['functional_stage_passes']}/6 | {row['full_stage_passes']}/6 | "
                     f"{row['successful_chains']}/2 | {row['fallback_stages']} |")
    lines += ["", "Input includes its cached subset. Output and reasoning-output counters are preserved "
              "separately; reasoning is not added to output. Token counts with missing requests are "
              "known subtotals, not complete totals.", "",
              "## Cost lower bounds", "",
              "All weights below are hypothetical normalized resource units, not invoices or dollar "
              "savings. The primary weights are uncached input 1, cached input 0.1 and output 5. "
              "Cache-neutral uses all input at 1; the output sensitivity rows use cached input 0.1.", "",
              "| Weights | Python exact total | Readable IR exact total | AIN known metered subtotal | AIN cost lower bound | AIN exact total |",
              "|---|---:|---:|---:|---:|---:|"]
    for weight in WEIGHTS:
        py = result["modes"]["python"]["costs"][weight]
        ir = result["modes"]["ir"]["costs"][weight]
        cost = ain["costs"][weight]
        lines.append(f"| {weight} | {_fmt(py['exact_total'])} | {_fmt(ir['exact_total'])} | "
                     f"{_fmt(cost['known_metered_subtotal'])} | ≥ {_fmt(cost['cost_lower_bound'])} | {_fmt(cost['exact_total'])} |")
    lines += ["", "The lower bound assumes omitted costs are nonnegative. It says actual AIN resource "
              "cost cannot be below the shown amount; it may be higher. With only wholly missing "
              "records, the known metered subtotal and lower bound coincide. Partial category records "
              "use conservative bounds that respect cached input being a subset of input.", "",
              "## Resource-saving upper bounds per assigned stage", "",
              "For a baseline with complete cost, `1 - (AIN cost lower bound / 6 assigned stages) / "
              "(baseline exact cost / 6 assigned stages)` is an upper bound on hypothetical resource "
              "saving per assigned stage. This descriptive comparison includes every assigned stage "
              "and is **not the success-adjusted primary savings outcome**. A positive bound does not show that any "
              "saving occurred. A negative bound rules out positive saving under those weights and "
              "denominators.", "",
              "| Baseline | Primary upper bound | Cache-neutral upper bound | Output weight 1 | Output weight 10 |",
              "|---|---:|---:|---:|---:|"]
    for baseline in ("python", "ir"):
        values = result["ain_savings_upper_bounds_per_assigned_stage"][baseline]
        lines.append(f"| {LABELS[baseline]} | " + " | ".join(
            "≤ " + _percent(values[weight]["savings_upper_bound_fraction"])
            if values[weight]["savings_upper_bound_fraction"] is not None else "undefined"
            for weight in WEIGHTS) + " |")
    lines += ["", "The JSON also retains the mathematical upper bound per eligible primary chain. "
              "That bound is undefined with zero successful chains. Primary-chain eligibility includes "
              "a predecessor-mutation requirement, so a harness-induced fallback can change its "
              "denominator even with correct model code. It should not be read as a pure model-cost penalty.", "",
              "For the article: this pilot can demonstrate whether a current agent can build, "
              "change and repair a substantial controller in AIN after supplied preparation, and "
              "can describe the resources of recorded calls. Missing measurements prevent an exact "
              "all-attempt saving claim. The experiment does not train AIN into model weights or "
              "measure a native-language reasoning mechanism.", ""]
    for name in figures:
        if name.endswith(".svg"):
            lines += [f"![{name.removesuffix('.svg').replace('-', ' ')}]({name})", ""]
    lines += ["## Limits", ""] + ["- " + limit for limit in result["limits"]] + [""]
    (output / "KNOWN_USAGE.md").write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-charts", action="store_true")
    args = parser.parse_args()
    result = write_analysis(args.run_dir, args.output, charts=not args.no_charts)
    print(json.dumps({"output": str(args.output or args.run_dir / "analysis"),
                      "figures": result["figures"], "post_hoc": True}))
