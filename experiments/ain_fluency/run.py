"""Metered, preregistered current-agent experiment; participant calls require --execute.

Never reads credentials. Codex uses its existing authenticated account. Participants
receive prompts only, in empty directories outside this checkout, with no tools.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
import tasks
from judge import judge_artifact

PLAN_COMMIT = "82405a53f1ea92b0992b657323617fecb3b3dfaf"
MODEL = "gpt-6.1-sol"
EFFORT = "ultra"
SEED = 20261106
TIMEOUT = 300


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()


def schedule():
    rng = random.Random(SEED)
    result = []
    for delta in (30, 75):
        for stage in ("build", "change", "repair"):
            modes = ["python", "ir", "ain"]
            rng.shuffle(modes)
            for mode in modes:
                result.append({"id": f"d{delta}-{stage}-{mode}", "mode": mode,
                               "stage": stage, "delta": delta})
    return result


def source_hashes():
    paths = [HERE / "PLAN.md", HERE / "PARTICIPANT_GUIDE.md", *HERE.glob("*.py"),
             *HERE.glob("tests/*.py"), *(HERE.parent / "ain_v0" / "ain").glob("*.py")]
    paths += [ROOT / "docs/ain/COMPLEX_TASK.md", HERE.parent / "ain_v0" / "ENGINE.md",
              HERE.parent / "ain_v0" / "LANGUAGE.md",
              *(HERE.parent / "ain_v0" / "programs").glob("arithmetic-example.*.json")]
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths)) if p.is_file()}


def parse_events(stdout):
    events, invalid = [], 0
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            invalid += 1
    completed = [e for e in events if e.get("type") == "turn.completed"]
    messages = [e["item"].get("text", "") for e in events
                if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "agent_message"]
    allowed = {"agent_message", "reasoning"}
    tools = [e.get("item", {}).get("type") for e in events
             if e.get("type") in {"item.started", "item.completed"} and
             e.get("item", {}).get("type") not in allowed]
    substantive = any(e.get("type") == "item.completed" and e.get("item", {}).get("type") in allowed
                      and any(e["item"].get(key) for key in ("text", "summary")) for e in events)
    return {"usage": completed[-1].get("usage") if completed else None,
            "response_text": messages[-1] if messages else None,
            "substantive_response": substantive,
            "tool_violations": sorted(set(tools)), "invalid_jsonl_lines": invalid,
            "turn_completed": bool(completed),
            "error_types": [e.get("type") for e in events if e.get("type") in {"error", "turn.failed"}]}


def invoke(call_dir, prompt, schema, isolated_root):
    """One call; retry infrastructure once only without substantive response."""
    call_dir.mkdir(parents=True, exist_ok=False)
    (call_dir / "prompt.txt").write_text(prompt, encoding="utf-8", newline="\n")
    dump(call_dir / "schema.json", schema)
    attempts = []
    for attempt_number in (1, 2):
        cell = isolated_root / call_dir.parent.name / call_dir.name / str(attempt_number)
        cell.mkdir(parents=True, exist_ok=False)
        schema_path = cell / "response-schema.json"
        dump(schema_path, schema)
        command = [shutil.which("codex"), "exec", "--json", "--ephemeral", "--ignore-user-config",
                   "--model", MODEL, "-c", f'model_reasoning_effort="{EFFORT}"',
                   "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
                   "--output-schema", str(schema_path), "-C", str(cell), "-"]
        start = time.perf_counter()
        timed_out = False
        try:
            proc = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                  encoding="utf-8", timeout=TIMEOUT)
            stdout, stderr, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as error:
            timed_out = True
            stdout = error.stdout or ""
            stderr = error.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            code = None
        elapsed = time.perf_counter() - start
        parsed = parse_events(stdout)
        # Keep stderr outside the publication tree, never echo authentication/local diagnostics.
        (cell / "stderr-private.log").write_text(stderr, encoding="utf-8", newline="\n")
        (call_dir / f"attempt-{attempt_number}.jsonl").write_text(stdout, encoding="utf-8", newline="\n")
        attempt = {"attempt": attempt_number, "elapsed_seconds": elapsed, "exit_code": code,
                   "timed_out": timed_out, **parsed,
                   "stderr_bytes": len(stderr.encode("utf-8")),
                   "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest()}
        attempts.append(attempt)
        dump(call_dir / "call.json", {"attempts": attempts})
        # Timeout and semantic/schema failures are not infrastructure retries.
        if (parsed["substantive_response"] or parsed["tool_violations"] or timed_out or
                parsed["turn_completed"] or attempt_number == 2):
            break
        print(json.dumps({"infrastructure_retry": str(call_dir.relative_to(HERE)), "attempt": attempt_number}), flush=True)
    return {"attempts": attempts}


def response(call):
    final = call["attempts"][-1]
    try:
        return json.loads(final.get("response_text") or "null")
    except (json.JSONDecodeError, TypeError):
        return None


def call_ok(call):
    final = call["attempts"][-1]
    return final["exit_code"] == 0 and final["turn_completed"] and not any(
        a["tool_violations"] for a in call["attempts"])


def service_failed(call):
    final = call["attempts"][-1]
    return (len(call["attempts"]) == 2 and not final["turn_completed"] and
            not final["substantive_response"] and not final["timed_out"] and
            not final["tool_violations"])


def score_fluency(answer):
    if not isinstance(answer, dict):
        return False
    actual = answer.get("fluency", answer)
    expected = tasks.expected_fluency()
    # JSON equality alone would accept True as 1. Canonical JSON preserves types.
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def run(out, isolated_root):
    if out.exists():
        raise SystemExit("Refusing to overwrite an existing run; partial runs require explicit audit, not implicit reruns.")
    if git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Commit the frozen harness before participant execution.")
    hashes = source_hashes()
    for source, digest in hashes.items():
        committed = subprocess.run(["git", "show", f"HEAD:{source}"], cwd=ROOT, capture_output=True)
        if committed.returncode or hashlib.sha256(committed.stdout).hexdigest() != digest:
            raise SystemExit(f"Source not frozen in HEAD: {source}")
    subprocess.run(["git", "merge-base", "--is-ancestor", PLAN_COMMIT, "HEAD"], cwd=ROOT, check=True)
    remote_sha = git("ls-remote", "origin", "refs/heads/research/ain-fluency-current-agents").split()[0]
    if remote_sha != git("rev-parse", "HEAD"):
        raise SystemExit("Push the frozen harness first.")
    version = subprocess.check_output([shutil.which("codex"), "--version"], text=True).strip()
    manifest = {"protocol": 1, "plan_commit": PLAN_COMMIT, "harness_commit": git("rev-parse", "HEAD"),
                "source_sha256": hashes, "model": MODEL, "effort": EFFORT,
                "codex_version": version, "python": platform.python_version(), "seed": SEED,
                "timeout_seconds": TIMEOUT, "started_utc": datetime.now(timezone.utc).isoformat(),
                "order": schedule(), "billing_dollars": None,
                "preparation": "Separate graded call, full prompt/response replayed in task context.",
                "scope": "In-context simulation; not trained-native weights or tokenizer changes.",
                "status": "running"}
    dump(out / "manifest.json", manifest)
    predecessors = {}
    for assignment in manifest["order"]:
        if source_hashes() != hashes:
            manifest.update(status="tainted_source_changed", stopped_at=assignment["id"])
            dump(out / "manifest.json", manifest)
            raise SystemExit("Frozen source changed during execution; stopping, preserving prior calls.")
        stage_dir = out / "stages" / assignment["id"]
        stage_dir.mkdir(parents=True)
        mode, stage, delta = assignment["mode"], assignment["stage"], assignment["delta"]
        fallback, genuine = False, True
        provenance = {"kind": "not_applicable"}
        prior = None
        if stage != "build":
            preceding = predecessors[(mode, delta)]
            if preceding["stage_passed"]:
                prior = (out / preceding["artifact_path"]).read_text(encoding="utf-8")
            else:
                prior = tasks.canonical_program(mode, "build" if stage == "change" else "change", delta)
                fallback, genuine = True, False
                provenance = {"kind": "failed_predecessor_canonical_fallback", "predecessor": preceding["id"]}
            if stage == "repair":
                prior = tasks.corrupt_artifact(prior, mode, delta)
                corruption = tasks.corruption_info()
                provenance = {**provenance, "corruption": corruption}
                injection_fallback = bool(corruption.get("fallback", corruption.get("used_fallback", False)))
                fallback = fallback or injection_fallback
                genuine = genuine and not injection_fallback
                genuine = genuine and corruption.get("mutation_count") == 3 and corruption.get("syntax_valid") is True
                # Confirm supplied broken work is actually rejected; no answer feedback goes to model.
                broken_path = stage_dir / ("supplied-broken.py" if mode == "python" else "supplied-broken.json")
                broken_path.write_text(prior, encoding="utf-8", newline="\n")
                broken_check = judge_artifact(broken_path, mode, stage, delta)
                dump(stage_dir / "supplied-broken-judge.json", broken_check)
                if broken_check.get("passed"):
                    genuine = False
                    provenance["fault_validation_failed"] = True
                standalone_checks = {}
                for fault, variant in tasks.corruption_variants(
                        tasks.canonical_program(mode, "change", delta) if fallback else
                        (out / preceding["artifact_path"]).read_text(encoding="utf-8"), mode, delta).items():
                    variant_path = stage_dir / (fault + (".py" if mode == "python" else ".json"))
                    variant_path.write_text(variant, encoding="utf-8", newline="\n")
                    checked = judge_artifact(variant_path, mode, stage, delta)
                    dump(stage_dir / (fault + "-judge.json"), checked)
                    standalone_checks[fault] = {
                        "rejected": checked.get("passed") is False and checked.get("cases") == 55
                        and 0 < checked.get("passed_cases", 0) < 55,
                        "passed_cases": checked.get("passed_cases"), "cases": checked.get("cases")}
                provenance["standalone_faults"] = standalone_checks
                if len(standalone_checks) != 3 or not all(x["rejected"] for x in standalone_checks.values()):
                    genuine = False
                    provenance["fault_validation_failed"] = True
        if prior is not None:
            (stage_dir / "predecessor.txt").write_text(prior, encoding="utf-8", newline="\n")
        print(json.dumps({"starting": assignment, "fallback": fallback}), flush=True)
        prep_prompt = tasks.preparation_prompt_for(mode, stage, delta)
        prep_call = invoke(stage_dir / "preparation", prep_prompt, tasks.fluency_response_schema(), isolated_root)
        prep_response = response(prep_call)
        prep_passed = call_ok(prep_call) and score_fluency(prep_response)
        if service_failed(prep_call):
            record = {**assignment, "preparation_passed": False, "fluency_passed": False,
                      "preparation_call": prep_call, "task_call": {"attempts": []},
                      "judge": {"passed": False, "error": "TASK_NOT_RUN_SERVICE_FAILURE"},
                      "fallback": fallback, "genuine_handoff": genuine, "repair_provenance": provenance,
                      "stage_passed": False, "incomplete": True, "harness_failure": False}
            dump(stage_dir / "stage.json", record)
            manifest.update(status="incomplete_service_failure", stopped_at=assignment["id"])
            dump(out / "manifest.json", manifest)
            return
        task_prompt = ("This is a controlled experiment. Do not use tools, browse, read files or run commands. "
                       "Return only the requested JSON. The preparation transcript below is replayed from "
                       "a separate turn; it is context, not learned model weights.\n\n"
                       "<preparation_prompt>\n" + prep_prompt + "\n</preparation_prompt>\n"
                       "<preparation_response>\n" + (prep_call["attempts"][-1].get("response_text") or "[No valid response]") +
                       "\n</preparation_response>\n\n" + tasks.prompt_for(mode, stage, delta, prior_artifact=prior))
        task_call = invoke(stage_dir / "task", task_prompt, tasks.response_schema(), isolated_root)
        answer = response(task_call)
        fluency_passed = score_fluency(answer)
        program = answer.get("program") if isinstance(answer, dict) else None
        artifact_path = stage_dir / ("artifact.py" if mode == "python" else "artifact.json")
        if isinstance(program, str):
            artifact_path.write_text(program, encoding="utf-8", newline="\n")
            judged = judge_artifact(artifact_path, mode, stage, delta)
        else:
            judged = {"passed": False, "error": "MISSING_PROGRAM"}
        dump(stage_dir / "judge.json", judged)
        oracle_failed = any(d.get("oracle_manual_gate") is False for d in judged.get("details", []))
        infrastructure_error = judged.get("error") == "INVALID_JUDGE_OUTPUT"
        record = {**assignment, "preparation_passed": prep_passed, "fluency_passed": fluency_passed,
                  "preparation_call": prep_call, "task_call": task_call, "judge": judged,
                  "harness_failure": bool(oracle_failed or infrastructure_error),
                  "fallback": fallback, "genuine_handoff": genuine, "repair_provenance": provenance,
                  "artifact_path": str(artifact_path.relative_to(out)).replace("\\", "/"),
                  "stage_passed": bool(prep_passed and fluency_passed and call_ok(task_call) and judged.get("passed"))}
        dump(stage_dir / "stage.json", record)
        predecessors[(mode, delta)] = record
        manifest["completed_stages"] = len(list((out / "stages").glob("*/stage.json")))
        dump(out / "manifest.json", manifest)
        print(json.dumps({"finished": assignment["id"], "preparation_passed": prep_passed,
                          "stage_passed": record["stage_passed"], "passed_cases": judged.get("passed_cases"),
                          "cases": judged.get("cases"), "fallback": fallback}), flush=True)
        if service_failed(task_call):
            manifest.update(status="incomplete_service_failure", stopped_at=assignment["id"])
            dump(out / "manifest.json", manifest)
            return
    if source_hashes() != hashes:
        manifest.update(status="tainted_source_changed")
        dump(out / "manifest.json", manifest)
        raise SystemExit("Frozen source changed; results tainted.")
    manifest["status"] = "complete"
    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    dump(out / "manifest.json", manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Make the 36 preregistered participant calls.")
    parser.add_argument("--output", type=Path, default=HERE / "results" / "current-agent-2026-11-06")
    parser.add_argument("--isolated-root", type=Path, default=ROOT.parent / "participant-cells")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({"schedule": schedule(), "planned_calls": 36, "no_participants_run": True}, indent=2))
    else:
        run(args.output.resolve(), args.isolated_root.resolve())
