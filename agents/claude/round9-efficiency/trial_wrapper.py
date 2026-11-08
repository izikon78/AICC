"""Runs one harness trial in-process and reports wall time, CPU time and peak RSS of THIS process as JSON on stderr."""
import json, os, resource, runpy, sys, time, io, contextlib
cwd, module_or_path, args = sys.argv[1], sys.argv[2], sys.argv[3:]
os.chdir(cwd); sys.path.insert(0, cwd)
t0, c0 = time.perf_counter(), time.process_time()
buf, rc = io.StringIO(), 0
with contextlib.redirect_stdout(buf):
    sys.argv = [module_or_path] + args
    try:
        (runpy.run_module(module_or_path, run_name="__main__") if not module_or_path.endswith(".py") else runpy.run_path(module_or_path, run_name="__main__"))
    except SystemExit as e: rc = e.code or 0
out = buf.getvalue()
try: d = json.loads(out); passed, total = d.get("passed"), d.get("total")
except Exception: passed = total = None
sys.stderr.write(json.dumps({"wall_ms": (time.perf_counter() - t0) * 1000, "cpu_ms": (time.process_time() - c0) * 1000,
                             "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, "passed": passed, "total": total, "rc": rc}) + "\n")
