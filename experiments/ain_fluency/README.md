# Current-agent AIN fluency simulation

Start with the [published plan and predictions](PLAN.md). This experiment asks
whether a current agent can produce correct workflow controllers more cheaply
after matched preparation in Python, readable IR or numeric AIN. It does not train
a model or establish native-language efficiency.

- [Participant material](PARTICIPANT_GUIDE.md): exactly what agents receive.
- [Judge](JUDGE.md): independent controller, manual checks, effects and recovery.
- `tasks.py`: prompts, strict output schemas and explicit fallback provenance.
- `run.py`: fixed schedule, separate preparation, metered CLI calls and artifacts.
- `report.py`: all-assigned-work accounting, success gates and cost sensitivities.

The 18 scored submissions form six chains, with 18 additional preparation calls.
One submission per stage; errors, failed fluency, timeouts and fallback costs stay
in the results. Canonical replacement work is diagnostic and cannot rescue a
failed chain. All forms use the existing shared AIN v0 host capabilities.

## Reproduce

Python 3.12 with Unicode 15.0 and an authenticated Codex CLI are needed. The fixed
model identifier is `gpt-6.1-sol`, with reasoning effort `ultra`. Replicators must
update the publication guard for their own preregistered branch, preserve the
original record, and publish the change before their trial. Do not reuse another
person's credentials or paste tokens into participant prompts.

```text
python -m unittest discover -s experiments/ain_fluency/tests -v
python experiments/ain_fluency/run.py
python experiments/ain_fluency/run.py --execute
python experiments/ain_fluency/report.py experiments/ain_fluency/results/current-agent-2026-11-06
```

The command without `--execute` only prints the fixed schedule. Participant calls
require the clean harness commit to be pushed first. The runner refuses to
overwrite a prior run. Source hashes and model/settings are saved in the manifest.
No dollar invoice is available through this sign-in; normalized token weights
are hypothetical sensitivity assumptions. Matplotlib is needed for charts only.
The experiment meters participant inference calls, not the earlier cost of
designing the language, implementing the host, or building this research harness.

Concept, architecture and research direction: **Izik Bachar**. Experiment design,
implementation, execution and documentation assistance: **Codex**, including
same-session design, language-material and independent-judge review agents.
Those helpers are not independent cross-provider replications.
