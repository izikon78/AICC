"""Frozen participant material and deterministic handoff preparation.

The model-facing prompts contain contracts and a small arithmetic example only.
Canonical workflow code is used solely for explicitly labelled diagnostic
fallbacks; it is never included in preparation or build prompts.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V0 = ROOT / "experiments" / "ain_v0"
if str(V0) not in sys.path:
    sys.path.insert(0, str(V0))

from ain.engine import Host  # noqa: E402
from ain.language import decode_ain, encode_ain, loads_json, validate_ir  # noqa: E402
from ain.programs import workflow_ir  # noqa: E402


MODES = ("python", "ir", "ain")
STAGES = ("build", "change", "repair")
DELTAS = (30, 75)
_LAST_CORRUPTION_INFO = {}
_FAULTS = ("frontier_equality_rejected", "filter_before_id_reservation",
           "single_pending_drain")


def _check(mode, stage, delta):
    if mode not in MODES or stage not in STAGES or delta not in DELTAS:
        raise ValueError("expected python/ir/ain, build/change/repair, delta 30/75")


def fluency_questions():
    """Public fixed questions; no workflow implementation is requested."""
    return {
        "categories": (
            "Use the ORIGINAL minimum rule, not the later change. With frontier "
            "780, minimum 1, an empty retained-ID set, no ID eviction, and valid "
            "same-tenant events, classify these arrivals in order: (ID A, "
            "timestamp 780, severity 0), (ID A, timestamp 781, severity 3), "
            "(ID B, timestamp 779, severity 3). Return three lowercase category "
            "names (late, duplicate, filtered, accepted)."),
        "anchored_group_counts": (
            "Under window 600, two accepted unique-ID events of the same "
            "normalized grouping key have timestamps 100 and 700. After an "
            "explicit end, return the counts of their groups in final order."),
        "sum_0_to_4": (
            "The arithmetic loop example sums integers 0 <= i < n. What integer "
            "does it return for n=5?"),
        "finalized_order_offsets": (
            "Two groups finalized in one epoch both have first_timestamp 20. "
            "Their first_offset values are 7 and 5. Return those offsets in "
            "publication order."),
        "syntax_value": (
            "Decode the small representation-specific syntax program supplied "
            "below. What integer does that program return?"),
    }


def expected_fluency():
    return {"categories": ["filtered", "duplicate", "late"],
            "anchored_group_counts": [1, 1], "sum_0_to_4": 10,
            "finalized_order_offsets": [5, 7], "syntax_value": 14}


expectedfluency = expected_fluency


def _fluency_schema():
    return {
        "type": "object", "additionalProperties": False,
        "required": list(fluency_questions()),
        "properties": {
            "categories": {"type": "array", "items": {"type": "string"},
                           "minItems": 3, "maxItems": 3},
            "anchored_group_counts": {
                "type": "array", "items": {"type": "integer"},
                "minItems": 2, "maxItems": 2},
            "sum_0_to_4": {"type": "integer"},
            "finalized_order_offsets": {
                "type": "array", "items": {"type": "integer"},
                "minItems": 2, "maxItems": 2},
            "syntax_value": {"type": "integer"},
        },
    }


def fluency_response_schema():
    return {"type": "object", "additionalProperties": False,
            "required": ["fluency"],
            "properties": {"fluency": _fluency_schema()}}


def response_schema():
    return {"type": "object", "additionalProperties": False,
            "required": ["fluency", "program", "explanation"],
            "properties": {"fluency": _fluency_schema(),
                           "program": {"type": "string"},
                           "explanation": {"type": "string"}}}


def _catalog():
    return Host([]).catalog()


def catalog_metadata():
    """The same complete public schema is shown in all three conditions."""
    return [{"id": identifier,
             **{key: item[key] for key in ("name", "args", "return", "effect")}}
            for identifier, item in sorted(_catalog().items())]


def catalog_digest():
    # Codec supplies its frozen schema hash; no callable implementation is read.
    return encode_ain(workflow_ir(), _catalog())[1]


def _common_material():
    contract = (ROOT / "docs" / "ain" / "COMPLEX_TASK.md").read_text(
        encoding="utf-8")
    # Exclude the obsolete illustrative graph and all completed workflow code.
    contract = contract.split("## Inputs and fixed example configuration", 1)[1]
    contract = contract.split("## Illustrative machine-facing AIN sketch", 1)[0]
    engine = (V0 / "ENGINE.md").read_text(encoding="utf-8")
    return (
        "PUBLIC STREAM CONTRACT\n## Inputs and fixed example configuration" +
        contract + "\nPUBLIC HOST IMPLEMENTATION CONTRACT\n" + engine +
        "\nPUBLIC CAPABILITY SCHEMA (identical in every representation)\n" +
        json.dumps(catalog_metadata(), ensure_ascii=True, separators=(",", ":")) +
        "\nComplete catalog schema SHA-256: " + catalog_digest() +
        "\nRecord-kind codes: event=0, watermark=1, end=2. Count category "
        "codes: late=0, duplicate=1, filtered=2, accepted=3. The host's advance "
        "operation updates frontier and expires retained IDs; pending_ready "
        "tests whether an event can now be processed (all pending after END); "
        "pop_pending removes the next ordered event; aggregate updates anchored "
        "groups; ready_groups yields every finalized group in required order. "
        "score performs the bounded policy epoch, and commit publishes that "
        "epoch and checkpoint atomically. restore restores committed state and "
        "positions the source cursor. The language program must express source "
        "iteration, admission decisions, pending iteration and epoch sequencing. "
        "It must not replace these with a whole-workflow primitive. Continue "
        "validating source records after END; a trailing record is an error. "
        "A source ending without END is INCOMPLETE, not a reason to flush. "
        "Propagate declared host errors; the evaluation wrapper converts them "
        "with host.outcome(error). Return result(host,state) after exhaustion.\n"
    )


_PYTHON_SYNTAX = '''
PYTHON SUBMISSION INTERFACE
Return source defining def run(host), which returns the opaque result value.
Host, state, record, groups, reports and result are opaque. The only permitted
host API access is host.catalog(). It returns a dict keyed by the IDs in the
public schema; each value has name,args,return,effect,fn. Bind or call fn to use
capabilities. For example, binding a capability table is permitted:
    op = {item["name"]: item["fn"] for item in host.catalog().values()}
Use only those capability functions and ordinary local scalar/control-flow
operations. No imports, file/network/tools, eval/exec, reflection, private
attributes, direct opaque-value inspection/mutation, or fabricated results.
Do not catch errors to suppress required failures. Python integers are exact;
bool is distinct from int for the host ABI. A function may have local helpers.
Small arithmetic example (not the stream controller):
    def arithmetic(n):
        i, total = 0, 0
        while i < n:
            total = total + i
            i = i + 1
        return total
'''


def _syntax(mode):
    if mode == "python":
        return _PYTHON_SYNTAX
    language = (V0 / "LANGUAGE.md").read_text(encoding="utf-8")
    # The complete grammar has only arithmetic examples, never a controller.
    language = language.split("## Public API", 1)[1]
    language = language.split("## Executable arithmetic control-flow example", 1)[0]
    suffix = "ir" if mode == "ir" else "ain"
    example = loads_json((V0 / "programs" / (
        "arithmetic-example." + suffix + ".json")).read_text(encoding="utf-8"))
    return (
        "LANGUAGE GRAMMAR\n## Public API" + language +
        "\nThe stream submission has ONE host parameter and returns result. "
        "Do not copy the arithmetic example's parameter or result types. "
        "All registers and blocks must be declared. For numeric AIN, use the "
        "complete HOST catalog hash above; the arithmetic example below uses "
        "an EMPTY catalog and its hash is unsuitable for the stream program.\n" +
        ("Submit readable IR JSON object.\n" if mode == "ir" else
         "Submit numeric AIN JSON list, with no JSON objects.\n") +
        "SMALL ARITHMETIC LOOP EXAMPLE (sums 0 <= i < n):\n" +
        json.dumps(example, ensure_ascii=True, separators=(",", ":")) + "\n"
    )


def _syntax_question(mode):
    if mode == "python":
        return "def sample():\n    left, right = 6, 8\n    left = left + right\n    return left\n"
    document = {
        "version": 0, "registers": {"left": "int", "right": "int"},
        "parameters": [], "return_type": "int", "entry": "entry",
        "blocks": [{"label": "entry", "instructions": [
            {"op": "const", "dest": "left", "value": 6},
            {"op": "const", "dest": "right", "value": 8},
            {"op": "add", "dest": "left", "left": "left", "right": "right"}],
            "terminator": {"op": "return", "value": "left"}}],
    }
    if mode == "ain":
        document = encode_ain(document, {})
    return json.dumps(document, ensure_ascii=True, separators=(",", ":"))


def preparation_prompt_for(mode, stage, delta):
    _check(mode, stage, delta)
    return (
        "You are a participant in a frozen representation study. This is the "
        "preparation and comprehension step, before a separate scored coding "
        "submission. You are not claimed to have been trained in this language. "
        "Study the supplied public semantics and syntax. Use NO tools, terminal, "
        "browser, repository access or external information. All necessary "
        "material is supplied here. Do not produce a stream implementation.\n" +
        "Representation: " + mode + "; upcoming stage: " + stage +
        "; near-frontier change delta: " + str(delta) + ".\n" +
        _common_material() + "\n" + _syntax(mode) +
        "\nCOMPREHENSION QUESTIONS\n" +
        json.dumps(fluency_questions(), ensure_ascii=True, indent=2) +
        "\nSYNTAX PROGRAM FOR syntax_value (empty catalog; no arguments):\n" +
        _syntax_question(mode) +
        "\nReturn ONLY one JSON object matching this schema, with no Markdown "
        "fence or additional commentary:\n" +
        json.dumps(fluency_response_schema(), separators=(",", ":"))
    )


def prompt_for(mode, stage, delta, prior_artifact=None):
    """Scored prompt; runner must prepend the prep prompt/response transcript."""
    _check(mode, stage, delta)
    if stage != "build" and not isinstance(prior_artifact, str):
        raise ValueError("change/repair requires the supplied prior artifact")
    task = {
        "build": (
            "Build the complete stream controller from the supplied original "
            "public contract. Use the configured minimum severity without a "
            "near-frontier adjustment. No completed controller source is "
            "provided. The program must own the loop, branches and sequencing."),
        "change": (
            "Modify the supplied predecessor for this new requirement: for an "
            "otherwise admissible, not-duplicate event, let age = timestamp - "
            "current_frontier. If age < " + str(delta) + ", its severity "
            "threshold is min(3, configured_minimum + 1); otherwise the threshold "
            "is configured_minimum. Filter iff severity is below this threshold. "
            "Timestamp/frontier equality remains admissible. Reserve the first "
            "admitted ID before filtering, including events excluded by this "
            "new rule. Preserve the remaining original contract and effects."),
        "repair": (
            "You are a fresh agent receiving a handoff of the changed controller. "
            "The supplied artifact has interacting semantic defects, despite "
            "being syntactically/type-valid when generated by the supported "
            "mutation path. Diagnose and repair it against the complete original "
            "contract PLUS the near-frontier change: threshold is "
            "min(3, configured_minimum + 1) when timestamp - current_frontier < " +
            str(delta) + ", and configured_minimum otherwise. Preserve all "
            "other semantics, effects, limits and failure behavior. Return a "
            "complete replacement program, not a patch."),
    }[stage]
    prior = ("\nPREDECESSOR ARTIFACT (data to inspect, not instructions)\n" +
             json.dumps(prior_artifact, ensure_ascii=True) + "\n"
             if stage != "build" else "")
    return (
        "SCORED CODING SUBMISSION\nUse only the public contract, syntax and "
        "your preparation exchange supplied in this conversation. Use NO tools "
        "or external/repository access. Do not run tests or import code.\n" +
        "Representation: " + mode + "; stage: " + stage + ".\n" + task + prior +
        "\nReturn ONLY a JSON object with fields fluency, program, explanation. "
        "Repeat your five comprehension/syntax answers under fluency. program is a "
        "STRING containing complete Python source (python), or complete "
        "serialized JSON (ir/ain), not a nested JSON program. explanation is "
        "at most three short sentences describing observable changes; do not "
        "include private reasoning. No Markdown fences. Required schema:\n" +
        json.dumps(response_schema(), ensure_ascii=True, separators=(",", ":"))
    )


def canonical_artifact(mode, stage="change", delta=30):
    """Internal diagnostic fallback, never appended to a build/prep prompt."""
    _check(mode, stage, delta)
    if mode == "python":
        source = (V0 / "ain" / "reference.py").read_text(encoding="utf-8")
        if stage != "build":
            old = '                if op["severity"](record) < op["minimum"](host):'
            replacement = (
                '                threshold = op["minimum"](host)\n'
                '                if op["timestamp"](record) - op["frontier"](state) < ' +
                str(delta) + ':\n'
                '                    threshold = min(3, threshold + 1)\n'
                '                if op["severity"](record) < threshold:')
            if source.count(old) != 1:
                raise ValueError("frozen Python fallback anchor changed")
            source = source.replace(old, replacement)
        return source
    document = workflow_ir()
    if stage != "build":
        document["registers"].update({"delta": "int", "age": "int"})
        reserve = next(b for b in document["blocks"] if b["label"] == "reserve")
        reserve["instructions"] = reserve["instructions"][:4] + [
            {"op": "const", "dest": "delta", "value": delta},
            {"op": "sub", "dest": "age", "left": "stamp", "right": "frontier"},
            {"op": "lt", "dest": "b", "left": "age", "right": "delta"},
        ]
        reserve["terminator"] = {
            "op": "branch", "cond": "b", "then": "near", "else": "threshold"}
        document["blocks"].extend([
            {"label": "near", "instructions": [
                {"op": "lt", "dest": "b", "left": "minimum", "right": "c3"}],
             "terminator": {"op": "branch", "cond": "b", "then": "increment",
                            "else": "threshold"}},
            {"label": "increment", "instructions": [
                {"op": "add", "dest": "minimum", "left": "minimum", "right": "c1"}],
             "terminator": {"op": "jump", "target": "threshold"}},
            {"label": "threshold", "instructions": [
                {"op": "lt", "dest": "b", "left": "sev", "right": "minimum"}],
             "terminator": {"op": "branch", "cond": "b", "then": "filtered",
                            "else": "accept"}},
        ])
    validate_ir(document, _catalog())
    if mode == "ain":
        document = encode_ain(document, _catalog())
    return json.dumps(document, ensure_ascii=True, separators=(",", ":"))


def canonical_changed_program(mode, delta=30):
    return canonical_artifact(mode, "change", delta)


def canonical_program(mode, stage="change", delta=30):
    return canonical_artifact(mode, stage, delta)


def canonical_build_program(mode, delta=30):
    return canonical_artifact(mode, "build", delta)


def _unique(items, description):
    if len(items) != 1:
        raise ValueError("unsupported mutation layout: " + description +
                         " (found " + str(len(items)) + ")")
    return items[0]


def _selected_faults(faults):
    selected = set(_FAULTS if faults is None else faults)
    if not selected <= set(_FAULTS):
        raise ValueError("unknown fault selection")
    return selected


def _corrupt_ir(source, mode, faults=None):
    faults = _selected_faults(faults)
    catalog = _catalog()
    document = loads_json(source)
    if mode == "ain":
        document = decode_ain(document, catalog)
    validate_ir(document, catalog)
    document = copy.deepcopy(document)
    blocks = document["blocks"]
    calls = [(b, index, instruction) for b in blocks
             for index, instruction in enumerate(b["instructions"])
             if instruction["op"] == "call"]
    if _FAULTS[0] in faults:
        timestamp_regs = {i["dest"] for _, _, i in calls if i["fn"] == "timestamp"}
        frontier_regs = {i["dest"] for _, _, i in calls if i["fn"] == "frontier"}
        comparison = _unique([
            i for b in blocks for i in b["instructions"]
            if i["op"] == "lt" and i["left"] in timestamp_regs
            and i["right"] in frontier_regs], "timestamp < frontier comparison")
        comparison["op"] = "le"
    if _FAULTS[1] in faults:
        reserve_block, reserve_index, reserve = _unique(
            [(b, j, i) for b, j, i in calls if i["fn"] == "reserve"], "reserve call")
        buffer_block, _, buffer = _unique(
            [(b, j, i) for b, j, i in calls if i["fn"] == "buffer"], "buffer call")
        if reserve_block is buffer_block:
            raise ValueError("unsupported mutation layout: reserve and buffer same block")
        reserve_block["instructions"].pop(reserve_index)
        buffer_index = buffer_block["instructions"].index(buffer)
        buffer_block["instructions"].insert(buffer_index, reserve)
    if _FAULTS[2] in faults:
        ready_block, _, _ = _unique(
            [(b, j, i) for b, j, i in calls if i["fn"] == "pending_ready"],
            "pending-ready test")
        aggregate_block, _, _ = _unique(
            [(b, j, i) for b, j, i in calls if i["fn"] == "aggregate"], "aggregate call")
        finalize_block, _, _ = _unique(
            [(b, j, i) for b, j, i in calls if i["fn"] == "ready_groups"],
            "ready-groups call")
        if aggregate_block["terminator"] != {"op": "jump", "target": ready_block["label"]}:
            raise ValueError("unsupported mutation layout: aggregate backedge")
        aggregate_block["terminator"]["target"] = finalize_block["label"]
    validate_ir(document, catalog)
    if mode == "ain":
        document = encode_ain(document, catalog)
    return json.dumps(document, ensure_ascii=True, separators=(",", ":"))


def _capability_name(expression, aliases):
    """Resolve conservative direct/name-table/numeric-table function references."""
    if isinstance(expression, ast.Name):
        return aliases.get(expression.id)
    if isinstance(expression, ast.Subscript) and isinstance(expression.slice, ast.Constant):
        key = expression.slice.value
        by_id = {row["id"]: row["name"] for row in catalog_metadata()}
        if type(key) is str and key in by_id.values():
            return key
        if type(key) is int and key in by_id:
            return by_id[key]
        if key == "fn":
            return _capability_name(expression.value, aliases)
    return None


def _call_name(node, aliases=None):
    return (_capability_name(node.func, aliases or {})
            if isinstance(node, ast.Call) else None)


def _python_bindings(tree):
    """Names written by one simple assignment only; no speculative dataflow."""
    assignments = {}
    writes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            writes[node.id] = writes.get(node.id, 0) + 1
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                assignments[target.id] = node.value
            elif (isinstance(target, (ast.Tuple, ast.List)) and
                  isinstance(node.value, (ast.Tuple, ast.List)) and
                  len(target.elts) == len(node.value.elts)):
                for left, right in zip(target.elts, node.value.elts):
                    if isinstance(left, ast.Name):
                        assignments[left.id] = right
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assignments[node.target.id] = node.value
    assignments = {name: value for name, value in assignments.items()
                   if writes.get(name) == 1 and value is not None}
    aliases = {}
    values = {}
    for _ in range(len(assignments) + 1):
        before = (dict(aliases), dict(values))
        for name, value in assignments.items():
            cap = _capability_name(value, aliases)
            if cap is not None:
                aliases[name] = cap
            if isinstance(value, ast.Name) and value.id in values:
                values[name] = values[value.id]
            else:
                kind = _call_name(value, aliases)
                if kind in ("timestamp", "frontier"):
                    values[name] = kind
        if before == (aliases, values):
            break
    return aliases, values


def _scalar_origin(node, aliases, values):
    return values.get(node.id) if isinstance(node, ast.Name) else _call_name(node, aliases)


def _statement_lists(tree):
    for node in ast.walk(tree):
        for _, value in ast.iter_fields(node):
            if isinstance(value, list) and value and all(isinstance(x, ast.stmt) for x in value):
                yield value


def _corrupt_python(source, faults=None):
    faults = _selected_faults(faults)
    tree = ast.parse(source)
    aliases, values = _python_bindings(tree)
    if _FAULTS[0] in faults:
        comparison = _unique([
            node for node in ast.walk(tree) if isinstance(node, ast.Compare)
            and len(node.ops) == 1 and isinstance(node.ops[0], ast.Lt)
            and _scalar_origin(node.left, aliases, values) == "timestamp"
            and _scalar_origin(node.comparators[0], aliases, values) == "frontier"],
            "timestamp < frontier comparison with direct/single-assignment operands")
        comparison.ops[0] = ast.LtE()
    if _FAULTS[1] in faults:
        reserve_parent, reserve = _unique([
            (body, node) for body in _statement_lists(tree) for node in body
            if isinstance(node, ast.Expr) and _call_name(node.value, aliases) == "reserve"],
            "reserve statement")
        buffer_parent, buffer = _unique([
            (body, node) for body in _statement_lists(tree) for node in body
            if isinstance(node, ast.Expr) and _call_name(node.value, aliases) == "buffer"],
            "buffer statement")
        if reserve_parent is buffer_parent:
            raise ValueError("unsupported mutation layout: reserve and buffer same body")
        reserve_parent.remove(reserve)
        buffer_parent.insert(buffer_parent.index(buffer), reserve)
    if _FAULTS[2] in faults:
        parent, drain = _unique([
            (body, node) for body in _statement_lists(tree) for node in body
            if isinstance(node, ast.While) and _call_name(node.test, aliases) == "pending_ready"
            and not node.orelse], "pending-ready loop")
        parent[parent.index(drain)] = ast.If(test=drain.test, body=drain.body, orelse=[])
    ast.fix_missing_locations(tree)
    output = ast.unparse(tree) + "\n"
    compile(output, "<corrupted-participant-artifact>", "exec")
    return output


def corrupt_artifact(programstr, mode, delta):
    """Inject three defects, with explicit deterministic fallback metadata.

    Call corruption_info() immediately afterward. This side-channel is local,
    sequential runner state, not thread-safe. A fallback never qualifies as a
    genuine predecessor-preserving repair chain. Supported structural layouts
    are deliberately conservative; semantic validation belongs to the judge.
    """
    _check(mode, "repair", delta)
    global _LAST_CORRUPTION_INFO
    info = {"fallback": False, "reason": None, "faults": list(_FAULTS),
            "mutation_count": 3, "syntax_valid": True,
            "type_valid": True if mode in ("ir", "ain") else None,
            "input_sha256": hashlib.sha256(programstr.encode("utf-8")).hexdigest(),
            "method": "python_ast" if mode == "python" else "typed_ir_structure"}
    try:
        bad = (_corrupt_python(programstr) if mode == "python" else
               _corrupt_ir(programstr, mode))
    except (ValueError, TypeError, KeyError, IndexError, SyntaxError) as error:
        info["fallback"] = True
        info["reason"] = type(error).__name__ + ": " + str(error)
        replacement = canonical_changed_program(mode, delta)
        bad = (_corrupt_python(replacement) if mode == "python" else
               _corrupt_ir(replacement, mode))
        info["fallback_source_sha256"] = hashlib.sha256(
            replacement.encode("utf-8")).hexdigest()
    info["output_sha256"] = hashlib.sha256(bad.encode("utf-8")).hexdigest()
    _LAST_CORRUPTION_INFO = info
    return bad


def corruption_info():
    return copy.deepcopy(_LAST_CORRUPTION_INFO)


def corruption_variants(programstr, mode, delta):
    """Single-fault artifacts from the compound mutation's exact source.

    Reproduce the deterministic compound fallback decision, then mutate only
    one defect at a time. Existing corruption_info() state is preserved. The
    caller must behaviorally reject each variant before claiming three verified
    faults; combined rejection alone establishes no individual fault effect.
    """
    global _LAST_CORRUPTION_INFO
    saved = corruption_info()
    try:
        corrupt_artifact(programstr, mode, delta)
        source = (canonical_changed_program(mode, delta)
                  if _LAST_CORRUPTION_INFO["fallback"] else programstr)
        return {
            name: (_corrupt_python(source, [name]) if mode == "python" else
                   _corrupt_ir(source, mode, [name]))
            for name in _FAULTS
        }
    finally:
        _LAST_CORRUPTION_INFO = saved
