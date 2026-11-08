"""Operational v1.1 continuation; preserve original partial data and frozen code."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))
import run as frozen
from judge import judge_artifact
import tasks

ORIGINAL = STUDY / "results/current-agent-2026-11-06"
OUTPUT = STUDY / "results/current-agent-2026-11-06-continuation"
CELLS = frozen.ROOT.parent / "participant-cells-continuation"


def hashes():
    return {str(p.relative_to(frozen.ROOT)).replace("\\", "/"):
            hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), HERE / "AMENDMENT.md", HERE / "test_resume.py")}


def dataset_hashes():
    return {p.relative_to(ORIGINAL).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(ORIGINAL.rglob("*")) if p.is_file()}


def empty_service_rejection(attempt):
    return (not attempt["turn_completed"] and not attempt["substantive_response"]
            and not attempt["timed_out"] and not attempt["tool_violations"])


def task_prompt_for(prep_prompt, prep_response, mode, stage, delta, prior):
    return ("This is a controlled experiment. Do not use tools, browse, read files or run commands. "
            "Return only the requested JSON. The preparation transcript below is replayed from "
            "a separate turn; it is context, not learned model weights.\n\n"
            "<preparation_prompt>\n" + prep_prompt + "\n</preparation_prompt>\n"
            "<preparation_response>\n" + (prep_response or "[No valid response]") +
            "\n</preparation_response>\n\n" + tasks.prompt_for(mode, stage, delta, prior_artifact=prior))


def one_request(call_dir, prompt, schema):
    """Exactly one post-reset request for the already-exhausted infrastructure slot."""
    call_dir.mkdir(parents=True, exist_ok=False)
    (call_dir / "prompt.txt").write_text(prompt, encoding="utf-8", newline="\n")
    frozen.dump(call_dir / "schema.json", schema)
    cell = CELLS / "d30-repair-ain/task-after-reset"
    cell.mkdir(parents=True, exist_ok=False)
    frozen.dump(cell / "response-schema.json", schema)
    command = [shutil.which("codex"), "exec", "--json", "--ephemeral", "--ignore-user-config",
               "--model", frozen.MODEL, "-c", f'model_reasoning_effort="{frozen.EFFORT}"',
               "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
               "--output-schema", str(cell / "response-schema.json"), "-C", str(cell), "-"]
    started = time.perf_counter()
    timed_out = False
    try:
        process = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                 encoding="utf-8", timeout=frozen.TIMEOUT)
        stdout, stderr, code = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as error:
        timed_out, code = True, None
        stdout, stderr = error.stdout or "", error.stderr or ""
        if isinstance(stdout, bytes): stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes): stderr = stderr.decode("utf-8", errors="replace")
    attempt = {"attempt": 3, "elapsed_seconds": time.perf_counter()-started,
               "exit_code": code, "timed_out": timed_out, **frozen.parse_events(stdout),
               "stderr_bytes": len(stderr.encode("utf-8")),
               "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
               "raw_events": "task-continuation/attempt-3.jsonl"}
    (cell / "stderr-private.log").write_text(stderr, encoding="utf-8", newline="\n")
    (call_dir / "attempt-3.jsonl").write_text(stdout, encoding="utf-8", newline="\n")
    result = {"attempts": [attempt]}
    frozen.dump(call_dir / "call.json", result)
    return result


def save_scored(stage_dir, assignment, prep_call, task_call, base):
    answer = frozen.response(task_call)
    program = answer.get("program") if isinstance(answer, dict) else None
    path = stage_dir / ("artifact.py" if assignment["mode"] == "python" else "artifact.json")
    if isinstance(program, str):
        path.write_text(program, encoding="utf-8", newline="\n")
        judged = judge_artifact(path, assignment["mode"], assignment["stage"], assignment["delta"])
    else:
        judged = {"passed": False, "error": "MISSING_PROGRAM"}
    prep_pass = frozen.call_ok(prep_call) and frozen.score_fluency(frozen.response(prep_call))
    fluency_pass = frozen.score_fluency(answer)
    record = {**assignment, **base, "preparation_call": prep_call, "task_call": task_call,
              "preparation_passed": prep_pass, "fluency_passed": fluency_pass, "judge": judged,
              "artifact_path": str(path.relative_to(OUTPUT)).replace("\\", "/"),
              "harness_failure": any(d.get("oracle_manual_gate") is False for d in judged.get("details", []))
              or judged.get("error") == "INVALID_JUDGE_OUTPUT",
              "stage_passed": bool(prep_pass and fluency_pass and frozen.call_ok(task_call) and judged.get("passed"))}
    frozen.dump(stage_dir / "judge.json", judged)
    frozen.dump(stage_dir / "stage.json", record)
    print(json.dumps({"finished": assignment["id"], "passed": record["stage_passed"],
                      "cases": judged.get("passed_cases"), "fallback": record["fallback"]}), flush=True)
    return record


def main():
    original_manifest = json.loads((ORIGINAL / "manifest.json").read_text(encoding="utf-8"))
    original_hashes = original_manifest["source_sha256"]
    adapter_hashes = hashes()
    original_data_hashes = dataset_hashes()
    def guard():
        if (frozen.source_hashes() != original_hashes or hashes() != adapter_hashes
                or dataset_hashes() != original_data_hashes):
            raise SystemExit("Frozen source changed; stop and preserve all records.")
    guard()
    version = subprocess.check_output([shutil.which("codex"), "--version"], text=True).strip()
    if version != original_manifest["codex_version"]:
        raise SystemExit("CLI version changed; publish a further amendment before execution.")
    if original_manifest["status"] != "incomplete_service_failure" or original_manifest["stopped_at"] != "d30-repair-ain":
        raise SystemExit("Unexpected original stopping point.")
    if OUTPUT.exists(): raise SystemExit("Refusing to overwrite a continuation.")
    if frozen.git("status", "--porcelain", "--untracked-files=no"):
        raise SystemExit("Commit and push continuation first.")
    head = frozen.git("rev-parse", "HEAD")
    if frozen.git("ls-remote", "origin", "refs/heads/research/ain-fluency-current-agents").split()[0] != head:
        raise SystemExit("Push continuation first.")
    for name, digest in adapter_hashes.items():
        data = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=frozen.ROOT)
        if hashlib.sha256(data).hexdigest() != digest: raise SystemExit("Adapter is not frozen in HEAD.")
    shutil.copytree(ORIGINAL, OUTPUT)
    manifest = {**original_manifest, "protocol": "1.1 operational continuation", "status": "running",
                "original_status": original_manifest["status"], "continuation_commit": head,
                "continuation_source_sha256": adapter_hashes,
                "original_dataset_sha256": original_data_hashes,
                "original_manifest_sha256": hashlib.sha256((ORIGINAL / "manifest.json").read_bytes()).hexdigest(),
                "continued_utc": datetime.now(timezone.utc).isoformat(),
                "note": "Original records are reused, not independent replications. Two quota failures have unknown usage."}
    def save_manifest(status="running"):
        manifest.update(status=status, completed_stages=len(list((OUTPUT / "stages").glob("*/stage.json"))))
        frozen.dump(OUTPUT / "manifest.json", manifest)
    save_manifest()
    assignment = original_manifest["order"][7]
    stage_dir = OUTPUT / "stages" / assignment["id"]
    previous = json.loads((stage_dir / "stage.json").read_text(encoding="utf-8"))
    shutil.copy2(stage_dir / "stage.json", stage_dir / "stage-before-continuation.json")
    print(json.dumps({"continuing": assignment["id"], "same_saved_prompt": True}), flush=True)
    continued = one_request(stage_dir / "task-continuation",
                            (stage_dir / "task/prompt.txt").read_text(encoding="utf-8"),
                            json.loads((stage_dir / "task/schema.json").read_text(encoding="utf-8")))
    combined = {"attempts": previous["task_call"]["attempts"] + continued["attempts"]}
    record = save_scored(stage_dir, assignment, previous["preparation_call"], combined,
                         {key: previous[key] for key in ("fallback", "genuine_handoff", "repair_provenance")})
    guard()
    if empty_service_rejection(continued["attempts"][-1]):
        save_manifest("incomplete_service_failure"); return
    predecessors = {}
    for earlier in original_manifest["order"][:8]:
        item = json.loads((OUTPUT / "stages" / earlier["id"] / "stage.json").read_text(encoding="utf-8"))
        predecessors[(item["mode"], item["delta"])] = item
    for assignment in original_manifest["order"][8:]:
        guard()
        mode, stage, delta = assignment["mode"], assignment["stage"], assignment["delta"]
        stage_dir = OUTPUT / "stages" / assignment["id"]
        stage_dir.mkdir(parents=True, exist_ok=False)
        fallback, genuine, prior = False, True, None
        provenance = {"kind": "not_applicable"}
        if stage != "build":
            preceding = predecessors[(mode, delta)]
            if preceding["stage_passed"]:
                prior = (OUTPUT / preceding["artifact_path"]).read_text(encoding="utf-8")
            else:
                prior = tasks.canonical_program(mode, "build" if stage == "change" else "change", delta)
                fallback, genuine = True, False
                provenance = {"kind": "failed_predecessor_canonical_fallback", "predecessor": preceding["id"]}
            if stage == "repair":
                mutation_source = prior
                prior = tasks.corrupt_artifact(prior, mode, delta)
                info = tasks.corruption_info()
                provenance["corruption"] = info
                fallback = fallback or info["fallback"]
                genuine = genuine and not info["fallback"] and info["mutation_count"] == 3 and info["syntax_valid"]
                broken = stage_dir / ("supplied-broken.py" if mode == "python" else "supplied-broken.json")
                broken.write_text(prior, encoding="utf-8", newline="\n")
                judged = judge_artifact(broken, mode, stage, delta)
                frozen.dump(stage_dir / "supplied-broken-judge.json", judged)
                checks = {}
                for fault, variant in tasks.corruption_variants(mutation_source, mode, delta).items():
                    path = stage_dir / (fault + (".py" if mode == "python" else ".json"))
                    path.write_text(variant, encoding="utf-8", newline="\n")
                    checked = judge_artifact(path, mode, stage, delta)
                    frozen.dump(stage_dir / (fault + "-judge.json"), checked)
                    checks[fault] = {"rejected": checked.get("passed") is False and checked.get("cases") == 55
                                     and 0 < checked.get("passed_cases", 0) < 55,
                                     "passed_cases": checked.get("passed_cases"), "cases": checked.get("cases")}
                provenance["standalone_faults"] = checks
                if judged.get("passed") or len(checks) != 3 or not all(x["rejected"] for x in checks.values()):
                    genuine = False; provenance["fault_validation_failed"] = True
        if prior is not None: (stage_dir / "predecessor.txt").write_text(prior, encoding="utf-8", newline="\n")
        print(json.dumps({"starting": assignment, "fallback": fallback}), flush=True)
        prep_prompt = tasks.preparation_prompt_for(mode, stage, delta)
        prep_call = frozen.invoke(stage_dir / "preparation", prep_prompt, tasks.fluency_response_schema(), CELLS)
        base = {"fallback": fallback, "genuine_handoff": genuine, "repair_provenance": provenance}
        if frozen.service_failed(prep_call):
            frozen.dump(stage_dir / "stage.json", {**assignment, **base, "preparation_call": prep_call,
                        "task_call": {"attempts": []}, "preparation_passed": False, "fluency_passed": False,
                        "stage_passed": False, "judge": {"passed": False, "error": "TASK_NOT_RUN_SERVICE_FAILURE"}})
            save_manifest("incomplete_service_failure"); return
        prompt = task_prompt_for(prep_prompt, prep_call["attempts"][-1].get("response_text"), mode, stage, delta, prior)
        task_call = frozen.invoke(stage_dir / "task", prompt, tasks.response_schema(), CELLS)
        record = save_scored(stage_dir, assignment, prep_call, task_call, base)
        predecessors[(mode, delta)] = record
        save_manifest()
        if frozen.service_failed(task_call): save_manifest("incomplete_service_failure"); return
    guard()
    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
    save_manifest("complete_amended_continuation")


if __name__ == "__main__":
    if sys.argv[1:] != ["--execute"]:
        raise SystemExit("Use --execute after publishing AMENDMENT.md and this adapter. No calls made.")
    main()
