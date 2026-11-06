"""Make reviewable tables/plots directly from retained worker records."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parent


def summarize(run, plot_deps=None):
    rows = json.loads((run / "workers.json").read_text())
    validation = json.loads((run / "validation.json").read_text())
    if validation != {"workers": 27, "failures": 0,
                       "output_matches": {s: True for s in ("repeated_keys", "many_keys", "late_mix")},
                       "source_unchanged": True}:
        raise ValueError("The planned complete 27-worker set did not validate")
    shapes, modes = ("repeated_keys", "many_keys", "late_mix"), ("python", "ir", "ain")
    metrics = ["execution_including_host_and_check_seconds", "fresh_process_wall_seconds",
               "python_allocation_peak_bytes", "process_peak_working_set_bytes",
               "program_preparation_seconds", "separate_check_seconds"]
    table = []
    for shape in shapes:
        for mode in modes:
            cell = [r for r in rows if (r["shape"], r["mode"]) == (shape, mode)]
            if len(cell) != 3:
                raise ValueError("Missing repetition")
            out = {"shape": shape, "mode": mode, "report_count": cell[0]["report_count"],
                   "counters": cell[0]["counters"], "result_sha256": cell[0]["result_sha256"]}
            for key in metrics:
                values = [r[key] for r in cell]
                out[key] = {"median": statistics.median(values), "min": min(values), "max": max(values)}
            table.append(out)
    (run / "summary.json").write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")
    if plot_deps:
        sys.path.insert(0, str(plot_deps))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "figure.facecolor": "#f7f9fc",
                         "axes.facecolor": "#f7f9fc", "savefig.facecolor": "#f7f9fc"})
    colors = ("#d4772b", "#5076a9", "#087f82")
    names = ("Python", "Readable IR", "Numeric AIN")
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.6))
    panels = [("execution_including_host_and_check_seconds", 1, "Execution, seconds", "Instrumented execution cost"),
              ("process_peak_working_set_bytes", 1024**2, "Peak process working set, MiB", "Whole-process memory")]
    for ax, (metric, scale, ylabel, title) in zip(axes, panels):
        for mi, (mode, color, name) in enumerate(zip(modes, colors, names)):
            medians, lower, upper = [], [], []
            positions = [si + (mi - 1) * .25 for si in range(3)]
            for si, shape in enumerate(shapes):
                record = next(r for r in table if (r["shape"], r["mode"]) == (shape, mode))
                entry = record[metric]
                medians.append(entry["median"] / scale)
                lower.append((entry["median"] - entry["min"]) / scale)
                upper.append((entry["max"] - entry["median"]) / scale)
                points = [r[metric] / scale for r in rows if (r["shape"], r["mode"]) == (shape, mode)]
                ax.scatter([positions[si] + jitter for jitter in (-.035, 0, .035)], points,
                           s=15, color="#102432", zorder=4)
            ax.bar(positions, medians, width=.21, label=name, color=color, alpha=.85,
                   yerr=[lower, upper], capsize=3, linewidth=0, zorder=2)
        ax.set_xticks(range(3), ["Repeated keys", "Many keys", "Late / mixed"])
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", pad=15)
        ax.grid(axis="y", alpha=.18, zorder=0)
        ax.set_ylim(bottom=0)
    axes[0].legend(frameon=False, ncol=3, loc="upper left", bbox_to_anchor=(0, 1.04), fontsize=9)
    fig.suptitle("AIN v0: matched complex streaming workflow", x=.06, ha="left", fontsize=19, fontweight="bold")
    fig.text(.06, .025, "20,000 events × 3 workloads × 3 forms × 3 fresh-worker repetitions. Bars: medians; dots/ranges: observed runs, not confidence intervals.\n"
             "Python interpreter + shared host, tracemalloc enabled. Process memory includes source, reports and history. No trained model or billing claim.", fontsize=9, color="#3d4c59")
    fig.subplots_adjust(left=.065, right=.985, top=.79, bottom=.18, wspace=.27)
    target = ROOT / "figures"
    target.mkdir(exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(target / ("local-processing." + extension), dpi=170)
    plt.close(fig)
    summary_lines = ["| Workload | Form | Execution median (s) | Fresh worker median (s) | Peak process median (MiB) |",
                     "|---|---|---:|---:|---:|"]
    for entry in table:
        summary_lines.append(f"| {entry['shape']} | {entry['mode']} | {entry[metrics[0]]['median']:.3f} | {entry[metrics[1]]['median']:.3f} | {entry[metrics[3]]['median'] / 1024**2:.1f} |")
    (run / "table.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print("\n".join(summary_lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--plot-deps", type=Path)
    args = parser.parse_args()
    summarize(args.run, args.plot_deps)
