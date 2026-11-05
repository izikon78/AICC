# Historical experiments and reproduction

## New engineering implementation

The [processing/learning study](processing_study/README.md) adds runnable optimized event-processing kernels, a scoped binding prototype, actual local neural cost-model training, and measured million-event jobs. Its results concern execution of finished code. They do not complete the planned independent AI-agent lifecycle study or measure billed model cost.

## Restored inputs

- [Round 7 packet](round7/packet/README.md): protocols, contracts, fixture code, symbolic runtime, and verifier.
- [Round 8 packet](round8/packet/README.md): protocols, tasks/contracts, mock host, reference/near-miss implementations, article addendum, architecture recommendation, and `SHA256SUMS.txt`.
- [Efficiency protocol PDF](efficiency/AICC_Token_Cost_Compute_Research_Protocol.pdf) and [measurement template](efficiency/AICC_Efficiency_Measurement_Template.csv).

The packet files are preserved from the supplied ZIPs. The directory name `sealed` describes the original authoring protocol; these are public historical fixtures and are not a secure hidden-test system.

## Portable official-suite verification

From the repository root with Python 3.10+:

```shell
python tools/verify_research_import.py
```

The runner checks the imported source hashes and Round 8 manifest, copies fixtures and existing Claude/Grok submissions into temporary directories under ignored `work/`, then executes eleven commands. It does not modify the packets or call model APIs. To save a fresh report, use a new output filename:

```shell
python tools/verify_research_import.py --output work/latest-verification.json
```

The [4 November verification record](../docs/research/verification-2026-11-04.json) passed all eleven commands. Official workflow results were 14/14 for the available Round 7 reuse submissions and 20/20 for the available Claude/Grok Round 8 submissions. The mock security checks are reported separately.

## Historical scripts and limits

Original contributor scripts remain under `agents/`. Several expect the organizer's Linux paths and extra dependencies. The full efficiency study still refers to an absent Language A/B runtime and specification under `/home/claude/sym`; its complete reproduction is not yet portable. `dry_run_trials.csv` is synthetic test input, not experimental measurements.

The [review](../docs/research/REVIEW_2026-11-04.md) records missing audited variants, Gemini corrections, and the distinction between executing existing programs and conducting independent AI-authoring trials. Do not pool counts across versions or treat source token sizes as billed inference usage.
