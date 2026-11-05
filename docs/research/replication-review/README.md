# Review of submitted processing replications

Reviewed by Codex and same-session checking agents on 5 November 2026. The review is an audit of supplied artifacts, not another provider trial or a rerun of the submitted stress benchmarks.

| Record | Scope |
|---|---|
| [Claude audit](claude-audit.json) | Reviewed commit 2f17cd3825f8e9785c919da2add80d1e35e97b97; 45 listed asset hashes, eleven frozen source identities, 21 original result checksums, all 45 matrix rows and raw/summary medians, matching output signatures, model/policy choices, and 18 deterministic checkpoint cases reproduced locally from inspected function definitions. |
| [Grok audit](grok-audit.json) | Original archive SHA-256 7294263b7fb8f7cc1c77c0d508a6ce5ab56271405bfcc5a38f90d7682f3acc9c; 16 listed asset hashes, eleven recorded source identities, all 45 matrix rows, summaries, calibration timing labels, model/policy choices, signatures, and granularity records. No new checkpoint probe or source copies were supplied. |

The original [study](../../../experiments/processing_study/README.md) and [replication protocol](../../../experiments/processing_study/agent-replication/README.md) define the comparison. The [combined synthesis](../REPLICATION_SYNTHESIS_2026-11-05.md) explains the findings and limits.

Recomputations used raw records to check all 15 job/mode medians per complete run; exactly three repeats per cell; disjoint 72/24/24 calibration splits with the same public descriptor populations; training-only fitting of the strongest of four static policies; and held-out costs/choices recomputed with the supplied model weights. Logs were checked as submitted execution records. Checksums verify byte consistency, not authorship or remote execution attestation.

Neither three repetitions nor observed same-code variation establishes a formal noise floor, proves zero AICC effect, or supports financial savings. Claude's checkpoint probe is a fake-clock cooperative demonstration; its size sweep is a post hoc warm/list/kernel-only diagnostic without output-conformance checks or raw timing samples. Grok did not inject mid-batch cancellation, revocation, or expiry. These probes are kept separate from the complete stress matrices.
