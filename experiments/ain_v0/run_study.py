"""Reproducible local engineering measurements; no external model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
import tracemalloc

ROOT = Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def source_manifest():
    paths = [ROOT / name for name in ("DEVELOPMENT_PROTOCOL.md", "run_study.py",
                                     "export_programs.py", "LANGUAGE.md", "ENGINE.md")]
    paths += sorted((ROOT / "ain").glob("*.py"))
    paths += sorted((ROOT / "tests").glob("*.py"))
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def generate(shape, count, seed=20261105):
    rng = random.Random(seed)
    out = []
    for i in range(count):
        stamp = i * 3 + rng.randrange(0, 60)
        if shape == "late_mix" and i % 5 == 0:
            stamp = max(0, stamp - 7000)
        key = i if shape == "many_keys" else i % 100
        event_id = i - 1 if i % 11 == 0 and i else i
        out.append({"offset": len(out) + 1, "kind": "event", "event": {
            "tenant": "t" + str(event_id % 4),
            "event_id": str(event_id),
            "timestamp": stamp, "severity": i % 4,
            "device": " ＰＵＭＰ\t" + str(key), "kind": " Alert ",
            "message": "Review\tissue " + str(key),
        }})
        if (i + 1) % 1000 == 0:
            out.append({"offset": len(out) + 1, "kind": "watermark", "timestamp": i * 3})
    out.append({"offset": len(out) + 1, "kind": "end"})
    return out


def peak_working_set():
    if os.name != "nt":
        return None
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    ctypes.windll.psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    ctypes.windll.psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
    return counters.PeakWorkingSetSize if ok else None


def worker(mode, shape, count, repetition):
    start = time.perf_counter()
    from ain.engine import Host
    from ain.reference import run
    from ain.language import run_ir, run_ain, validate_ir, decode_ain
    from ain.programs import workflow_ir, workflow_ain
    generation_start = time.perf_counter()
    records = generate(shape, count)
    generation_seconds = time.perf_counter() - generation_start
    preparation_start = time.perf_counter()
    catalog = Host([]).catalog()
    document = None if mode == "python" else workflow_ir() if mode == "ir" else workflow_ain(catalog)
    preparation_seconds = time.perf_counter() - preparation_start
    checking_start = time.perf_counter()
    if mode == "ir":
        validate_ir(document, catalog)
    elif mode == "ain":
        validate_ir(decode_ain(document, catalog), catalog)
    checking_seconds = time.perf_counter() - checking_start
    tracemalloc.start()
    execution_start, cpu_start = time.perf_counter(), time.process_time()
    host = Host(records)
    if mode == "python":
        result = run(host)
    elif mode == "ir":
        result = run_ir(document, host.catalog(), [host], fuel=100_000_000)
    else:
        result = run_ain(document, host.catalog(), [host], fuel=100_000_000)
    execution_seconds = time.perf_counter() - execution_start
    cpu_seconds = time.process_time() - cpu_start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if result["status"] != "COMPLETE":
        raise RuntimeError("Worker did not complete: " + repr(result.get("error")))
    result_hash = digest(result)
    print(json.dumps({
        "mode": mode, "shape": shape, "event_count": count, "record_count": len(records),
        "repetition": repetition, "generation_seconds": generation_seconds,
        "program_preparation_seconds": preparation_seconds,
        "separate_check_seconds": checking_seconds,
        "execution_including_host_and_check_seconds": execution_seconds,
        "execution_cpu_seconds": cpu_seconds, "python_allocation_peak_bytes": peak,
        "process_peak_working_set_bytes": peak_working_set(),
        "worker_internal_seconds": time.perf_counter() - start,
        "result_sha256": result_hash, "report_count": len(result["reports"]),
        "counters": result["counters"], "status": result["status"],
    }, sort_keys=True))


def run_study(output, count, repetitions):
    output.mkdir(parents=True, exist_ok=False)
    manifest = source_manifest()
    environment = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "python": sys.version, "platform": platform.platform(),
                   "cpu_count": os.cpu_count(), "python_executable": str(Path(sys.executable).name),
                   "event_count": count, "repetitions": repetitions,
                   "seed": 20261105, "source_sha256": manifest,
                   "billed_tokens": None, "dollar_cost": None,
                   "timing_condition": "tracemalloc enabled during host construction and execution"}
    (output / "environment.json").write_bytes(canonical(environment) + b"\n")
    order = [(m, s, r) for m in ("python", "ir", "ain")
             for s in ("repeated_keys", "many_keys", "late_mix")
             for r in range(1, repetitions + 1)]
    random.Random(20261105).shuffle(order)
    rows, failures = [], []
    for index, (mode, shape, repetition) in enumerate(order, 1):
        print(f"Worker {index}/{len(order)}: {shape}, {mode}, repetition {repetition}", flush=True)
        begin = time.perf_counter()
        name = f"{index:02d}-{shape}-{mode}-{repetition}"
        failure = None
        try:
            proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--worker",
                                   "--mode", mode, "--shape", shape, "--events", str(count),
                                   "--repetition", str(repetition)], capture_output=True, text=True,
                                  encoding="utf-8", timeout=240)
            if proc.returncode:
                failure = {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
            else:
                try:
                    row = json.loads(proc.stdout)
                except json.JSONDecodeError as error:
                    failure = {"error": str(error), "stdout": proc.stdout, "stderr": proc.stderr}
        except subprocess.TimeoutExpired as error:
            def as_text(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value
            failure = {"error": "worker timeout", "stdout": as_text(error.stdout),
                       "stderr": as_text(error.stderr), "timeout_seconds": 240}
        if failure is not None:
            failure.update(name=name, mode=mode, shape=shape, repetition=repetition,
                           elapsed_seconds=time.perf_counter() - begin)
            failures.append(failure)
            (output / (name + "-failure.json")).write_bytes(canonical(failure) + b"\n")
            continue
        row["fresh_process_wall_seconds"] = time.perf_counter() - begin
        row["worker_order"] = index
        rows.append(row)
        (output / (name + ".json")).write_bytes(canonical(row) + b"\n")
    (output / "workers.json").write_bytes(canonical(rows) + b"\n")
    matches = {shape: len({row["result_sha256"] for row in rows if row["shape"] == shape}) == 1
               for shape in ("repeated_keys", "many_keys", "late_mix")}
    summary = {"workers": len(rows), "failures": len(failures), "output_matches": matches,
               "source_unchanged": source_manifest() == manifest}
    (output / "validation.json").write_bytes(canonical(summary) + b"\n")
    print(json.dumps(summary, indent=2))
    if failures or len(rows) != len(order) or not all(matches.values()) or not summary["source_unchanged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--mode", choices=("python", "ir", "ain"))
    parser.add_argument("--shape", choices=("repeated_keys", "many_keys", "late_mix"))
    parser.add_argument("--events", type=int, default=20_000)
    parser.add_argument("--repetition", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.worker:
        worker(args.mode, args.shape, args.events, args.repetition)
    else:
        run_study(args.output, args.events, args.repetitions)
