"""Matched compact-source tasks for a bounded native compiler learning screen.

The semantic tasks and splits come from the earlier 96/12/12 scalar gate. All
programs are affine integer functions and several held-out compositions share
the same net offset. This screen measures executable fluency and serialization
size. The pretrained model's Python familiarity remains a confound.
"""
from __future__ import annotations

import hashlib

from experiments.native_learning_gate.data import make_dataset as make_legacy_dataset


ARMS = ("python", "ir", "ain")
FORMATS = {
    "python": "a Python expression in x",
    "ir": "compact readable IR",
    "ain": "compact numeric AIN",
}
CASES = (-1_000_000, -17, -2, 0, 1, 9, 31, 1047, 1_000_000)


def _compact_targets(steps):
    expression = "x"
    readable = []
    numeric = []
    for operation, constant in steps:
        symbol = "+" if operation == "add" else "-"
        opcode = 2 if operation == "add" else 3
        expression += f"{symbol}{constant}"
        readable.append(f"{operation} {constant}")
        numeric.append(f"{opcode} {constant}")
    return {"python": expression, "ir": ";".join(readable), "ain": ";".join(numeric)}


def make_dataset():
    """Reuse every prior semantic row and retain its complete-envelope targets."""
    rows = make_legacy_dataset()
    for row in rows:
        row["legacy_targets"] = row["targets"]
        row["targets"] = _compact_targets(row["steps"])
        row["prompt"] = row["prompt"].replace(
            "Output only the program in {format}.", "Output only {format}.")
    return rows


def format_prompt(row, arm):
    """Supply a task and format label, with no grammar or worked example."""
    return row["prompt"].format(format=FORMATS[arm]) + "\n"


def _oracle(steps, value):
    """Calculate expectations independently of the parser, VM and compiler."""
    for operation, constant in steps:
        if operation == "add":
            value += constant
        else:
            value -= constant
    return value


def judge(arm, text, row):
    """Compile a strictly parsed candidate and execute native code on all cases.

    syntax_ok includes compiler validation. compiler_seconds is the compiler's
    measured parsing, lowering and JIT setup time for successfully compiled
    candidates. assembly_sha256 identifies the emitted assembly without placing
    repeated assembly text in every prediction record.
    """
    from experiments.ain_compiler_gate.compiler import compile_program

    syntax_ok = False
    compiler_seconds = 0.0
    assembly_sha256 = None
    try:
        compiled = compile_program(arm, text)
        syntax_ok = True
        compiler_seconds = compiled.compile_seconds
        assembly_sha256 = hashlib.sha256(compiled.assembly.encode("utf-8")).hexdigest()
        for value in CASES:
            actual = compiled.run(value)
            expected = _oracle(row["steps"], value)
            if type(actual) is not int or actual != expected:
                return {"syntax_ok": True, "correct": False,
                        "error": f"wrong result for x={value}: {actual!r} != {expected}",
                        "compiler_seconds": compiler_seconds,
                        "assembly_sha256": assembly_sha256}
        return {"syntax_ok": True, "correct": True, "error": None,
                "compiler_seconds": compiler_seconds, "assembly_sha256": assembly_sha256}
    except Exception as error:
        return {"syntax_ok": syntax_ok, "correct": False,
                "error": f"{type(error).__name__}: {error}",
                "compiler_seconds": compiler_seconds, "assembly_sha256": assembly_sha256}
