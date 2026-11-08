"""Compile a bounded scalar subset through the existing typed IR to native code.

Compact AIN spells the existing add/sub opcodes as ``2 n;3 n``. The frontend
supplies the accumulator, constant registers, types, single block and return.
Readable IR supplies exactly the same fields for ``add n;sub n``. Python accepts
an expression such as ``x+7-4`` or the prior screen's plain solve(x) function.

The admitted domain is exact integer arithmetic with at most 16 operations,
input and literal magnitudes at most one million. Thus every intermediate is
bounded by 17 million, and signed i64 lowering preserves the VM semantics.
"""
from __future__ import annotations

import ast
import ctypes
from dataclasses import dataclass, field
import re
import time
from typing import Any

from experiments.ain_v0.ain.language import OPCODES, validate_ir


MAX_MAGNITUDE = 1_000_000
MAX_STEPS = 16
MAX_TEXT = 4096
_NUMERIC_OPERATIONS = {str(OPCODES[name]): name for name in ("add", "sub")}
_READABLE_OPERATIONS = {name: name for name in ("add", "sub")}
_LLVM_READY = False


def _literal(node):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _literal(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    raise ValueError("each accumulator operation needs an integer literal")


def _python_steps(text):
    tree = ast.parse(text)
    if len(tree.body) != 1 or len(list(ast.walk(tree))) > 128:
        raise ValueError("expected one small accumulator expression or solve(x) function")
    statement = tree.body[0]
    if isinstance(statement, ast.Expr):
        expression = statement.value
    elif isinstance(statement, ast.FunctionDef):
        arguments = statement.args
        if (statement.name != "solve" or len(arguments.args) != 1
                or arguments.args[0].arg != "x" or arguments.args[0].annotation
                or arguments.posonlyargs or arguments.kwonlyargs or arguments.vararg
                or arguments.kwarg or arguments.defaults or arguments.kw_defaults
                or statement.decorator_list or statement.returns or statement.type_comment
                or getattr(statement, "type_params", []) or len(statement.body) != 1
                or not isinstance(statement.body[0], ast.Return)):
            raise ValueError("expected a plain solve(x) function with one return expression")
        expression = statement.body[0].value
    else:
        raise ValueError("expected an accumulator expression or solve(x) function")
    steps = []

    def visit(node):
        if isinstance(node, ast.Name) and node.id == "x":
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            visit(node.left)
            if len(steps) >= MAX_STEPS:
                raise ValueError("program exceeds 16 arithmetic operations")
            steps.append(("add" if isinstance(node.op, ast.Add) else "sub",
                          _literal(node.right)))
            return
        raise ValueError("expected x followed by addition/subtraction of integer literals")

    visit(expression)
    return steps


def _compact_steps(arm, text):
    operations = _NUMERIC_OPERATIONS if arm == "ain" else _READABLE_OPERATIONS
    steps = []
    for instruction in text.strip().split(";"):
        match = re.fullmatch(r"\s*([^\s;]+)\s+([+-]?[0-9]{1,8})\s*", instruction)
        if match is None or match.group(1) not in operations:
            raise ValueError("expected supported opcode and integer literal per instruction")
        steps.append((operations[match.group(1)], int(match.group(2))))
    return steps


def parse_program(arm: str, text: str) -> dict[str, Any]:
    """Expand the declared compact subset and validate using the existing VM."""
    if type(text) is not str or not text.strip() or len(text) > MAX_TEXT:
        raise ValueError("expected nonempty program text of at most 4096 characters")
    if arm not in ("python", "ir", "ain"):
        raise ValueError(f"unknown arm {arm!r}")
    steps = _python_steps(text) if arm == "python" else _compact_steps(arm, text)
    if len(steps) > MAX_STEPS:
        raise ValueError("program exceeds 16 arithmetic operations")
    if any(abs(value) > MAX_MAGNITUDE for _, value in steps):
        raise ValueError("literal magnitude exceeds one million")
    instructions = []
    source = "x"
    for operation, value in steps:
        instructions.extend([
            {"op": "const", "dest": "c", "value": value},
            {"op": operation, "dest": "y", "left": source, "right": "c"},
        ])
        source = "y"
    document = {
        "version": 0, "registers": {"x": "int", "c": "int", "y": "int"},
        "parameters": ["x"], "return_type": "int", "entry": "b",
        "blocks": [{"label": "b", "instructions": instructions,
                    "terminator": {"op": "return", "value": source}}],
    }
    validate_ir(document, {})
    return document


@dataclass
class NativeProgram:
    """Own the execution engine for the complete lifetime of its native function."""

    assembly: str
    llvm_ir: str
    compile_seconds: float
    _engine: Any = field(repr=False)
    _module: Any = field(repr=False)
    _function: Any = field(repr=False)

    def run(self, value: int) -> int:
        if type(value) is not int or abs(value) > MAX_MAGNITUDE:
            raise ValueError("input must be an exact integer with magnitude at most one million")
        return self._function(value)


def compile_program(arm: str, text: str) -> NativeProgram:
    """Parse, validate, optimize, emit assembly and JIT the same i64 backend."""
    from llvmlite import binding, ir

    started = time.perf_counter()
    document = parse_program(arm, text)
    checked = validate_ir(document, {})
    global _LLVM_READY
    if not _LLVM_READY:
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        _LLVM_READY = True
    target = binding.Target.from_default_triple()
    target_machine = target.create_target_machine(
        cpu=binding.get_host_cpu_name(), features=binding.get_host_cpu_features().flatten(),
        opt=3,
    )
    module = ir.Module(name="scalar_gate")
    module.triple = binding.get_default_triple()
    module.data_layout = str(target_machine.target_data)
    integer = ir.IntType(64)
    function = ir.Function(module, ir.FunctionType(integer, [integer]), name="solve")
    function.args[0].name = "x"
    builder = ir.IRBuilder(function.append_basic_block("entry"))
    registers = {checked.parameters[0]: function.args[0]}
    for code in checked.blocks[0].instructions:
        if code[0] == OPCODES["const"]:
            registers[code[1]] = ir.Constant(integer, code[2])
        elif code[0] == OPCODES["add"]:
            registers[code[1]] = builder.add(registers[code[2]], registers[code[3]])
        else:
            registers[code[1]] = builder.sub(registers[code[2]], registers[code[3]])
    builder.ret(registers[checked.blocks[0].terminator[1]])
    native_module = binding.parse_assembly(str(module))
    native_module.verify()
    optimizer = binding.create_pass_manager_builder()
    optimizer.opt_level = 3
    passes = binding.create_module_pass_manager()
    optimizer.populate(passes)
    passes.run(native_module)
    assembly = target_machine.emit_assembly(native_module)
    engine = binding.create_mcjit_compiler(binding.parse_assembly(""), target_machine)
    engine.add_module(native_module)
    engine.finalize_object()
    engine.run_static_constructors()
    address = engine.get_function_address("solve")
    if address == 0:
        raise RuntimeError("LLVM did not emit the solve function")
    callable_function = ctypes.CFUNCTYPE(ctypes.c_int64, ctypes.c_int64)(address)
    return NativeProgram(assembly, str(native_module), time.perf_counter() - started,
                         engine, native_module, callable_function)
