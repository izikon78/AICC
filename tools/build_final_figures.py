"""Build the final publication figures from the frozen chart-data snapshot.

All quantitative inputs retain their verified primary-source identities.
The conceptual architecture figure is explicitly proposed and has no measurements.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "publication/figures"
ARMS = ("python", "ir", "ain")
NAVY = "#1B4965"
TEAL = "#007F7A"
GRAY = "#BFC8CE"
INK = "#202020"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources(data):
    for relative, expected in data["source_sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"Frozen chart source differs at {relative}")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prepare_style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 9,
        "axes.labelsize": 9, "axes.titlesize": 9.5,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.fontsize": 9, "text.color": INK,
        "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#777777", "axes.linewidth": 0.6,
        "svg.fonttype": "none", "svg.hashsalt": "aicc-final",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    })
    return matplotlib, plt


def grid(axis):
    axis.set_axisbelow(True)
    axis.grid(axis="y", color="#E2E5E7", linewidth=0.6)
    axis.tick_params(length=3, width=0.6)


def save_figure(figure, output, name, description):
    figure.savefig(output / f"{name}.png", dpi=300,
                   metadata={"Description": description})
    figure.savefig(output / f"{name}.svg",
                   metadata={"Date": None, "Creator": "AICC final publication figure builder", "Description": description})
    svg_path = output / f"{name}.svg"
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(
        encoding="utf-8").splitlines()) + "\n", encoding="utf-8", newline="\n")


def processing_figure(data, output, plt):
    rows = []
    figure, axis = plt.subplots(figsize=(6.5, 3.35))
    figure.subplots_adjust(left=0.13, right=0.98, bottom=0.23, top=0.81)
    modes = (("reference", "Reference", GRAY), ("static", "Ordinary optimized", NAVY),
             ("aicc_static", "Same code via AICC", TEAL))
    for offset, (mode, label, color) in enumerate(modes):
        values = []
        for record in data["processing"]:
            medians = record["per_job_mode_medians"]
            baseline = sum(row["pipeline_seconds"] for row in medians if row["mode"] == "reference")
            candidate = sum(row["pipeline_seconds"] for row in medians if row["mode"] == mode)
            value = 100 * candidate / baseline
            values.append(value)
            rows.append({"record": record["agent_record"], "host": record["reported_host"],
                         "mode": mode, "sum_pipeline_medians_seconds": candidate,
                         "within_host_reference_percent": value})
        positions = [index + (offset - 1) * 0.24 for index in range(3)]
        bars = axis.bar(positions, values, width=0.22, color=color, label=label)
        for bar, value in zip(bars, values, strict=True):
            axis.text(bar.get_x() + bar.get_width() / 2, value + 2, f"{value:.1f}",
                      ha="center", va="bottom", fontsize=9)
    axis.set_ylim(0, 115)
    axis.set_yticks((0, 25, 50, 75, 100))
    axis.set_ylabel("Pipeline cost (% of host reference)")
    axis.set_xticks(range(3), ("Original record\nWindows 11", "Claude record\nLinux", "Grok record\nWindows 10"))
    axis.legend(loc="lower center", bbox_to_anchor=(0.48, 1.03), ncol=3, frameon=False,
                handlelength=1.2, columnspacing=1.1)
    grid(axis)
    figure.text(0.13, 0.025, "Within-host normalization; three workload medians with equal job weight.", fontsize=9)
    save_figure(figure, output, "processing-cost", data["measurement_boundaries"]["processing"])
    plt.close(figure)
    write_csv(output / "processing-cost.csv", rows)


def memory_figure(data, output, plt):
    rows = []
    figure, axes = plt.subplots(1, 3, figsize=(6.5, 3.45), sharey=True)
    figure.subplots_adjust(left=0.12, right=0.98, bottom=0.28, top=0.77, wspace=0.16)
    jobs = ("repeated-shuffled", "diverse-shuffled", "ordered-stream")
    titles = ("Original / Windows 11", "Claude / Linux", "Grok / Windows 10")
    for axis, record, title in zip(axes, data["processing"], titles, strict=True):
        medians = {(row["job"], row["mode"]): row for row in record["per_job_mode_medians"]}
        for offset, (mode, label, color) in enumerate((("static", "Ordinary optimized", NAVY),
                                                      ("aicc_static", "Same code via AICC", TEAL))):
            values = []
            for job in jobs:
                reference = medians[job, "reference"]["peak_mib"]
                candidate = medians[job, mode]["peak_mib"]
                values.append(100 * candidate / reference)
                rows.append({"record": record["agent_record"], "host": record["reported_host"],
                             "job": job, "mode": mode, "reference_peak_mib": reference,
                             "candidate_peak_mib": candidate, "reference_percent": values[-1]})
            axis.bar([index + (offset - 0.5) * 0.34 for index in range(3)], values,
                     width=0.31, color=color, label=label)
        axis.axhline(100, color="#777777", linewidth=0.8, linestyle="--")
        axis.set_title(title, pad=8)
        axis.set_xticks(range(3), ("Repeated", "Diverse", "Ordered"), rotation=35, ha="right")
        axis.set_ylim(0, 108)
        axis.set_yticks((0, 25, 50, 75, 100))
        grid(axis)
    axes[0].set_ylabel("Peak process memory (% of reference)")
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.56, 1.0),
                  frameon=False, ncol=2)
    figure.text(0.12, 0.035, "Each host and workload has its own 100% reference. OS peak accounting differs.", fontsize=9)
    save_figure(figure, output, "memory-cost", data["measurement_boundaries"]["memory"])
    plt.close(figure)
    write_csv(output / "memory-cost.csv", rows)


def adaptation_figure(data, output, plt):
    rows = []
    figure, axis = plt.subplots(figsize=(6.5, 3.45))
    figure.subplots_adjust(left=0.12, right=0.98, bottom=0.21, top=0.78)
    conditions = (("full_format", "Full-format adaptation", GRAY),
                  ("compact_native", "Compact adaptation + native backend", TEAL))
    for offset, (condition, label, color) in enumerate(conditions):
        record = data["adaptation"][condition]
        values = [record["arms"][arm]["correct"] for arm in ARMS]
        positions = [index + (offset - 0.5) * 0.34 for index in range(3)]
        bars = axis.bar(positions, values, width=0.31, color=color, label=label)
        for arm, bar, value in zip(ARMS, bars, values, strict=True):
            assigned = record["arms"][arm]["assigned"]
            axis.text(bar.get_x() + bar.get_width() / 2, value + 0.6,
                      f"{value}/{assigned}", ha="center", fontsize=9)
            rows.append({"condition": condition, "arm": arm,
                         **record["arms"][arm],
                         "evaluation_stage_cap_seconds": record["config"]["eval_seconds_per_stage"],
                         "output_cap_tokens": record["config"]["max_new_tokens"]})
    axis.set_ylim(0, 28)
    axis.set_yticks((0, 6, 12, 18, 24))
    axis.set_xticks(range(3), ("Python", "Readable IR", "Numeric AIN"))
    axis.set_ylabel("Correct tasks (out of 24 assigned)")
    axis.legend(loc="lower center", bbox_to_anchor=(0.47, 1.02), frameon=False, ncol=1)
    grid(axis)
    figure.text(0.12, 0.035, "Full: 90 s / 320 output cap. Compact: 120 s / 64. Reused arithmetic cases.", fontsize=9)
    save_figure(figure, output, "adaptation-correctness", data["measurement_boundaries"]["adaptation"])
    plt.close(figure)
    write_csv(output / "adaptation-correctness.csv", rows)


def theory_figure(data, output, plt):
    from matplotlib.ticker import FuncFormatter

    rows = []
    figure, axis = plt.subplots(figsize=(6.5, 3.5))
    figure.subplots_adjust(left=0.13, right=0.98, bottom=0.25, top=0.81)
    schedules = ("resident", "inspect")
    for offset, (key, label, color) in enumerate((("python_total", "Short-alias Python text", NAVY),
                                                 ("ideal_total", "Ideal AIN / IR / Python", TEAL))):
        values = [data["theory"][schedule][key] for schedule in schedules]
        positions = [index + (offset - 0.5) * 0.3 for index in range(2)]
        bars = axis.bar(positions, values, width=0.27, color=color, label=label)
        for schedule, bar, value in zip(schedules, bars, values, strict=True):
            axis.text(bar.get_x() + bar.get_width() / 2, value + 1500,
                      f"{value:,}", ha="center", fontsize=9)
            rows.append({"schedule": schedule, "profile": key, "total_positions": value,
                         "ideal_reduction_fraction": data["theory"][schedule]["reduction_fraction"]})
    for index, schedule in enumerate(schedules):
        record = data["theory"][schedule]
        axis.text(index, record["python_total"] + 7500,
                  f"{record['reduction_fraction']:.1%} lower", ha="center", fontsize=9)
    axis.set_ylim(0, 90000)
    axis.set_yticks((0, 20000, 40000, 60000, 80000))
    axis.yaxis.set_major_formatter(FuncFormatter(lambda value, position: f"{value / 1000:.0f}"))
    axis.set_ylabel("Counted positions (thousands)")
    axis.set_xticks(range(2), ("Resident data / handle", "Records included in context"))
    axis.legend(loc="lower center", bbox_to_anchor=(0.45, 1.02), ncol=2, frameon=False,
                handlelength=1.2, columnspacing=1.2)
    grid(axis)
    figure.text(0.13, 0.075, "Measured text tokens + modeled code units; equal cost per position assumed.", fontsize=9)
    figure.text(0.13, 0.025, "Premises include fluent language, approved core and supplied correct composition.", fontsize=9)
    save_figure(figure, output, "approved-core-demand", data["measurement_boundaries"]["theory"])
    plt.close(figure)
    write_csv(output / "approved-core-demand.csv", rows)


def architecture_figure(output, plt):
    from matplotlib.path import Path as DrawingPath
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    figure, axis = plt.subplots(figsize=(6.5, 4.65))
    figure.subplots_adjust(left=0.025, right=0.975, bottom=0.01, top=0.99)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    fills = {"agent": "#DCEAF2", "host": "#DDF2EF", "data": "#EEF1F3"}

    def box(x, y, title, detail, layer, height=0.145):
        axis.add_patch(FancyBboxPatch((x, y), 0.27, height,
                       boxstyle="round,pad=0.008,rounding_size=0.012",
                       facecolor=fills[layer], edgecolor="#637580", linewidth=0.8))
        axis.text(x + 0.135, y + height - 0.034, title, ha="center", va="center",
                  fontsize=10, fontweight="bold")
        axis.text(x + 0.135, y + 0.052, detail, ha="center", va="center",
                  fontsize=9, linespacing=1.3)

    def arrow(start, end, color="#4B606C"):
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                       mutation_scale=11, linewidth=1, color=color))

    def routed_arrow(vertices, dashed=False):
        path = DrawingPath(vertices, [DrawingPath.MOVETO] +
                           [DrawingPath.LINETO] * (len(vertices) - 1))
        axis.add_patch(FancyArrowPatch(path=path, arrowstyle="-|>",
                       mutation_scale=11, linewidth=1, color="#637580",
                       linestyle="--" if dashed else "-"))

    axis.text(0.5, 0.965, "AIN / AICC workflow", ha="center", fontsize=12,
              fontweight="bold")
    axis.text(0.5, 0.919, "Proposed learned representation and governed execution",
              ha="center", fontsize=9.5)
    box(0.035, 0.72, "Task + saved record", "requirements / parameters\nprior artifact and memory", "data")
    box(0.36, 0.72, "Learned agent", "fluent AIN representation\nselect / compose / revise", "agent")
    box(0.685, 0.72, "Executable record", "program + tool actions\nworking memory", "agent")
    box(0.685, 0.395, "Host binding", "contract, version, authority\nresource obligations", "host")
    box(0.36, 0.395, "Approved execution", "shared implementation\ncompiler / native backend", "host")
    box(0.035, 0.395, "Observations", "results, errors and state\nreturned to the agent", "data")
    arrow((0.313, 0.79), (0.352, 0.79))
    arrow((0.638, 0.79), (0.677, 0.79))
    arrow((0.82, 0.712), (0.82, 0.548))
    arrow((0.677, 0.465), (0.638, 0.465))
    arrow((0.352, 0.465), (0.313, 0.465))
    routed_arrow([(0.17, 0.548), (0.17, 0.625), (0.495, 0.625), (0.495, 0.712)])
    axis.text(0.315, 0.643, "feedback", ha="center", fontsize=9)
    axis.add_patch(FancyBboxPatch((0.343, 0.37), 0.63, 0.207,
                   boxstyle="round,pad=0.008,rounding_size=0.012", fill=False,
                   edgecolor=TEAL, linewidth=0.9, linestyle="--"))
    axis.text(0.658, 0.325, "Host authority and execution boundary", ha="center",
              fontsize=9, color=TEAL)
    box(0.685, 0.145, "Human-readable view", "on request\nprojection cost is counted", "data", height=0.13)
    routed_arrow([(0.963, 0.79), (0.99, 0.79), (0.99, 0.21), (0.963, 0.21)], dashed=True)
    axis.text(0.17, 0.24, "Blue: agent representation\nTeal: host and runtime\nGray: supplied or returned data",
              ha="left", va="center", fontsize=9, linespacing=1.5)
    axis.text(0.5, 0.076, "Proposed complete architecture; experiments implement selected components.",
              ha="center", fontsize=9)
    axis.text(0.5, 0.03, "Count generation, checks, tool traffic, memory and requested projections.",
              ha="center", fontsize=9)
    save_figure(figure, output, "ain-aicc-workflow",
                "Proposed AIN/AICC workflow architecture. The full learned-agent system is future work; existing experiments implement selected components.")
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--data", type=Path, default=DEFAULT_OUTPUT / "chart-data.json")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    data = load(args.data)
    verify_sources(data)
    matplotlib, plt = prepare_style()
    architecture_figure(args.output, plt)
    processing_figure(data, args.output, plt)
    memory_figure(data, args.output, plt)
    adaptation_figure(data, args.output, plt)
    theory_figure(data, args.output, plt)
    metadata = {
        "publication": "AIN final draft",
        "matplotlib": matplotlib.__version__,
        "source_chart_data_sha256": digest(args.data),
        "verified_primary_source_count": len(data["source_sha256"]),
        "conceptual_figure": "ain-aicc-workflow is a proposed architecture, not a measured result",
        "figure_inches": {
            "ain-aicc-workflow": [6.5, 4.65], "processing-cost": [6.5, 3.35],
            "memory-cost": [6.5, 3.45], "adaptation-correctness": [6.5, 3.45],
            "approved-core-demand": [6.5, 3.5]},
        "png_dpi": 300, "svg_text": "selectable DejaVu Sans",
        "outputs_sha256": {
            path.name: digest(path) for path in sorted(args.output.iterdir())
            if path.suffix in (".png", ".svg", ".csv")}}
    (args.output / "render-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
