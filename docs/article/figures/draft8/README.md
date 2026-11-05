# Draft 8 figures

These charts are regenerated from the three recorded processing studies. They are **not measurements of AIN**, a native-language model, billed tokens, or dollar savings. The AIN comparison diagram is a proposed experiment.

- [Processing gains](processing-gains.png): ordinary optimized and AICC optimized pipeline reductions versus each run's own reference, using sums of three per-job medians.
- [Memory gains](memory-gains.png): ordinary optimized versus reference by workload/run; Windows working set and Linux RSS differ.
- [Neural selection](neural-selection.png): extra kernel-only time versus static on each run's 24 held-out calibration jobs, excluding selection overhead.
- [Worker-time pies](worker-time-pies.png): for each run's nine AICC-static workers, sum pipeline time and sum the remainder of worker time. These are an actual-time partition, not sums of medians and not a cost breakdown.
- [AIN comparison design](ain-comparison-design.png): conventional source, structured IR, and an AIN form evaluated against equal semantic behavior. Proposed, not executed.

SVG copies are available for all figures. [Figure data](figure-data.json) records exact values and source hashes. [Summary CSV](summary-data.csv) contains 45 per-run/job/mode medians; [worker CSV](worker-data.csv) contains 135 actual worker records.

From the repository root:

```shell
python tools/synthesize_processing_replications.py
```

Requires NumPy and Matplotlib; optional pinned plotting requirements remain in `experiments/processing_study/requirements-plot.txt`. This command recomputes recorded results and renders figures; it does not run new benchmarks or call model APIs.
