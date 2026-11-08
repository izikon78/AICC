"""Write the post-comparison report; never changes the first counter or ledgers."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from packaging.requirements import Requirement
import importlib.metadata

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PACKAGE = ROOT / "experiments" / "approved_workflow_theory"
FIRST = BASE / "initial-v1"
EXACT = BASE / "exact-reference-offline-v1"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


manifest = load(FIRST / "manifest.json")
seal = load(BASE / "precomparison-seal.json")
freeze = load(FIRST / "freeze.json")
for name, expected in freeze["outputs_sha256"].items():
    assert digest(FIRST / name) == expected, f"first-attempt file changed: {name}"
assert digest(BASE / "independent_counter.py") == digest(BASE / "initial-counter-preserved.py") == seal["implementation_sha256"]
assert digest(BASE / "initial-canonical-ledgers.json") == seal["canonical_ledger_sha256"]
independent = load(FIRST / "comparison.json")
exact = load(EXACT / "comparison.json")
assert independent["matches_reference"] and exact["matches_reference"]
tests_log = (EXACT / "logs" / "tests.log").read_text(encoding="utf-8")
assert "Ran 20 tests" in tests_log and tests_log.rstrip().endswith("OK")
pins = {}
for line in (PACKAGE / "requirements-reproduce.txt").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    requirement = Requirement(line)
    if requirement.marker is None or requirement.marker.evaluate():
        version = importlib.metadata.version(requirement.name)
        pins[requirement.name] = dict(installed=version, required=str(requirement.specifier), matches=version in requirement.specifier)
assert all(record["matches"] for record in pins.values())
tracked_status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT, text=True)
assert not tracked_status.strip()
reference_manifest = load(EXACT / "manifest.json")
totals = load(FIRST / "totals.json")
inputs = load(PACKAGE / "trace-inputs.json")
save(BASE / "extracted-fixtures.json", inputs["fixtures"])
save(BASE / "extracted-approved-core-sources.json", inputs["approved_core_sources"])
validation = dict(verified_utc=datetime.now(timezone.utc).isoformat(),
                  first_attempt_files_unchanged=True, first_implementation_unchanged=True,
                  tracked_files_unchanged=True, package_pins=pins,
                  independent_comparison=independent, exact_reference_comparison=exact,
                  reference_tests_passed=20,
                  extracted_fixtures_file_sha256=digest(BASE / "extracted-fixtures.json"),
                  extracted_core_file_sha256=digest(BASE / "extracted-approved-core-sources.json"),
                  reference_manifest_source_hashes=reference_manifest["source_sha256"],
                  reference_fixture_hash=reference_manifest["fixture_sha256"])
save(BASE / "final-validation.json", validation)

lines = [
    "# Independent approved-core accounting recreation", "",
    "The first independently written counter matched the published reference exactly on both schedule/profile totals and every request ledger. The separate exact reference rerun also matched. No accounting correction, expected-number tuning or failed measurement attempt occurred.", "",
    "## Independence and order of work", "",
    "I began with no AIN background supplied to me. I first read only `AGENT_START_HERE.md`, then `REPLICATION_SPEC.md`, `trace-inputs.json`, pinned requirements and tokenizer hashes. I ran only `reproduce.py --prepare-tokenizer` to obtain and verify assets. I next consulted the expressly permitted `workloads.py` for approved implementations and fixture oracles. I wrote my own generic and typed counters, Python program/action renderers, recurrence and aggregation. I did not inspect reference accounting.py, run.py, report.py, the article brief, reference aggregates or reference ledgers before freezing the first results.", "",
    f"Git revision: `{manifest['git_revision']}`. The first output freeze is timestamped `{freeze['frozen_utc']}`; the additional canonical-ledger seal is timestamped `{seal['sealed_utc']}`. These are local provenance records, not third-party timestamp attestations.", "",
    "Only after preserving source, complete first ledgers, totals, hashes, environment, renderer text and execution evidence did I run the published independent comparator. I then ran the exact offline reference wrapper into a different new folder. After both succeeded, I read ARTICLE_REPRODUCTION_BRIEF.md, README.md and reference accounting/rendering/report code to assess interpretation and explain implementation differences.", "",
    "All filesystem mutations were confined to this fresh checkout's `work/` directory. Python bytecode generation was disabled and HF_HOME pointed to `work/tokenizer-cache` on every tokenizer/reference command. Tracked files are unchanged. The pre-existing Python environment was used without installation changes.", "",
    "## Environment and hashes", "",
    f"Python: `{manifest['python']}`. Platform: `{manifest['platform']}`. No Torch, TensorFlow or Flax installation was needed; all work used CPU execution and tokenizer assets. All applicable pinned package versions match (`final-validation.json`), and `initial-v1/manifest.json` records every installed package.", "",
    f"Tokenizer: `Qwen/Qwen2.5-1.5B`, revision `{manifest['tokenizer_revision']}`, encoding with `add_special_tokens=False`. All six assets were SHA-256 verified before counting and verified again by my counter. Windows emitted a cache symlink warning and stored duplicate files instead; this changed neither asset hashes nor results.", "",
    "| Evidence | SHA-256 |", "|---|---|",
]
for label, value in [
    ("First independent counter", seal["implementation_sha256"]),
    ("Initial canonical ledgers", seal["canonical_ledger_sha256"]),
    ("Initial episodes.json bytes", seal["episodes_file_sha256"]),
    ("Initial totals.json bytes", seal["totals_file_sha256"]),
    ("Canonical totals (reference comparator)", independent["checks"]["totals.json"]["actual_canonical_sha256"]),
    ("First freeze.json", seal["freeze_file_sha256"]),
]:
    lines.append(f"| {label} | `{value}` |")
lines.extend(["", "Original input hashes:", "", "| Input | SHA-256 |", "|---|---|"])
for name, value in manifest["input_hashes"].items():
    lines.append(f"| {name} | `{value}` |")
lines.extend(["", "The extracted approved sources and fixtures are retained separately. `final-validation.json` records their file hashes as well as the exact wrapper's independently frozen source and fixture hashes. Tokenizer asset hashes and full package versions are in the first manifest.", "", "## Measured and modeled totals", "",
              "| Schedule | Profile | Input | Output | Input + output |", "|---|---|---:|---:|---:|"])
for schedule, profiles in totals.items():
    for profile, values in profiles.items():
        ip, op = values["input_positions"], values["output_positions"]
        lines.append(f"| {schedule} | {profile} | {ip:,} | {op:,} | {ip + op:,} |")
for schedule in totals:
    baseline = sum(totals[schedule]["python_aliases"][key] for key in ("input_positions", "output_positions"))
    ideal = sum(totals[schedule]["ideal_ain"][key] for key in ("input_positions", "output_positions"))
    lines.extend(["", f"{schedule}: `{baseline:,} - {ideal:,} = {baseline - ideal:,}` counted positions saved versus short-alias Python, or `{100 * (baseline - ideal) / baseline:.8f}%`."])
lines.extend([
    "", "The Python rows combine measured Qwen text-token counts and fixed framing positions. The ideal rows combine the same measured common text with declared ideal code units and fixed framing. Equal cost per position is assumed. All three ideal labels tie by construction under the same semantic interface; this experiment establishes no advantage unique to AIN over equally ideal IR or Python.", "",
    "## Verification and implementation differences", "",
    "The independent attempt contains 144 supplied episodes (72 per data schedule), 432 logical requests across schedules and 2,160 ledger rows across five profiles. My 17 boundary checks passed, including UTF-8 payloads, bool/integer distinction, signed operand boundaries, generic versus typed lists, invalid values, nonfinite floats, length limits, cycles and depth limits. All 144 episode action replays matched the final artifact, working records, memory and oracle result. Both independently rendered Python forms executed correctly for each episode (288 rendering checks). All 36 repair episodes confirmed that the injected broken program changed the result.", "",
    "My counter uses direct integer totals and a token cache, rather than the reference's diagnostic breakdown dictionaries. I preserve dictionary insertion order for Python repr/text rendering; generic ideal sums are order-insensitive. I replay the supplied actions and verify rendered lambdas against permitted fixture oracles. The reference additionally reconstructs its semantic episodes itself and validates Python programs through a restricted AST reader. My own result is an independent accounting/rendering recreation from published semantic traces, with approved workload execution reused as the specification permits.", "",
    "The independent comparator returned exit code 0 with `matches_reference: true`, exact totals and exact per-request ledgers, and `first_difference: null` for both files. The canonical ledger hash independently sealed before comparison equals the comparator's actual and expected ledger hashes. No earliest discrepancy exists.", "",
    "The exact offline wrapper returned exit code 0, all 20 package tests passed, and fixtures, approved core sources, totals, full episodes (except execution_seconds), summary and normalized manifest matched. Host timings remain in fresh raw outputs. Only episode execution timing is excluded; source path separators are normalized for cross-platform comparison.", "",
    "## Ambiguities and bugs observed", "",
    "1. REPLICATION_SPEC says the approved signatures supply operand types, including field-dependent equality types, but config.catalog_schema contains only argument names. The frozen JSON values and special write(program) rule were sufficient to reproduce every count. A generalized typed interface would benefit from an explicit type schema. No alternate accounting was introduced.",
    "2. The generated reference REPORT.md says 'Sixteen focused tests passed', while logs/tests.log records 20 tests, all passing. The sentence is hardcoded in report.py. This is stale reporting prose and does not affect the arithmetic or wrapper comparison.",
    "3. No installation, accounting or environment compatibility bug blocked reproduction. The Windows cache symlink and unavailable model-framework messages were diagnostic only.", "",
    "## Scientific interpretation", "",
    "The package makes its premises usable by a new agent: fluent optimized representation, fully approved shared core and correct predefined composition plans. I could reconstruct the integer result from the documented rules without seeing expected numbers. This supports reproducibility of the conditional accounting example. It does not demonstrate that an agent learned AIN, planned the workflows without supplied traces, generated arbitrary new control flow, or used less real inference time, energy or money.", "",
    "The 18 chains are six variants of three composition templates; the two data schedules replay the same tasks. The functions and loops execute inside the shared approved core. Context exposure, framing, vocabulary, payload packing and tokenization are frozen model choices. Changes to those assumptions or actual model evaluation should be a separately versioned extension.", "",
    "## Retained files and rerun commands", "",
    "- `independent_counter.py` and byte-identical `initial-counter-preserved.py`: first independent implementation.",
    "- `initial-v1/episodes.json`, `totals.json`, `renderings.json`, `checks.json`, `manifest.json`, `freeze.json`, `independent-report-before-comparison.md`: unchanged first attempt.",
    "- `initial-canonical-ledgers.json` and `precomparison-seal.json`: canonical ledger and pre-reference provenance.",
    "- `initial-v1/comparison.json`: successful independent reference comparison, added after the freeze.",
    "- `exact-reference-offline-v1/`: separate fresh reference artifacts, environment, report, comparison and complete tests/run/report logs.",
    "- `final-validation.json`: post-comparison integrity, package pins, checks and extraction hashes.", "",
    "Run from the checkout root with the pinned Python environment. The independent script has no user-specific filesystem paths; it expects its prescribed location at work/independent-agent and accepts a fresh output directory via CLI. Tokenizer assets resolve under work/tokenizer-cache.", "",
    "```powershell",
    "$env:PYTHONDONTWRITEBYTECODE='1'",
    "$env:HF_HOME=Join-Path (Get-Location) 'work\\tokenizer-cache'",
    "& $envPython experiments/approved_workflow_theory/reproduce.py --prepare-tokenizer",
    "& $envPython work/independent-agent/independent_counter.py --output work/independent-agent/new-independent-attempt",
    "# Preserve and seal the new implementation/outputs before comparing.",
    "& $envPython experiments/approved_workflow_theory/reproduce.py --compare work/independent-agent/new-independent-attempt",
    "& $envPython experiments/approved_workflow_theory/reproduce.py --offline --output work/independent-agent/new-exact-reference-attempt",
    "```", "",
    "The original attempt remains preserved. No correction or extension was needed to match.",
])
(BASE / "INDEPENDENT_REPORT_DETAILS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
concise = f"""# Independent reconstruction: first attempt matched

I reconstructed this accounting without prior AIN background on Git commit
`{manifest['git_revision']}`. Both the first independent
counter and a subsequent exact offline reference rerun matched the published
results. No corrections to the counter or ledgers were needed.

**Read order.** I began only with AGENT_START_HERE.md, then read
REPLICATION_SPEC.md, semantic trace-inputs.json, pinned requirements and tokenizer
hashes. I ran only tokenizer preparation and consulted the expressly permitted
workloads.py for approved execution components and fixture oracles. I wrote my
own counting, Python rendering, recurrence and aggregation code. Before seeing
reference accounting.py/run.py/report.py, article observations, aggregate counts
or reference ledgers, I preserved source, all first ledgers, totals, environment
and hashes. I compared only after freezing; reference implementation review
followed the successful runs. The seals are local provenance records rather than
third-party timestamp attestations.

**Frozen evidence.** Source SHA-256:
`{seal['implementation_sha256']}`.
Canonical ledger SHA-256:
`{seal['canonical_ledger_sha256']}`.
Canonical totals SHA-256:
`{independent['checks']['totals.json']['actual_canonical_sha256']}`.
The comparator confirmed the same ledger/totals hashes, with no differing field.
`precomparison-seal.json`, `initial-v1/freeze.json` and
`initial-v1/manifest.json` preserve dates, byte hashes and consulted materials.

| Schedule | Short-alias Python input/output | Ideal input/output | Total reduction |
|---|---:|---:|---:|
| resident | 34,686 / 5,928 | 27,144 / 3,714 | 24.02127345% |
| inspect | 70,470 / 5,928 | 62,928 / 3,714 | 12.76996780% |

**Checks and environment.** All 144 episodes, 2,160 profile/request ledger rows,
17 independent boundary checks, 144 execution replays and 288 rendered-Python
execution checks passed. The injected defects changed results in all 36 repair
episodes. The independent comparator returned exit 0 and exact matches; the
separate reference wrapper returned exit 0, passed all 20 package tests and
matched fixtures, sources, totals, episodes, summary and normalized manifest.
Only episode execution_seconds was excluded from deterministic comparison.
Python 3.12.14 on Windows 11 used the CPU-only pinned dependencies; every
applicable package pin matched. All six assets of Qwen/Qwen2.5-1.5B revision
`{manifest['tokenizer_revision']}` were verified.
Full package, source, fixture, input and tokenizer hashes are retained in the
manifests and final-validation.json. All mutations stayed under checkout/work/;
tracked files remained unchanged.

**Two findings, as observed on this commit.** The specification says signatures
supply operand types, but catalog_schema lists only argument names. JSON value
types and the special program rule sufficed for this frozen workload; a general
interface needs an explicit type contract. The generated report says sixteen
tests passed, while its tests.log records twenty, all passing. This stale prose
does not change the counts.

Python text tokens are measured; ideal units are modeled. Common text and ideal
units share an assumed cost per position. Approved components, fluent
representation and correct supplied composition are premises. Ideal AIN, IR and
Python tie. The result reproduces conditional accounting across three workflow
templates, not measured model learning, planning success, latency or energy.

**Retained files.** independent_counter.py (also initial-counter-preserved.py);
initial-v1/ (untouched first ledgers/totals/renderings/checks/provenance plus later
comparison.json); initial-canonical-ledgers.json; precomparison-seal.json;
exact-reference-offline-v1/ (fresh raw artifacts and logs); final-validation.json;
and INDEPENDENT_REPORT_DETAILS.md. No failed measurement attempt or corrected
accounting version occurred.
"""
(BASE / "INDEPENDENT_REPORT.md").write_text(concise, encoding="utf-8")
inventory = {path.relative_to(BASE).as_posix(): digest(path) for path in sorted(BASE.rglob("*")) if path.is_file() and path.name != "evidence-inventory.sha256.json"}
save(BASE / "evidence-inventory.sha256.json", inventory)
print(json.dumps(dict(report=str(BASE / "INDEPENDENT_REPORT.md"), report_sha256=digest(BASE / "INDEPENDENT_REPORT.md"),
                      evidence_files=len(inventory), first_files_unchanged=True, package_pins=len(pins), tracked_files_unchanged=True), indent=2))
