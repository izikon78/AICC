"""Synthetic scalar authoring data for a bounded learning feasibility gate.

Training and development use add, sub, and add/add structures. Development
constants are disjoint. Structural holdouts use sub/add, add/sub, and sub/sub.
These affine programs can have equivalent simplified implementations, which the
judge accepts. This narrow split cannot establish broad program generalization.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys


V0 = Path(__file__).resolve().parents[1] / "ain_v0"
if str(V0) not in sys.path:
    sys.path.insert(0, str(V0))

from ain.language import encode_ain, loads_ain, loads_ir, run_ain, run_ir  # noqa: E402


ARMS = ("python", "ir", "ain")
FORMATS = {
    "python": "Python function solve(x)",
    "ir": "readable typed IR JSON",
    "ain": "numeric AIN JSON",
}
CASES = (-17, -2, 0, 1, 9, 31, 1047)


def _oracle(steps, value):
    """Evaluate the semantic task independently of generated source/VM code."""
    for operation, constant in steps:
        if operation == "add":
            value += constant
        else:
            value -= constant
    return value


def _targets(steps):
    expression = "x"
    instructions = []
    source = "x"
    for operation, constant in steps:
        symbol = "+" if operation == "add" else "-"
        expression = f"({expression} {symbol} {constant})"
        instructions.extend([
            {"op": "const", "dest": "c", "value": constant},
            {"op": operation, "dest": "y", "left": source, "right": "c"},
        ])
        source = "y"
    document = {
        "version": 0, "registers": {"x": "int", "c": "int", "y": "int"},
        "parameters": ["x"], "return_type": "int", "entry": "b",
        "blocks": [{"label": "b", "instructions": instructions,
                    "terminator": {"op": "return", "value": "y"}}],
    }
    return {
        "python": f"def solve(x):\n    return {expression}",
        "ir": json.dumps(document, separators=(",", ":")),
        "ain": json.dumps(encode_ain(document, {}), separators=(",", ":")),
    }


def _row(split, family, index, steps):
    clauses = [f"{'add' if operation == 'add' else 'subtract'} {constant}"
               for operation, constant in steps]
    return {
        "id": f"{split}-{family}-{index:03d}",
        "split": split,
        "family": family,
        "prompt": ("Write a program with one integer input x. Starting with x, "
                   + ", then ".join(clauses) + ". Return the resulting integer. "
                   "Output only the program in {format}."),
        "steps": [[operation, constant] for operation, constant in steps],
        "targets": _targets(steps),
    }


def make_dataset():
    """Return 96 train, 12 dev, and 12 structural-holdout paired examples."""
    rows = []
    for operation in ("add", "sub"):
        for index, constant in enumerate(range(1, 33)):
            rows.append(_row("train", operation, index, [(operation, constant)]))
        for index, constant in enumerate(range(101, 105)):
            rows.append(_row("dev", operation, index, [(operation, constant)]))
    for index in range(32):
        steps = [("add", index // 4 + 1), ("add", index % 4 + 1)]
        rows.append(_row("train", "add_add", index, steps))
    for index in range(4):
        rows.append(_row("dev", "add_add", index,
                         [("add", 101 + index), ("add", 105 + index)]))
    for operations in (("sub", "add"), ("add", "sub"), ("sub", "sub")):
        for index in range(4):
            steps = [(operations[0], 3 + index), (operations[1], 9 + index)]
            rows.append(_row("holdout", "_".join(operations), index, steps))
    return rows


def format_prompt(row, arm):
    """Add only the requested format label, with no grammar or examples."""
    return row["prompt"].format(format=FORMATS[arm]) + "\n"


def _python_expression(text):
    tree = ast.parse(text)
    if len(list(ast.walk(tree))) > 128 or len(tree.body) != 1:
        raise ValueError("expected one small solve function")
    function = tree.body[0]
    if not isinstance(function, ast.FunctionDef) or function.name != "solve":
        raise ValueError("expected function solve(x)")
    arguments = function.args
    if (len(arguments.args) != 1 or arguments.args[0].arg != "x"
            or arguments.posonlyargs or arguments.kwonlyargs or arguments.vararg
            or arguments.kwarg or arguments.defaults or arguments.kw_defaults
            or function.decorator_list or function.returns
            or arguments.args[0].annotation or function.type_comment
            or getattr(function, "type_params", [])):
        raise ValueError("expected plain function solve(x)")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.Return):
        raise ValueError("expected a single return expression")
    expression = function.body[0].value

    def check(node, depth=0):
        if depth > 16:
            raise ValueError("expression is too deep")
        if isinstance(node, ast.Name) and node.id == "x":
            return
        if (isinstance(node, ast.Constant) and type(node.value) is int
                and abs(node.value) <= 1_000_000_000):
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            check(node.left, depth + 1)
            check(node.right, depth + 1)
            return
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            check(node.operand, depth + 1)
            return
        raise ValueError("only x, integer literals, addition and subtraction are allowed")

    check(expression)
    return expression


def _run_python(expression, value):
    if isinstance(expression, ast.Name):
        return value
    if isinstance(expression, ast.Constant):
        return expression.value
    if isinstance(expression, ast.UnaryOp):
        return -_run_python(expression.operand, value)
    left = _run_python(expression.left, value)
    right = _run_python(expression.right, value)
    return left + right if isinstance(expression.op, ast.Add) else left - right


def judge(arm, text, row):
    """Judge a complete output without evaluating arbitrary Python source.

    syntax_ok includes structural/type validation. correct requires exact integer
    results for every independent input. VM execution has a 1000-instruction cap.
    """
    syntax_ok = False
    try:
        if type(text) is not str or len(text) > 32768:
            raise ValueError("expected program text of at most 32768 characters")
        if arm == "python":
            program = _python_expression(text)
            run = lambda value: _run_python(program, value)
        elif arm == "ir":
            program = loads_ir(text, {})
            run = lambda value: run_ir(program, {}, [value], fuel=1000)
        elif arm == "ain":
            program = loads_ain(text, {})
            run = lambda value: run_ain(program, {}, [value], fuel=1000)
        else:
            raise ValueError(f"unknown arm {arm!r}")
        syntax_ok = True
        for value in CASES:
            actual = run(value)
            expected = _oracle(row["steps"], value)
            if type(actual) is not int or actual != expected:
                return {"syntax_ok": True, "correct": False,
                        "error": f"wrong result for x={value}: {actual!r} != {expected}"}
        return {"syntax_ok": True, "correct": True, "error": None}
    except Exception as error:
        return {"syntax_ok": syntax_ok, "correct": False,
                "error": f"{type(error).__name__}: {error}"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(make_dataset(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
