"""Deterministic parent-side judge for the current-agent fluency development study.

The oracle has independently written control flow over the frozen shared host.
Hand-derived expectations additionally check important shared-host obligations.
Python participants are trusted/cooperative, not securely sandboxed adversaries.
The complete suite runs in a fresh subprocess with a wall-clock cap.
"""
from __future__ import annotations

import argparse
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import threading

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent / "ain_v0"
sys.path.insert(0, str(STUDY))
from ain.engine import Host, Sink, WorkflowError
from ain.language import loads_json, run_ir, run_ain

FUEL = 200_000
ARTIFACT_LIMIT = 128 * 1024
TIMEOUT = 45
GROUP_FIELDS = ("tenant", "device", "kind", "message", "first_timestamp",
                "last_timestamp", "first_offset", "count", "severity_sum")


def event(offset, event_id, timestamp, severity=1, **fields):
    return {"offset": offset, "kind": "event", "event": {
        "tenant": fields.get("tenant", "t"), "event_id": event_id,
        "timestamp": timestamp, "severity": severity,
        "device": fields.get("device", "pump"), "kind": fields.get("kind", "alert"),
        "message": fields.get("message", "m")}}


def watermark(offset, timestamp):
    return {"offset": offset, "kind": "watermark", "timestamp": timestamp}


def end(offset):
    return {"offset": offset, "kind": "end"}


def _policy(group, version, token):
    return 77, 2


_policy.version = "fixture-v1"


def reference(host, stage="build", delta=30):
    """Independent imperative orchestration, not imported workflow source."""
    operations = {number: record["fn"] for number, record in host.catalog().items()}
    state = operations[0](host)
    while operations[1](host):
        operations[3](host)
        row = operations[2](host)
        operations[4](host, state, row)
        category = operations[5](row)
        if category != 0:
            operations[15](host, state, row)
            while operations[16](host, state):
                pending = operations[17](host, state)
                operations[18](host, state, pending)
            groups = operations[19](host, state)
            reports = operations[20](host, state, groups)
            operations[21](host, state, reports)
            continue
        timestamp = operations[7](row)
        cutoff = operations[6](state)
        if timestamp < cutoff:
            operations[14](host, state, 0)
            continue
        if operations[8](host, state, row):
            operations[14](host, state, 1)
            continue
        operations[9](host, state, row)
        threshold = operations[11](host)
        if stage != "build" and timestamp - cutoff < delta:
            threshold = min(3, threshold + 1)
        cleaned = operations[12](row)
        if operations[10](cleaned) < threshold:
            operations[14](host, state, 2)
            continue
        operations[13](host, state, cleaned)
        operations[14](host, state, 3)
    return operations[22](host, state)


def _load_python(path):
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    banned_names = {"eval", "exec", "compile", "open", "input", "globals", "locals",
                    "vars", "getattr", "setattr", "delattr", "breakpoint", "help", "exit", "quit"}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Global, ast.Nonlocal,
                             ast.ClassDef, ast.AsyncFunctionDef, ast.Await)):
            raise ValueError("Python source uses a disallowed construct: " + type(node).__name__)
        if isinstance(node, ast.Name) and (node.id in banned_names or node.id.startswith("__")):
            raise ValueError("Python source uses a disallowed name")
        if isinstance(node, ast.Attribute) and node.attr not in {"catalog", "values", "items", "get"}:
            raise ValueError("Python must access the host only through catalog capabilities")
    allowed = {"dict": dict, "list": list, "tuple": tuple, "set": set,
               "min": min, "max": max, "len": len, "range": range, "enumerate": enumerate,
               "zip": zip, "int": int, "bool": bool, "str": str, "abs": abs}
    namespace = {"__builtins__": allowed}
    exec(compile(tree, str(path), "exec"), namespace)
    run = namespace.get("run")
    if not callable(run):
        raise ValueError("Python artifact must define run(host)")
    return run


def _load(path, mode):
    if path.stat().st_size > ARTIFACT_LIMIT:
        raise ValueError("artifact exceeds 128 KiB limit")
    if mode == "python":
        return _load_python(path)
    document = loads_json(path.read_text(encoding="utf-8"))
    if mode == "ir":
        return lambda host: run_ir(document, host.catalog(), [host], fuel=FUEL)
    if mode == "ain":
        return lambda host: run_ain(document, host.catalog(), [host], fuel=FUEL)
    raise ValueError("unknown mode")


def _instrument(host):
    """Observe required program-level checks without demanding cosmetic call order."""
    original = host.catalog()
    audit = {"cancel_before_read": False, "validated": set(), "violations": []}
    catalog = {}
    for number, operation in original.items():
        fn = operation["fn"]
        def call(*args, _number=number, _fn=fn):
            if _number == 3:
                audit["cancel_before_read"] = True
            if _number == 2:
                if not audit["cancel_before_read"]:
                    audit["violations"].append("missing cancellation check before source admission")
                audit["cancel_before_read"] = False
            if _number in {5, 7, 8, 9, 10, 12, 13}:
                row = args[-1] if _number in {8, 9, 13} else args[0]
                if type(row) is dict and row.get("offset") not in audit["validated"]:
                    audit["violations"].append("record inspected/processed before complete validation")
            value = _fn(*args)
            if _number == 4:
                audit["validated"].add(args[-1]["offset"])
            return value
        catalog[number] = {**operation, "fn": call}
    host.catalog = lambda: catalog
    return audit


def _options(kind):
    options = {"policy": _policy}
    if kind == "authority_policy":
        options["authority"] = lambda stage, group: stage != "policy"
    elif kind == "authority_commit":
        options["authority"] = lambda stage, group: stage != "precommit"
    elif kind == "cancel_before":
        token = threading.Event(); token.set(); options["cancel"] = token
    elif kind == "cancel_policy":
        token = threading.Event()
        def policy(group, version, cooperative):
            token.set()
            raise ValueError("fixture failure hidden by cancellation")
        options.update(cancel=token, policy=policy)
    elif kind == "policy_error":
        def policy(group, version, cooperative):
            raise ValueError("declared local fixture error")
        options["policy"] = policy
    elif kind == "invalid_policy":
        options["policy"] = lambda group, version, token: (True, 0)
    elif kind == "scope":
        options["allowed_tenants"] = ["other"]
    return options


def _execute(run, records, config=None, sink=None, options_kind=None, fault=None):
    host = None
    try:
        options = _options(options_kind)
        if fault:
            options["fault"] = fault
        host = Host(deepcopy(records), config=config, sink=sink, **options)
        audit = _instrument(host)
        returned = run(host)
        canonical = host.outcome()
        return returned, canonical, audit["violations"]
    except WorkflowError as error:
        outcome = host.outcome(error) if host else Host.error_result(error, sink=sink)
        return outcome, outcome, audit["violations"] if host else []


def _summary(result):
    return {"status": result.get("status"), "error": result.get("error"),
            "counters": result.get("counters"),
            "groups": [{key: row[key] for key in GROUP_FIELDS} for row in result.get("reports", [])],
            "commits": [row["epoch_offset"] for row in result.get("trace", [])],
            "cursor": (result.get("checkpoint") or {}).get("cursor")}


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _cases(delta):
    cases = []
    def add(name, records, **kwargs):
        cases.append({"name": name, "records": records, **kwargs})
    add("published_ten_record_trace", [event(1,"A",100,0), event(2,"A",90,3),
        event(3,"B",200,2), event(4,"C",150,1), watermark(5,900), event(6,"D",779,3),
        event(7,"D",780,3), watermark(8,1500), event(9,"A",1400,2), end(10)])
    for minimum in range(4):
        add("near_frontier_manual_minimum_"+str(minimum), [watermark(1,900),
            event(2,"L",779,3), event(3,"N",780,minimum), event(4,"N",781,3),
            event(5,"X",780+delta-1,minimum), event(6,"B",780+delta,minimum),
            event(7,"F",780+delta+1,3), end(8)], config={"minimum":minimum},
            manual="near", minimum=minimum)
    add("drain_many_tied_and_out_of_order", [event(1,"A",200,3), event(2,"B",100,3),
        event(3,"C",100,2), event(4,"D",800,3), end(5)])
    add("nfkc_and_message_case", [event(1,"A",100,3,device=" ＰＵＭＰ\t",kind=" ALERT ",message="a\tb"),
        event(2,"B",101,3,device="pump",kind="alert",message="a b"),
        event(3,"C",102,3,device="pump",message="A b"),end(4)])
    add("anchored_window_equality",[event(1,"A",100,3),event(2,"B",699,3),
        event(3,"C",700,3),end(4)])
    add("first_id_before_threshold",[event(1,"A",0,0),event(2,"A",1,3),event(3,"B",200,3),end(4)])
    add("late_id_not_reserved",[watermark(1,900),event(2,"A",779,3),event(3,"A",780,3),end(4)])
    add("horizon_readmission",[event(1,"A",100,3),watermark(2,1420),event(3,"A",1300,3),end(4)])
    add("frontier_equal_waits",[event(1,"A",780,3),watermark(2,900),end(3)])
    add("eof_not_end",[event(1,"A",100,3),watermark(2,900),event(3,"B",1000,3)])
    add("empty_input",[])
    add("empty_end",[end(1)])
    add("after_end_same_invocation",[end(1),event(2,"A",0,3)])
    add("invalid_duplicate_payload",[event(1,"A",100,0),event(2,"A",101,True),end(3)])
    add("invalid_late_payload",[watermark(1,900),event(2,"A",0,True),end(3)])
    add("future_invalid_preserves_commit",[watermark(1,0),event(2,"A",0,True)])
    add("decreasing_watermark",[watermark(1,500),watermark(2,499)])
    add("duplicate_offset",[event(1,"A",100,3),event(1,"B",101,3),end(2)])
    add("signed_timestamp_maximum",[event(1,"A",2**63-1,3),end(2)])
    for resource in ("dedupe_entries","buffered_events","open_groups","epoch_reports"):
        if resource in ("dedupe_entries","buffered_events"):
            records=[event(1,"A",100,3),event(2,"B",101,3),end(3)]
        else:
            records=[event(1,"A",100,3,device="a"),event(2,"B",101,3,device="b"),end(3)]
        add("capacity_"+resource,records,config={resource:1})
    for kind in ("authority_policy","authority_commit","cancel_before","cancel_policy",
                 "policy_error","invalid_policy","scope"):
        add(kind,[event(1,"A",100,3),end(2)],options_kind=kind)
    for seed in range(20):
        rng=random.Random(880000+delta*100+seed)
        records=[]; water=0
        for _ in range(50):
            if rng.random()<.18:
                water += rng.randrange(0,200)
                row=watermark(len(records)+1,water)
            else:
                row=event(len(records)+1,str(rng.randrange(18)),max(0,water+rng.randrange(-200,250)),
                          rng.randrange(4),tenant=rng.choice(("t","T")),
                          device=rng.choice((" ＰＵＭＰ ","pump","motor")),
                          message=rng.choice(("a\tb","a b","A b")))
            records.append(row)
        records.append(end(len(records)+1))
        add("generated_"+str(seed),records,config={"minimum":seed%4})
    return cases


def _manual_check(case, result, stage, delta):
    # Explicit outcomes prevent a shared-host failure from silently turning an
    # intended error fixture into a vacuous agreement between two controllers.
    name = case["name"]
    errors = {"authority_policy": "AUTHORITY", "authority_commit": "AUTHORITY",
              "scope": "AUTHORITY", "cancel_before": "CANCELLED",
              "cancel_policy": "CANCELLED", "policy_error": "POLICY",
              "invalid_policy": "POLICY", "invalid_duplicate_payload": "VALIDATION",
              "invalid_late_payload": "VALIDATION", "future_invalid_preserves_commit": "VALIDATION",
              "decreasing_watermark": "VALIDATION", "duplicate_offset": "VALIDATION",
              "after_end_same_invocation": "VALIDATION"}
    code = "CAPACITY" if name.startswith("capacity_") else errors.get(name)
    if code:
        if result.get("error", {}).get("code") != code:
            return False
        if name == "future_invalid_preserves_commit":
            return [row["epoch_offset"] for row in result["trace"]] == [1]
        return True
    if name == "eof_not_end":
        return result["status"] == "INCOMPLETE" and result["checkpoint"]["cursor"] == 2
    if name == "drain_many_tied_and_out_of_order":
        return (result["status"] == "COMPLETE" and
                [(row["first_timestamp"], row["first_offset"], row["count"], row["severity_sum"])
                 for row in result["reports"]] == [(100, 2, 3, 8), (800, 4, 1, 3)] and
                [row["epoch_offset"] for row in result["trace"]] == [5])
    if case.get("manual") != "near":
        return True
    minimum=case["minimum"]
    increased=stage!="build" and minimum<3
    accepted=2 if increased else 4
    first=780+delta if increased else 780
    first_offset=6 if increased else 3
    expected={"late":1,"duplicate":1,"filtered":2 if increased else 0,"accepted":accepted}
    groups=result["reports"]
    return (result["status"]=="COMPLETE" and result["counters"]==expected and len(groups)==1 and
            groups[0]["count"]==accepted and groups[0]["severity_sum"]==
            (minimum+3 if increased else minimum*3+3) and
            groups[0]["first_timestamp"]==first and groups[0]["last_timestamp"]==781+delta and
            groups[0]["first_offset"]==first_offset and
            [t["epoch_offset"] for t in result["trace"]]==[1,8])


def _worker(path, mode, stage, delta):
    run=_load(path,mode)
    oracle=lambda host:reference(host,stage,delta)
    details=[]
    for case in _cases(delta):
        name=case["name"]
        try:
            kwargs={key:case[key] for key in ("config","options_kind") if key in case}
            expected, expected_state, oracle_audit=_execute(oracle,case["records"],**kwargs)
            actual, actual_state, audit=_execute(run,case["records"],**kwargs)
            oracle_ok=expected==expected_state and not oracle_audit and _manual_check(case,expected,stage,delta)
            passed=oracle_ok and actual==expected and actual_state==expected and not audit
            details.append({"case":name,"passed":passed,"oracle_manual_gate":oracle_ok,
                            "actual_sha256":_hash(actual),"expected_sha256":_hash(expected),
                            "violations":audit,
                            **({} if passed else {"actual":_summary(actual),"expected":_summary(expected)})})
        except Exception as error:
            details.append({"case":name,"passed":False,"exception":type(error).__name__,
                            "message":str(error)[:400]})
    # Two restarts test durable checkpoints, not just final numeric output.
    recovery_rows=[event(1,"A",100,3),watermark(2,900),event(3,"B",1000,3),end(4)]
    for fault in ("before_commit","after_commit"):
        try:
            expected_sink=Sink(); actual_sink=Sink()
            expected_fault, expected_fault_state, expected_fault_audit = _execute(
                oracle,recovery_rows,sink=expected_sink,fault=fault)
            expected,_,expected_audit=_execute(oracle,recovery_rows,sink=expected_sink)
            actual_fault, actual_fault_state, fault_audit = _execute(
                run,recovery_rows,sink=actual_sink,fault=fault)
            actual,actual_state,audit=_execute(run,recovery_rows,sink=actual_sink)
            expected_code = "CRASH_BEFORE_COMMIT" if fault == "before_commit" else "LOST_ACK"
            # Compare the failed prefix as well as the successful replay.
            passed=(expected_fault.get("error", {}).get("code") == expected_code and
                    expected_fault == expected_fault_state and not expected_fault_audit and
                    actual_fault == expected_fault and actual_fault_state == expected_fault and
                    actual==expected and actual_state==expected and not audit and
                    not expected_audit and not fault_audit)
            details.append({"case":"recovery_"+fault,"passed":passed,
                            **({} if passed else {"actual":_summary(actual),"expected":_summary(expected),"violations":audit})})
        except Exception as error:
            details.append({"case":"recovery_"+fault,"passed":False,
                            "exception":type(error).__name__,"message":str(error)[:400]})
    return {"passed":all(d["passed"] for d in details),"cases":len(details),
            "passed_cases":sum(d["passed"] for d in details),"details":details,
            "mode":mode,"stage":stage,"delta":delta,
            "artifact_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def judge_artifact(path, mode="python", stage="build", delta=30):
    """Run a complete suite in one fresh bounded subprocess; always return a report."""
    path=Path(path).resolve()
    if mode not in {"python","ir","ain"} or stage not in {"build","change","repair"} or delta not in {30,75}:
        raise ValueError("invalid judge condition")
    try:
        run=subprocess.run([sys.executable,str(Path(__file__).resolve()),"--worker",str(path),
                            "--mode",mode,"--stage",stage,"--delta",str(delta)],
                           capture_output=True,text=True,encoding="utf-8",timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return {"passed":False,"mode":mode,"stage":stage,"delta":delta,
                "error":"JUDGE_TIMEOUT","timeout_seconds":TIMEOUT}
    try:
        report=json.loads(run.stdout)
    except json.JSONDecodeError:
        return {"passed":False,"error":"INVALID_JUDGE_OUTPUT","exit_code":run.returncode,
                "stderr":run.stderr[-1200:],"stdout":run.stdout[-1200:]}
    report["judge_exit_code"]=run.returncode
    if run.returncode:
        report["passed"]=False
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--worker",type=Path,required=True)
    parser.add_argument("--mode",choices=("python","ir","ain"),required=True)
    parser.add_argument("--stage",choices=("build","change","repair"),required=True)
    parser.add_argument("--delta",type=int,required=True)
    args=parser.parse_args()
    try:
        result=_worker(args.worker,args.mode,args.stage,args.delta)
    except Exception as error:
        result={"passed":False,"error":"ARTIFACT_LOAD_OR_JUDGE_ERROR",
                "exception":type(error).__name__,"message":str(error)[:800]}
    print(json.dumps(result,sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
