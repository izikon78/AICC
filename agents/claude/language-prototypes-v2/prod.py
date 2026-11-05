import ast, io, json, keyword, subprocess, tokenize, sysconfig, os, builtins
import python_minifier
LIB = sysconfig.get_paths()["stdlib"]
FILES = ["textwrap.py", "shlex.py", "csv.py", "json/decoder.py", "json/encoder.py", "heapq.py", "bisect.py",
         "fractions.py", "statistics.py", "dataclasses.py", "argparse.py", "string.py"]
def toks(s):
    r = subprocess.run(["node", "tokstr.js"], input=s, capture_output=True, text=True); return json.loads(r.stdout)
def ntok(s): return len(toks(s)) if s else 0
def categories(src):
    """character -> category using Python's tokenizer"""
    cat = ["whitespace"] * len(src)
    lines = src.splitlines(keepends=True); starts = [0]
    for l in lines: starts.append(starts[-1] + len(l))
    off = lambda rc: starts[rc[0] - 1] + rc[1]
    prev_sig = tokenize.NEWLINE
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER): 
            if t.type in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT): prev_sig = t.type
            continue
        a, b = off(t.start), off(t.end)
        if t.type == tokenize.COMMENT: c = "comment"
        elif t.type == tokenize.STRING or t.type in getattr(tokenize, "FSTRING_START", -1) if False else t.type == tokenize.STRING:
            c = "docstring" if prev_sig in (tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT) and t.line.strip().startswith(t.string[:3]) and t.line.strip().endswith(t.string[-3:]) and len(t.string) > 2 and t.string.lstrip("rbuRBU")[:3] in ('"""', "'''") else "string"
        elif t.type == tokenize.NUMBER: c = "number"
        elif t.type == tokenize.NAME: c = "keyword" if keyword.iskeyword(t.string) or keyword.issoftkeyword(t.string) else "identifier"
        elif t.type == tokenize.OP: c = "operator/punctuation"
        else: c = "string" if "STRING" in tokenize.tok_name[t.type] else "operator/punctuation"
        for k in range(a, b): cat[k] = c
        prev_sig = t.type
    return cat
def b_estimate(src, keep_docstrings):
    tree = ast.parse(src); nodes = 0; text = []
    builtin_names = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Load, ast.Store, ast.Del, ast.expr_context)): continue
        nodes += 1
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            text.append(node.value)
        elif isinstance(node, ast.Attribute): text.append(node.attr)                 # external member names
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): text.append(node.name)
        elif isinstance(node, ast.keyword) and node.arg: text.append(node.arg)
        elif isinstance(node, ast.alias): text.append(node.name)
        elif isinstance(node, ast.Name) and (node.id in builtin_names): text.append(node.id)
    if not keep_docstrings:
        ds = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                d = ast.get_docstring(node, clean=False)
                if d: ds.add(d)
        text = [t for t in text if t not in ds]
    r = subprocess.run(["node", "countlist.js"], input=json.dumps(text), capture_output=True, text=True)
    return nodes, sum(json.loads(r.stdout))
tot = {"orig": 0, "min": 0, "b_doc": 0, "b_nodoc": 0}; catsum = {}
rows = []
for f in FILES:
    src = "".join(c if ord(c) < 128 else "x" for c in open(os.path.join(LIB, f)).read())   # ASCII-fold rare non-ASCII literals so token offsets are exact
    ts = toks(src); assert "".join(ts) == src, f
    cat = categories(src); pos = 0; ccount = {}
    for t in ts:
        nonws = [cat[k] for k in range(pos, pos + len(t)) if not src[k].isspace()]
        c = nonws[0] if nonws else "whitespace"
        ccount[c] = ccount.get(c, 0) + 1; pos += len(t)
    mn = python_minifier.minify(src, rename_locals=True, remove_literal_statements=True)
    nodes, ext = b_estimate(src, True); nodes2, ext2 = b_estimate(src, False)
    r = {"file": f, "orig": len(ts), "min": ntok(mn), "b_doc": nodes + ext, "b_nodoc": nodes2 + ext2}
    rows.append(r)
    for k in tot: tot[k] += r[k]
    for k, v in ccount.items(): catsum[k] = catsum.get(k, 0) + v
    print(f"{f:18s} orig {r['orig']:6d}  minified {r['min']:6d}  B-est(with docs) {r['b_doc']:6d}  B-est(no docs) {r['b_nodoc']:6d}")
print(f"{'TOTAL':18s} orig {tot['orig']:6d}  minified {tot['min']:6d}  B-est(with docs) {tot['b_doc']:6d}  B-est(no docs) {tot['b_nodoc']:6d}")
print(f"ratios: orig/minified {tot['orig']/tot['min']:.2f}  orig/B(no docs) {tot['orig']/tot['b_nodoc']:.2f}  minified/B(no docs) {tot['min']/tot['b_nodoc']:.2f}  orig/B(with docs) {tot['orig']/tot['b_doc']:.2f}")
T = sum(catsum.values())
print("o200k token shares by category:", {k: f"{100*v/T:.1f}%" for k, v in sorted(catsum.items(), key=lambda x: -x[1])})
json.dump({"rows": rows, "tot": tot, "cats": catsum}, open("prod_results.json", "w"), indent=1)
