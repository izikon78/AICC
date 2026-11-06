"""Audit and report the conditional approved-workflow experiment."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.approved_workflow_theory.accounting import text_token_count
from experiments.approved_workflow_theory.workloads import execute, expected


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path,
                        default=Path(__file__).parent / "results/approved-core-2026-11-06")
    args = parser.parse_args()
    directory = args.results
    manifest = load(directory / "manifest.json")
    for relative, digest in manifest["source_sha256"].items():
        if hashlib.sha256((ROOT / relative.replace("\\", "/")).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Frozen source changed at {relative}")
    fixtures = load(directory / "fixtures.json")
    if hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest() != manifest["fixture_sha256"]:
        raise ValueError("Frozen fixture hash changed")
    episodes = load(directory / "episodes.json")
    totals = load(directory / "totals.json")
    tasks = {(chain["id"], stage["stage"]): stage["task"]
             for chain in fixtures for stage in chain["stages"]}
    for episode in episodes:
        if execute(episode["artifact"], tasks[episode["chain"], episode["stage"]]) != expected(tasks[episode["chain"], episode["stage"]]):
            raise ValueError("Saved artifact failed replay")
        if not episode["working_records"] or not episode["outgoing_memory"]["checks_passed"]:
            raise ValueError("Saved working record or persisted memory is missing")
    sources = load(directory / "approved_core_sources.json")
    core_source = "\n".join(sources.values())
    tree = ast.parse(core_source)
    core = {"public_functions": len(sources) - 1, "source_tokens": text_token_count(core_source),
            "for_loops": sum(isinstance(node, ast.For) for node in ast.walk(tree)),
            "while_loops": sum(isinstance(node, ast.While) for node in ast.walk(tree)),
            "comprehensions": sum(isinstance(node, ast.comprehension) for node in ast.walk(tree))}
    result = {"approved_core": core, "schedules": {}}
    lines = [
        "# Approved-core workflow theory test", "",
        "6 November 2026. Theory and research direction by Izik Bachar. Experiment implementation "
        "and review by Codex with collaboration agents.", "",
        "The experiment adopts the requested premise that an optimized short representation, "
        "fluent agents and fully approved reusable core code already exist. It fixes composition "
        "correctness through oracle agents and executes their artifacts and tool actions. "
        "This isolates the conditional resource demand of composing, changing, repairing and "
        "handing off workflows.", "",
        "Under the frozen equal-cost-per-position assumption, ideal AIN uses 24.0% fewer total "
        "positions than short-alias Python in the resident-data schedule and 12.8% fewer in the "
        "inspect-data schedule. This is a conditional accounting result. The Python columns "
        "contain measured text-token counts, while the ideal columns contain modeled semantic "
        "code units plus the same common input text. Actual inference latency and trained "
        "agent efficiency require separate measurements.", "",
        "## Complete workflow ledger", "",
        "Each schedule contains 18 chains, 72 stages and 216 logical agent requests. Shared "
        "requirements and business parameters are charged at every request. Predecessor artifacts, "
        "persisted memory and all accumulated action/tool history are counted at every reuse. "
        "Total positions include input and output, with equal position cost. Output includes "
        "one response-end position. Every schedule's 72 stages passed independent result checks.", "",
        "| Data schedule | Representation | Input positions | Output positions | Total positions | "
        "Reduction versus short-alias Python |",
        "|---|---|---|---|---|---|",
    ]
    labels = {"python": "Python approved calls", "python_aliases": "Python short aliases",
              "ideal_ain": "Ideal AIN", "ideal_ir": "Ideal readable IR", "ideal_python": "Ideal Python interface"}
    for schedule, profiles in totals.items():
        baseline = sum(profiles["python_aliases"][key] for key in ("input_positions", "output_positions"))
        result["schedules"][schedule] = {}
        for profile, values in profiles.items():
            total = values["input_positions"] + values["output_positions"]
            reduction = 1 - total / baseline
            result["schedules"][schedule][profile] = {"total_positions": total,
                                                    "reduction_vs_alias_python": reduction}
            lines.append(f"| {schedule} | {labels[profile]} | {values['input_positions']:,} | "
                         f"{values['output_positions']:,} | {total:,} | {reduction:.1%} |")
    native_output = totals["resident"]["ideal_ain"]["output_positions"]
    python_output = totals["resident"]["python_aliases"]["output_positions"]
    lines.extend([
        "", f"Generated output falls from {python_output:,} measured Python text positions to "
        f"{native_output:,} modeled ideal positions, a {1 - native_output / python_output:.1%} "
        "conditional reduction. Total savings are smaller because shared task inputs and tool "
        "history also consume positions.", "",
        "Ideal readable IR and ideal Python attain the same counts as ideal AIN under the "
        "same learned vocabulary and interface assumptions. This supports the shared mechanism "
        "of compact learned composition. The vocabulary label supplies no additional reduction "
        "in this experiment.", "",
        "## Executed work and reuse", "",
        "The workflows perform event filtering/deduplication/grouping, cache version selection "
        "with expiry/deletion, and idempotent publication/retry simulation. Each artifact "
        "composes five generic approved functions. Build writes a composition, change edits "
        "one parameter, repair edits one injected defect, and fresh-context handoff uses the "
        "saved artifact and memory. Working records and persisted memory are stored by the "
        "executed host actions. Checks run against separate fixture oracles before submission.", "",
        f"The approved core contains {core['public_functions']} public functions, "
        f"{core['for_loops']} explicit for loops, {core['while_loops']} while loop and "
        f"{core['comprehensions']} comprehensions. Its stored Python source measures "
        f"{core['source_tokens']:,} text tokens. Approval and fluent core knowledge are given "
        "to every condition, so shared function bodies incur zero repeated generation cost "
        "in the primary comparison. Functions and loops run inside those approved components. "
        "Agent-authored artifacts specify their composition and arguments.", "",
        "Resident data stays in host storage and is referenced through a handle. The agent "
        "receives task rules, parameters and schema, and tools expose status acknowledgements. "
        "The private judge checks complete business results. The inspect schedule also includes "
        "all records in each request context. Literal values remain in the saved fixtures and "
        "host-data byte ledger under both schedules.", "",
        "## Fixed representation model", "",
        "The illustrative vocabulary has 65,536 entries. Of these, 32,768 encode fifteen-bit "
        "payloads, eight encode type/atom tags and a frozen finite set encode public interface "
        "symbols. Approved signatures supply operand order and types. A program length and "
        "each operation reference cost one unit. Small signed integer operands cost one unit. "
        "Known public field references cost one unit. New strings and larger values carry "
        "type, length and packed UTF-8 payload charges. Lists and memory records carry framing "
        "and every operand/key/value. This is a fixed accounting proxy for the existing "
        "optimized-language premise.", "",
        "Python text is tokenized using the cached Qwen2.5-1.5B tokenizer at the pinned revision "
        "recorded in accounting.py. A short-alias control gives approved functions and tools "
        "fixed single-letter names. Ideal controls give every representation the same compact "
        "semantic interface. Requirements use identical common text in every arm. A fixed "
        "framing charge adds four input positions per request and three per previous action/"
        "observation pair. No model inference or new language training is performed by this test.", "",
        "The auxiliary `byte_fallback_units` field is a raw payload-byte diagnostic. Its "
        "call-stream integer tally supplies decimal byte lengths and is unused by the primary "
        "fifteen-bit encoding and result tables.", "",
        "## Setup and repeated use", "",
        "Approval, reusable core availability and fluent vocabulary knowledge are premises. "
        "An additional AIN-specific setup cost, if introduced, is an unknown fixed cost F. "
        "The table below gives the maximum additional setup positions recoverable from the "
        "conditional resident-data saving, under the same equal-cost assumption. It supplies "
        "a break-even boundary for an entered setup cost.", "",
        "| Repeated four-stage chains | Additional setup positions recoverable |",
        "|---|---|",
    ])
    saving = (result["schedules"]["resident"]["python_aliases"]["total_positions"]
              - result["schedules"]["resident"]["ideal_ain"]["total_positions"]) / len(fixtures)
    for repetitions in (1, 10, 100, 1000):
        lines.append(f"| {repetitions:,} | {saving * repetitions:,.0f} |")
    lines.extend([
        "", "For positive F, the corresponding break-even count is F divided by the saving "
        "per chain. Training hours, financial cost, power consumption and maintenance cost "
        "have separate units and would require their own measured conversion.", "",
        "## Limits and audit", "",
        "The 18 chains are six parameter/data variants of three fixed composition templates. "
        "The two schedules replay the same tasks. They establish executable accounting cases. "
        "Core approval alone leaves planning uncertain, so this experiment adds a perfect-"
        "composer assumption to isolate resource demand. New functions and arbitrary new "
        "control-flow implementations require further cases. Actual trained-agent correctness, "
        "inference speed and success-adjusted compute remain open measurements.", "",
        "The manifest freezes codebook, aliases, source hashes, fixture hash and assumptions "
        "before measurement. Sixteen focused tests passed. This report verifies frozen hashes "
        "and replays every saved artifact. The raw episodes preserve input contexts, all actions, "
        "host observations, working records, persisted memory, business-data bytes and per-"
        "request ledgers. Timing of shared host execution is retained as a separate diagnostic.", "",
    ])
    (directory / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(directory / "REPORT.md")


if __name__ == "__main__":
    main()
