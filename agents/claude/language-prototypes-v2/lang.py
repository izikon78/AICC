"""Reference implementation of two candidate AI-native languages (illustrative research prototype).
Language A: tokenizer-aligned compact text.  Language B: dedicated opcode stream (prefix, fixed arity,
de Bruijn locals).  Both parse to ONE shared AST with ONE type checker and ONE interpreter."""
from dataclasses import dataclass
import re, struct

# ---------------------------------------------------------------- AST
@dataclass
class Int:
    v: int
@dataclass
class Bool:
    v: bool
@dataclass
class Var:
    name: str
@dataclass
class Bin:
    op: str
    l: object
    r: object
@dataclass
class Tern:
    c: object
    a: object
    b: object
@dataclass
class Interp:            # inline interpolated string: parts are str or expr
    parts: list
@dataclass
class Tpl:               # interned template application
    name: str
    args: list
@dataclass
class Block:
    stmts: list
@dataclass
class For:               # for var < bound   (var = 0..bound-1, none if bound <= 0)
    var: str
    bound: object
    body: object
@dataclass
class ForR:              # for var in lo ..< hi
    var: str
    lo: object
    hi: object
    body: object
@dataclass
class If:
    c: object
    then: object
    els: object = None
@dataclass
class Eff:               # effect via a capability alias
    alias: str
    args: list
@dataclass
class Fn:
    name: str
    params: list         # [(name, type)]
    ret: str
    body: object
@dataclass
class Module:
    uses: dict           # alias -> (ref, [arg types])
    tpls: dict           # name -> template text with {0},{1}...
    fns: list

PRELUDE = {"log": ("std.log.info", ["str"])}   # default binding when no `use` is given
I32_MIN, I32_MAX = -2**31, 2**31 - 1

class LangError(Exception):
    def __init__(self, kind, msg):
        super().__init__(f"{kind}: {msg}"); self.kind = kind

def tpl_arity(text):
    idx = [int(m) for m in re.findall(r"\{(\d+)\}", text)]
    return (max(idx) + 1) if idx else 0

# ---------------------------------------------------------------- Language A: lexer
KW = {"fn", "for", "in", "if", "else", "use", "tpl", "true", "false"}
TYPES = {"i32", "bool", "str", "unit"}
PUNCT3 = ["..<"]
PUNCT2 = ["==", "!=", "<=", ">=", "&&", "||"]
PUNCT1 = list("(){}:,;?<>+-*/%!=")

def lex(src):
    toks, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c.isspace():
            i += 1; continue
        m = re.match(r"cap:[0-9a-f]+(\.[a-z_]+)*", src[i:])
        if m:
            toks.append(("REF", m.group(0))); i += m.end(); continue
        if c.isalpha() or c == "_":
            m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", src[i:])
            w = m.group(0); toks.append(("KW" if w in KW else "NAME", w)); i += m.end(); continue
        if c.isdigit():
            m = re.match(r"[0-9]+", src[i:]); toks.append(("INT", int(m.group(0)))); i += m.end(); continue
        if c == '"':
            j, buf = i + 1, []
            while j < n and src[j] != '"':
                if src[j] == "\\" and j + 1 < n:
                    buf.append(src[j:j + 2]); j += 2
                else:
                    buf.append(src[j]); j += 1
            if j >= n:
                raise LangError("E_LEX", "unterminated string")
            toks.append(("STR", "".join(buf))); i = j + 1; continue
        for p in PUNCT3 + PUNCT2 + PUNCT1:
            if src.startswith(p, i):
                toks.append(("P", p)); i += len(p); break
        else:
            raise LangError("E_LEX", f"unexpected character {c!r}")
    toks.append(("EOF", None))
    return toks

# ---------------------------------------------------------------- Language A: parser
class Parser:
    def __init__(self, src):
        self.t = lex(src); self.k = 0
    def peek(self, o=0): return self.t[self.k + o]
    def next(self):
        tok = self.t[self.k]; self.k += 1; return tok
    def accept(self, kind, val=None):
        tok = self.peek()
        if tok[0] == kind and (val is None or tok[1] == val):
            self.k += 1; return tok
        return None
    def expect(self, kind, val=None):
        tok = self.accept(kind, val)
        if not tok:
            raise LangError("E_PARSE", f"expected {val or kind}, got {self.peek()[1]!r}")
        return tok

    def module(self):
        uses, tpls, fns = {}, {}, []
        while self.peek()[0] != "EOF":
            if self.accept("KW", "use"):
                name = self.expect("NAME")[1]; self.expect("P", "="); ref = self.expect("REF")[1]
                self.expect("P", ";"); uses[name] = (ref, ["str"])
            elif self.accept("KW", "tpl"):
                name = self.expect("NAME")[1]; self.expect("P", "="); tpls[name] = self.expect("STR")[1]
                self.accept("P", ";")
            elif self.peek() == ("KW", "fn"):
                fns.append(self.fn())
            else:
                raise LangError("E_PARSE", f"unexpected {self.peek()[1]!r} at top level")
        if not fns:
            raise LangError("E_PARSE", "no function")
        return Module(uses, tpls, fns)

    def fn(self):
        self.expect("KW", "fn"); name = self.expect("NAME")[1]; self.expect("P", "(")
        params = []
        if not self.accept("P", ")"):
            while True:
                pn = self.expect("NAME")[1]; self.expect("P", ":"); ty = self.type_()
                params.append((pn, ty))
                if self.accept("P", ")"): break
                self.expect("P", ",")
        ret = "unit"
        if self.accept("P", ":"): ret = self.type_()
        return Fn(name, params, ret, self.block())

    def type_(self):
        tok = self.expect("NAME")
        if tok[1] not in TYPES: raise LangError("E_PARSE", f"unknown type {tok[1]}")
        return tok[1]

    def block(self):
        self.expect("P", "{"); stmts = []
        while not self.accept("P", "}"):
            stmts.append(self.stmt()); self.accept("P", ";")
        return Block(stmts)

    def stmt(self):
        if self.accept("KW", "for"):
            var = self.expect("NAME")[1]
            if self.accept("P", "<"):
                bound = self.expr(); return For(var, bound, self.block())
            self.expect("KW", "in"); lo = self.expr(); self.expect("P", "..<"); hi = self.expr()
            return ForR(var, lo, hi, self.block())
        if self.accept("KW", "if"):
            c = self.expr(); then = self.block(); els = None
            if self.accept("KW", "else"):
                els = self.stmt() if self.peek() == ("KW", "if") else self.block()
            return If(c, then, els)
        if self.peek()[0] == "NAME":
            alias = self.next()[1]
            if self.peek()[0] == "STR":                       # sugar: log"..."
                return Eff(alias, [self.string(self.next()[1])])
            self.expect("P", "("); args = self.args(); return Eff(alias, args)
        raise LangError("E_PARSE", f"unexpected {self.peek()[1]!r} at statement start")

    def args(self):
        args = []
        if self.accept("P", ")"): return args
        while True:
            args.append(self.expr())
            if self.accept("P", ")"): return args
            self.expect("P", ",")

    def string(self, raw):
        parts, i, buf = [], 0, []
        while i < len(raw):
            ch = raw[i]
            if ch == "\\" and i + 1 < len(raw):
                buf.append(raw[i + 1]); i += 2; continue
            if ch == "{":
                j = raw.find("}", i)
                if j < 0: raise LangError("E_PARSE", "unclosed interpolation hole")
                if buf: parts.append("".join(buf)); buf = []
                sub = Parser(raw[i + 1:j]); e = sub.expr()
                if sub.peek()[0] != "EOF": raise LangError("E_PARSE", "junk in interpolation hole")
                parts.append(e); i = j + 1; continue
            if ch == "}": raise LangError("E_PARSE", "stray } in string")
            buf.append(ch); i += 1
        if buf: parts.append("".join(buf))
        return Interp(parts)

    # expressions, lowest precedence first
    def expr(self):
        c = self.or_()
        if self.accept("P", "?"):
            a = self.expr(); self.expect("P", ":"); b = self.expr(); return Tern(c, a, b)
        return c
    def or_(self):
        l = self.and_()
        while self.accept("P", "||"): l = Bin("||", l, self.and_())
        return l
    def and_(self):
        l = self.cmp()
        while self.accept("P", "&&"): l = Bin("&&", l, self.cmp())
        return l
    def cmp(self):
        l = self.sum_()
        for op in ("==", "!=", "<=", ">=", "<", ">"):
            if self.accept("P", op): return Bin(op, l, self.sum_())
        return l
    def sum_(self):
        l = self.prod()
        while True:
            if self.accept("P", "+"): l = Bin("+", l, self.prod())
            elif self.accept("P", "-"): l = Bin("-", l, self.prod())
            else: return l
    def prod(self):
        l = self.unary()
        while True:
            for op in ("*", "/", "%"):
                if self.accept("P", op): l = Bin(op, l, self.unary()); break
            else: return l
    def unary(self):
        if self.accept("P", "-"): return Bin("-", Int(0), self.unary())
        if self.accept("P", "!"): return Bin("==", self.unary(), Bool(False))
        return self.atom()
    def atom(self):
        tok = self.next()
        if tok[0] == "INT": return Int(tok[1])
        if tok == ("KW", "true"): return Bool(True)
        if tok == ("KW", "false"): return Bool(False)
        if tok[0] == "STR": return self.string(tok[1])
        if tok[0] == "NAME":
            if self.accept("P", "("): return Tpl(tok[1], self.args())
            return Var(tok[1])
        if tok == ("P", "("):
            e = self.expr(); self.expect("P", ")"); return e
        raise LangError("E_PARSE", f"unexpected {tok[1]!r} in expression")

def parse_a(src):
    return Parser(src).module()

# ---------------------------------------------------------------- type checker (shared)
ARITH, CMP, LOGIC = {"+", "-", "*", "/", "%"}, {"<", "<=", ">", ">="}, {"&&", "||"}

def check(mod):
    caps = dict(PRELUDE); caps.update(mod.uses)
    def ty(e, env):
        if isinstance(e, Int):
            if not (I32_MIN <= e.v <= I32_MAX): raise LangError("E_TYPE", "integer literal out of i32 range")
            return "i32"
        if isinstance(e, Bool): return "bool"
        if isinstance(e, Var):
            if e.name not in env: raise LangError("E_SCOPE", f"unbound name {e.name}")
            return env[e.name]
        if isinstance(e, Bin):
            a, b = ty(e.l, env), ty(e.r, env)
            if e.op in ARITH or e.op in CMP:
                if a != "i32" or b != "i32": raise LangError("E_TYPE", f"{e.op} needs i32 operands")
                return "i32" if e.op in ARITH else "bool"
            if e.op in ("==", "!="):
                if a != b or a not in ("i32", "bool"): raise LangError("E_TYPE", f"{e.op} operand mismatch")
                return "bool"
            if a != "bool" or b != "bool": raise LangError("E_TYPE", f"{e.op} needs bool operands")
            return "bool"
        if isinstance(e, Tern):
            if ty(e.c, env) != "bool": raise LangError("E_TYPE", "condition must be bool")
            a, b = ty(e.a, env), ty(e.b, env)
            if a != b: raise LangError("E_TYPE", "ternary branches differ")
            return a
        if isinstance(e, Interp):
            for p in e.parts:
                if not isinstance(p, str) and ty(p, env) not in ("i32", "bool", "str"):
                    raise LangError("E_TYPE", "unformattable hole")
            return "str"
        if isinstance(e, Tpl):
            if e.name not in mod.tpls: raise LangError("E_SCOPE", f"unknown template {e.name}")
            need = tpl_arity(mod.tpls[e.name])
            if len(e.args) != need:
                raise LangError("E_TPL_ARITY", f"template {e.name} needs {need} argument(s), got {len(e.args)}")
            for a in e.args:
                if ty(a, env) not in ("i32", "bool", "str"): raise LangError("E_TYPE", "unformattable argument")
            return "str"
        raise LangError("E_TYPE", f"unknown expression {e}")
    def st(s, env):
        if isinstance(s, Block):
            for x in s.stmts: st(x, env)
        elif isinstance(s, For):
            if ty(s.bound, env) != "i32": raise LangError("E_TYPE", "loop bound must be i32")
            st(s.body, {**env, s.var: "i32"})
        elif isinstance(s, ForR):
            if ty(s.lo, env) != "i32" or ty(s.hi, env) != "i32": raise LangError("E_TYPE", "range must be i32")
            st(s.body, {**env, s.var: "i32"})
        elif isinstance(s, If):
            if ty(s.c, env) != "bool": raise LangError("E_TYPE", "if condition must be bool")
            st(s.then, env)
            if s.els is not None: st(s.els, env)
        elif isinstance(s, Eff):
            if s.alias not in caps: raise LangError("E_SCOPE", f"unknown capability alias {s.alias}")
            sig = caps[s.alias][1]
            if len(s.args) != len(sig): raise LangError("E_EFF_ARITY", f"{s.alias} takes {len(sig)} argument(s)")
            for a, want in zip(s.args, sig):
                if ty(a, env) != want: raise LangError("E_TYPE", f"{s.alias} argument must be {want}")
        else:
            raise LangError("E_TYPE", f"unknown statement {s}")
    for f in mod.fns:
        st(f.body, dict(f.params))
    return True

# ---------------------------------------------------------------- interpreter (shared)
def fmt(v):
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, int): return str(v)          # invariant decimal, ASCII '-' for negatives
    return v

def run(mod, fn_name, args, max_events=10_000):
    caps = dict(PRELUDE); caps.update(mod.uses)
    fn = next(f for f in mod.fns if f.name == fn_name)
    trace = []
    def chk(x):
        if not (I32_MIN <= x <= I32_MAX): raise LangError("E_OVERFLOW", "i32 overflow")
        return x
    def ev(e, env):
        if isinstance(e, (Int, Bool)): return e.v
        if isinstance(e, Var): return env[e.name]
        if isinstance(e, Bin):
            a, b = ev(e.l, env), ev(e.r, env)
            if e.op == "+": return chk(a + b)
            if e.op == "-": return chk(a - b)
            if e.op == "*": return chk(a * b)
            if e.op in ("/", "%"):
                if b == 0: raise LangError("E_DIV0", "division by zero")
                q = abs(a) // abs(b) * (1 if (a >= 0) == (b >= 0) else -1)   # truncating, like C#
                return chk(q) if e.op == "/" else chk(a - q * b)
            return {"==": a == b, "!=": a != b, "<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b,
                    "&&": a and b, "||": a or b}[e.op]
        if isinstance(e, Tern): return ev(e.a, env) if ev(e.c, env) else ev(e.b, env)
        if isinstance(e, Interp): return "".join(p if isinstance(p, str) else fmt(ev(p, env)) for p in e.parts)
        if isinstance(e, Tpl):
            vals = [fmt(ev(a, env)) for a in e.args]
            return re.sub(r"\{(\d+)\}", lambda m: vals[int(m.group(1))], mod.tpls[e.name])
    def ex(s, env):
        if isinstance(s, Block):
            for x in s.stmts: ex(x, env)
        elif isinstance(s, For):
            for k in range(ev(s.bound, env)): ex(s.body, {**env, s.var: k})
        elif isinstance(s, ForR):
            for k in range(ev(s.lo, env), ev(s.hi, env)): ex(s.body, {**env, s.var: k})
        elif isinstance(s, If):
            if ev(s.c, env): ex(s.then, env)
            elif s.els is not None: ex(s.els, env)
        elif isinstance(s, Eff):
            trace.append((caps[s.alias][0], *[fmt(ev(a, env)) for a in s.args]))
            if len(trace) > max_events: raise LangError("E_RUNAWAY", "too many effects")
    ex(fn.body, dict(zip([p for p, _ in fn.params], args)))
    return trace

# ---------------------------------------------------------------- Language A: canonical printer
PREC = {"||": 1, "&&": 2, "==": 3, "!=": 3, "<": 3, "<=": 3, ">": 3, ">=": 3, "+": 4, "-": 4, "*": 5, "/": 5, "%": 5}
def a_expr(e, p=0):
    if isinstance(e, Int): return str(e.v)
    if isinstance(e, Bool): return "true" if e.v else "false"
    if isinstance(e, Var): return e.name
    if isinstance(e, Bin):
        q = PREC[e.op]; s = f"{a_expr(e.l, q)}{e.op}{a_expr(e.r, q + 1)}"
        return f"({s})" if q < p else s
    if isinstance(e, Tern):
        s = f"{a_expr(e.c, 1)}?{a_expr(e.a)}:{a_expr(e.b)}"; return f"({s})" if p else s
    if isinstance(e, Interp):
        return '"' + "".join(x if isinstance(x, str) else "{" + a_expr(x) + "}" for x in e.parts) + '"'
    if isinstance(e, Tpl): return f"{e.name}({','.join(a_expr(a) for a in e.args)})"
def a_stmt(s):
    if isinstance(s, Block): return "{" + ";".join(a_stmt(x) for x in s.stmts) + "}"
    if isinstance(s, For): return f"for {s.var}<{a_expr(s.bound)}{a_stmt(s.body)}"
    if isinstance(s, ForR): return f"for {s.var} in {a_expr(s.lo)}..<{a_expr(s.hi)}{a_stmt(s.body)}"
    if isinstance(s, If):
        out = f"if {a_expr(s.c)}{a_stmt(s.then)}"
        return out + (f"else{a_stmt(s.els)}" if s.els is not None else "")
    if isinstance(s, Eff):
        if len(s.args) == 1 and isinstance(s.args[0], Interp): return f"{s.alias}{a_expr(s.args[0])}"
        return f"{s.alias}({','.join(a_expr(a) for a in s.args)})"
def print_a(mod, headers=True):
    out = []
    if headers:
        out += [f"use {k}={v[0]};" for k, v in mod.uses.items()]
        out += [f'tpl {k}="{v}";' for k, v in mod.tpls.items()]
    for f in mod.fns:
        ps = ",".join(f"{n}:{t}" for n, t in f.params)
        out.append(f"fn {f.name}({ps}){':' + f.ret if f.ret != 'unit' else ''}{a_stmt(f.body)}")
    return "\n".join(out)

# ---------------------------------------------------------------- Language B: vocabulary
STRUCT = ["FN0", "FN1", "FN2", "FN3", "BLK", "END", "FOR", "FORR", "IF", "IF1", "SEL", "EFF", "STRB", "STRE"]
TYPEV = ["TI32", "TBOOL", "TSTR", "TUNIT"]
OPS = ["ADD", "SUB", "MUL", "DIV", "MOD", "EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR"]
BOOLS = ["TRUE", "FALSE"]
CONSTS = [f"C{i}" for i in range(16)] + ["CI32"]
PARAMS = [f"P{i}" for i in range(8)]
LOCALS = [f"L{i}" for i in range(16)]
TPLS = [f"TP{i}" for i in range(32)]
CAPS = [f"K{i}" for i in range(16)]
BYTES = [f"X{i}" for i in range(256)]           # payload bytes for CI32
VOCAB = STRUCT + TYPEV + OPS + BOOLS + CONSTS + PARAMS + LOCALS + TPLS + CAPS + BYTES
OPCODE = {name: i for i, name in enumerate(VOCAB)}
CLASSES = {"struct": STRUCT, "type": TYPEV, "op": OPS, "bool": BOOLS, "const": CONSTS[:-1],
           "param": PARAMS, "local": LOCALS, "tpl": TPLS, "cap": CAPS}
OPMAP = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD", "==": "EQ", "!=": "NE",
         "<": "LT", "<=": "LE", ">": "GT", ">=": "GE", "&&": "AND", "||": "OR"}
RMAP = {v: k for k, v in OPMAP.items()}
TYMAP = {"i32": "TI32", "bool": "TBOOL", "str": "TSTR", "unit": "TUNIT"}
RTY = {v: k for k, v in TYMAP.items()}

def encode_b(mod, inline_strings=False):
    """AST -> (header, token list). Inline strings become templates; locals become de Bruijn indices."""
    assert len(mod.fns) == 1, "prototype encodes one function"
    f = mod.fns[0]
    tpl_names, tpl_texts, origin = [], [], []
    for k, v in mod.tpls.items(): tpl_names.append(k); tpl_texts.append(v); origin.append("decl")
    caps = dict(PRELUDE); caps.update(mod.uses)
    cap_names = list(caps.keys())
    params = [p for p, _ in f.params]; toks = []
    def e(x, binders):
        if isinstance(x, Int):
            if 0 <= x.v <= 15: toks.append(f"C{x.v}")
            else: toks.append("CI32"); toks.extend(f"X{b}" for b in struct.pack("<i", x.v))
        elif isinstance(x, Bool): toks.append("TRUE" if x.v else "FALSE")
        elif isinstance(x, Var):
            if x.name in binders: toks.append(f"L{binders[::-1].index(x.name)}")   # de Bruijn: 0 = innermost binder
            else: toks.append(f"P{params.index(x.name)}")
        elif isinstance(x, Bin): toks.append(OPMAP[x.op]); e(x.l, binders); e(x.r, binders)
        elif isinstance(x, Tern): toks.append("SEL"); e(x.c, binders); e(x.a, binders); e(x.b, binders)
        elif isinstance(x, Interp) and inline_strings:
            toks.append("STRB")
            for p in x.parts:
                if isinstance(p, str): toks.append(("TXT", p))     # base-tokenizer text, not an opcode
                else: e(p, binders)
            toks.append("STRE")
        elif isinstance(x, Interp):
            text, args = "", []
            for p in x.parts:
                if isinstance(p, str): text += p
                else: text += "{" + str(len(args)) + "}"; args.append(p)
            tpl_names.append(None); tpl_texts.append(text); origin.append("inline")
            toks.append(f"TP{len(tpl_texts) - 1}")
            for a in args: e(a, binders)
        elif isinstance(x, Tpl):
            toks.append(f"TP{tpl_names.index(x.name)}")
            for a in x.args: e(a, binders)
    def s(x, binders):
        if isinstance(x, Block):
            if len(x.stmts) == 1: s(x.stmts[0], binders); return   # single-statement blocks are transparent
            toks.append("BLK")
            for y in x.stmts: s(y, binders)
            toks.append("END")
        elif isinstance(x, For): toks.append("FOR"); e(x.bound, binders); s(x.body, binders + [x.var])
        elif isinstance(x, ForR): toks.append("FORR"); e(x.lo, binders); e(x.hi, binders); s(x.body, binders + [x.var])
        elif isinstance(x, If):
            toks.append("IF" if x.els is not None else "IF1"); e(x.c, binders); s(x.then, binders)
            if x.els is not None: s(x.els, binders)
        elif isinstance(x, Eff):
            toks.append("EFF"); toks.append(f"K{cap_names.index(x.alias)}")
            for a in x.args: e(a, binders)
    toks.append(f"FN{len(f.params)}"); toks.extend(TYMAP[t] for _, t in f.params); toks.append(TYMAP[f.ret])
    s(f.body, [])
    header = {"fn": f.name, "param_names": params, "templates": tpl_texts, "template_names": tpl_names,
              "template_origin": origin, "caps": [(k, caps[k][0], caps[k][1]) for k in cap_names]}
    return header, toks

def decode_b(header, toks):
    """Tokens -> AST, deterministic prefix parse with fixed arities. Raises LangError on malformed input."""
    pos = [0]; loopnames = "ijklmnopqrstuvwxyz"
    def nxt():
        if pos[0] >= len(toks): raise LangError("E_EOS", "unexpected end of token stream")
        t = toks[pos[0]]; pos[0] += 1
        if isinstance(t, tuple): return t
        if t not in OPCODE: raise LangError("E_TOKEN", f"unknown token {t}")
        return t
    caps = header["caps"]; tpls = header["templates"]
    def e(binders):
        t = nxt()
        if isinstance(t, tuple): raise LangError("E_SORT", "text outside a string")
        if t == "STRB":
            parts = []
            while True:
                if pos[0] >= len(toks): raise LangError("E_EOS", "unterminated string")
                if toks[pos[0]] == "STRE": pos[0] += 1; return Interp(parts)
                if isinstance(toks[pos[0]], tuple): parts.append(toks[pos[0]][1]); pos[0] += 1
                else: parts.append(e(binders))
        if t in OPS: return Bin(RMAP[t], e(binders), e(binders))
        if t == "SEL": return Tern(e(binders), e(binders), e(binders))
        if t in BOOLS: return Bool(t == "TRUE")
        if t == "CI32":
            payload = [nxt() for _ in range(4)]
            if not all(isinstance(x, str) and x in BYTES for x in payload):
                raise LangError("E_SORT", "CI32 must be followed by four byte tokens")
            return Int(struct.unpack("<i", bytes(int(x[1:]) for x in payload))[0])
        if t.startswith("C") and t[1:].isdigit(): return Int(int(t[1:]))
        if t.startswith("P") and t[1:].isdigit():
            k = int(t[1:])
            if k >= len(nparams[0]): raise LangError("E_SCOPE", f"no parameter {t}")
            return Var(nparams[0][k])
        if t.startswith("L") and t[1:].isdigit():
            k = int(t[1:])
            if k >= len(binders): raise LangError("E_SCOPE", f"no local {t}")
            return Var(binders[len(binders) - 1 - k])
        if t.startswith("TP") and t[2:].isdigit():
            k = int(t[2:])
            if k >= len(tpls): raise LangError("E_SCOPE", f"no template {t}")
            args = [e(binders) for _ in range(tpl_arity(tpls[k]))]
            if header["template_origin"][k] == "inline":
                parts, last = [], 0
                for m in re.finditer(r"\{(\d+)\}", tpls[k]):
                    if m.start() > last: parts.append(tpls[k][last:m.start()])
                    parts.append(args[int(m.group(1))]); last = m.end()
                if last < len(tpls[k]): parts.append(tpls[k][last:])
                return Interp(parts)
            return Tpl(header["template_names"][k], args)
        raise LangError("E_SORT", f"{t} cannot start an expression")
    def s(binders):
        t = nxt()
        if isinstance(t, tuple): raise LangError("E_SORT", "text cannot start a statement")
        if t == "BLK":
            out = []
            while True:
                if pos[0] >= len(toks): raise LangError("E_EOS", "unterminated block")
                if toks[pos[0]] == "END": pos[0] += 1; return Block(out)
                out.append(s(binders))
        if t == "FOR":
            b = e(binders); v = loopnames[len(binders) % len(loopnames)]
            return For(v, b, wrap(s(binders + [v])))
        if t == "FORR":
            lo, hi = e(binders), e(binders); v = loopnames[len(binders) % len(loopnames)]
            return ForR(v, lo, hi, wrap(s(binders + [v])))
        if t in ("IF", "IF1"):
            c = e(binders); th = wrap(s(binders))
            return If(c, th, wrap(s(binders)) if t == "IF" else None)
        if t == "EFF":
            k = nxt()
            if not (k.startswith("K") and k[1:].isdigit()) or int(k[1:]) >= len(caps):
                raise LangError("E_SORT", f"EFF needs a capability alias, got {k}")
            alias, _, sig = caps[int(k[1:])]
            return Eff(alias, [e(binders) for _ in sig])
        raise LangError("E_SORT", f"{t} cannot start a statement")
    def wrap(x): return x if isinstance(x, Block) else Block([x])
    nparams = [header["param_names"]]
    t = nxt()
    if not (t.startswith("FN") and t[2:].isdigit()): raise LangError("E_SORT", "stream must start with FNk")
    k = int(t[2:])
    if k != len(header["param_names"]): raise LangError("E_SCOPE", "parameter count mismatch")
    ptys = []
    for _ in range(k):
        ty = nxt()
        if ty not in RTY: raise LangError("E_SORT", f"expected a type, got {ty}")
        ptys.append(RTY[ty])
    rt = nxt()
    if rt not in RTY: raise LangError("E_SORT", f"expected a return type, got {rt}")
    body = wrap(s([]))
    if pos[0] != len(toks): raise LangError("E_TRAILING", "tokens after end of function")
    mod_uses = {a: (r, sig) for a, r, sig in caps if a not in PRELUDE or (r, sig) != PRELUDE[a]}
    named = {n: t for n, t, o in zip(header["template_names"], tpls, header["template_origin"]) if o == "decl"}
    return Module(mod_uses, named, [Fn(header["fn"], list(zip(header["param_names"], ptys)), RTY[rt], body)])

def b_bytes(header, toks):
    """Binary serialization: 1 byte per opcode (payload bytes raw) + length-prefixed UTF-8 templates."""
    out = bytearray()
    for t in header["templates"]:
        b = t.encode("utf-8"); out += bytes([len(b)]) + b
    out += bytes([0xFF])
    i = 0
    while i < len(toks):
        if toks[i] == "CI32":
            out.append(OPCODE["CI32"]); out += bytes(int(x[1:]) for x in toks[i + 1:i + 5]); i += 5
        else:
            out.append(OPCODE[toks[i]]); i += 1
    return bytes(out)

# ---------------------------------------------------------------- projections to Python and C#
def proj_py(mod):
    f = mod.fns[0]; lines = [f"def {f.name}(self, {', '.join(f'{n}: int' for n, _ in f.params)}) -> None:"]
    def ex(e, safe):
        if isinstance(e, Int): return str(e.v)
        if isinstance(e, Bool): return "True" if e.v else "False"
        if isinstance(e, Var): return e.name
        if isinstance(e, Bin):
            op = {"&&": "and", "||": "or"}.get(e.op, e.op)
            s = f"{ex(e.l, safe)} {op} {ex(e.r, safe)}"
            if e.op in ("+", "-", "*") and not (e.op == "+" and isinstance(e.r, Int) and e.r.v == 1 and isinstance(e.l, Var) and e.l.name in safe):
                return f"_chk32({s})"          # keep i32 overflow semantics unless provably safe
            return s
        if isinstance(e, Tern): return f"({ex(e.a, safe)} if {ex(e.c, safe)} else {ex(e.b, safe)})"
        if isinstance(e, Interp): return 'f"' + "".join(p if isinstance(p, str) else "{" + ex(p, safe) + "}" for p in e.parts) + '"'
    def st(s, ind, safe):
        pad = "    " * ind
        if isinstance(s, Block):
            for x in s.stmts: st(x, ind, safe)
        elif isinstance(s, For):
            lines.append(f"{pad}for {s.var} in range({ex(s.bound, safe)}):")
            st(s.body, ind + 1, safe | {s.var} if isinstance(s.bound, Var) else safe)
        elif isinstance(s, If):
            lines.append(f"{pad}if {ex(s.c, safe)}:"); st(s.then, ind + 1, safe)
            if s.els is not None: lines.append(f"{pad}else:"); st(s.els, ind + 1, safe)
        elif isinstance(s, Eff):
            lines.append(f"{pad}self.m_log.info({', '.join(ex(a, safe) for a in s.args)})")
    st(f.body, 1, set()); return "\n".join(lines)

def proj_cs(mod):
    f = mod.fns[0]; safe = [set()]; lines = [f"public void {f.name[0].upper() + f.name[1:]}({', '.join(f'int {n}' for n, _ in f.params)})", "{"]
    def ex(e):
        if isinstance(e, Int): return str(e.v)
        if isinstance(e, Bool): return "true" if e.v else "false"
        if isinstance(e, Var): return e.name
        if isinstance(e, Bin):
            safe_inc = e.op == "+" and isinstance(e.r, Int) and e.r.v == 1 and isinstance(e.l, Var) and e.l.name in safe[0]
            return f"checked({ex(e.l)} {e.op} {ex(e.r)})" if e.op in ("+", "-", "*") and not safe_inc else f"{ex(e.l)} {e.op} {ex(e.r)}"
        if isinstance(e, Tern): return f"({ex(e.c)} ? {ex(e.a)} : {ex(e.b)})"
        if isinstance(e, Interp):   # invariant culture: CGIR formatting is culture-independent
            return 'FormattableString.Invariant($"' + "".join(p if isinstance(p, str) else "{" + ex(p) + "}" for p in e.parts) + '")'
    def st(s, ind):
        pad = "    " * ind
        if isinstance(s, Block):
            for x in s.stmts: st(x, ind)
        elif isinstance(s, For):
            lines.append(f"{pad}for (int {s.var} = 0; {s.var} < {ex(s.bound)}; {s.var}++)"); lines.append(pad + "{")
            if isinstance(s.bound, Var): safe[0] = safe[0] | {s.var}      # i < n <= int.MaxValue, so i + 1 cannot overflow
            st(s.body, ind + 1); lines.append(pad + "}")
        elif isinstance(s, If):
            lines.append(f"{pad}if ({ex(s.c)})"); lines.append(pad + "{"); st(s.then, ind + 1); lines.append(pad + "}")
            if s.els is not None: lines.append(f"{pad}else"); lines.append(pad + "{"); st(s.els, ind + 1); lines.append(pad + "}")
        elif isinstance(s, Eff): lines.append(f"{pad}m_log.Info({', '.join(ex(a) for a in s.args)});")
    st(f.body, 1); lines.append("}"); return "\n".join(lines)
