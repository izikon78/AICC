import json, subprocess
COLS = ["chars", "bytes", "o200k", "cl100k", "llama3", "qwen25", "deepseekv3", "gemma3"]
def count(d):
    r = subprocess.run(["node", "/home/claude/sym/count.js"], input=json.dumps(d), capture_output=True, text=True, cwd="/home/claude/sym")
    if r.returncode: raise RuntimeError(r.stderr[-800:])
    return json.loads(r.stdout)
def table(d, ref=None):
    res = count(d)
    w = max(len(k) for k in res) + 2
    print("name".ljust(w) + "".join(c.rjust(11) for c in COLS))
    for k, v in res.items():
        print(k.ljust(w) + "".join(str(v[c]).rjust(11) for c in COLS))
    return res
