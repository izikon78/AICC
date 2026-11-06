"""Typed mutable-register VM and two serializations of the same control flow.

AIN v0 is a mechanical numeric spelling of the readable IR.  It is an
engineering control, not evidence of a trained native-token language advantage.
Source programs are data: no Python source evaluation or dynamic import occurs.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping


class LanguageError(ValueError):
    """A malformed program, catalog, argument, or scalar capability result."""


class FuelExhausted(LanguageError):
    """The next VM instruction/terminator exceeded the execution budget."""


TYPE_NAMES = ("int", "bool", "str", "host", "state", "record", "groups",
              "reports", "result", "void")
TYPE_CODES = MappingProxyType({name: i for i, name in enumerate(TYPE_NAMES)})
EFFECT_NAMES = ("pure", "state", "input", "policy", "commit")
SCALAR_TYPES = frozenset(("int", "bool", "str"))
OPCODES = MappingProxyType({"const": 0, "move": 1, "add": 2, "sub": 3,
                           "lt": 4, "le": 5, "eq": 6, "not": 7, "call": 8})


@dataclass(frozen=True)
class CatalogOperation:
    identifier: int
    name: str
    args: tuple[str, ...]
    return_type: str
    effect: str
    fn: Callable[..., Any]


@dataclass(frozen=True)
class Block:
    instructions: tuple[tuple[Any, ...], ...]
    terminator: tuple[Any, ...]


@dataclass(frozen=True)
class CompiledProgram:
    """Immutable checked control flow; catalog callables are trusted capabilities."""

    register_names: tuple[str, ...]
    register_types: tuple[str, ...]
    parameters: tuple[int, ...]
    return_type: str
    entry: int
    blocks: tuple[Block, ...]
    operations: Mapping[int, CatalogOperation]
    catalog_schema_sha256: str


def _fail(path: str, message: str) -> None:
    raise LanguageError(f"{path}: {message}")


def _fields(value: Any, required: set[str], path: str,
            optional: frozenset[str] = frozenset()) -> None:
    if type(value) is not dict:
        _fail(path, "expected an ordinary JSON object")
    if not all(type(k) is str for k in value):
        _fail(path, "object keys must be strings")
    missing = required - value.keys()
    extra = value.keys() - required - optional
    if missing:
        _fail(path, f"missing fields {sorted(missing)!r}")
    if extra:
        _fail(path, f"unknown fields {sorted(extra)!r}")


def _list(value: Any, path: str) -> list[Any]:
    if type(value) is not list:
        _fail(path, "expected an ordinary JSON array")
    return value


def _name(value: Any, path: str) -> str:
    if type(value) is not str or not value:
        _fail(path, "expected a nonempty string")
    return value


def _integer(value: Any, path: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        _fail(path, f"expected an integer >= {minimum}; bool is not int")
    return value


def _type(value: Any, path: str, allow_void: bool = False) -> str:
    if type(value) is not str or value not in TYPE_CODES:
        _fail(path, "unknown type")
    if value == "void" and not allow_void:
        _fail(path, "void is not a register/argument type")
    return value


def _scalar(value: Any, type_name: str, path: str) -> None:
    expected = {"int": int, "bool": bool, "str": str}[type_name]
    if type(value) is not expected:
        _fail(path, f"expected exact {type_name}, got {type(value).__name__}")


def _catalog(catalog: Any) -> tuple[dict[int, CatalogOperation], dict[str, int], str]:
    if type(catalog) is not dict:
        _fail("catalog", "expected a dict of numeric IDs to operation records")
    operations: dict[int, CatalogOperation] = {}
    by_name: dict[str, int] = {}
    for identifier, record in catalog.items():
        _integer(identifier, "catalog ID")
        path = f"catalog[{identifier}]"
        _fields(record, {"name", "args", "return", "effect", "fn"}, path)
        name = _name(record["name"], path + ".name")
        if name in by_name:
            _fail(path, f"duplicate operation name {name!r}")
        arg_types = tuple(_type(t, path + ".args")
                          for t in _list(record["args"], path + ".args"))
        return_type = _type(record["return"], path + ".return", allow_void=True)
        effect = record["effect"]
        if type(effect) is not str or effect not in EFFECT_NAMES:
            _fail(path + ".effect", "unknown effect")
        if not callable(record["fn"]):
            _fail(path + ".fn", "expected a trusted callable")
        operations[identifier] = CatalogOperation(identifier, name, arg_types,
                                                  return_type, effect, record["fn"])
        by_name[name] = identifier
    schema = [[i, operations[i].name,
               [TYPE_CODES[t] for t in operations[i].args],
               TYPE_CODES[operations[i].return_type],
               EFFECT_NAMES.index(operations[i].effect)] for i in sorted(operations)]
    encoded = json.dumps(schema, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    return operations, by_name, hashlib.sha256(encoded).hexdigest()


def _uses_and_write(code: tuple[Any, ...]) -> tuple[tuple[int, ...], int | None]:
    op = code[0]
    if op == 0:
        return (), code[1]
    if op in (1, 7):
        return (code[2],), code[1]
    if op in (2, 3, 4, 5, 6):
        return (code[2], code[3]), code[1]
    return code[3], None if code[1] == -1 else code[1]


def _successors(term: tuple[Any, ...]) -> tuple[int, ...]:
    if term[0] == 100:
        return (term[1],)
    if term[0] == 101:
        return (term[2], term[3])
    return ()


def _definite_initialization(blocks: tuple[Block, ...], entry: int,
                             parameters: tuple[int, ...], names: tuple[str, ...]) -> None:
    """Greatest fixed point of the forward must analysis, including loop edges."""
    reachable: set[int] = set()
    todo = [entry]
    while todo:
        block = todo.pop()
        if block not in reachable:
            reachable.add(block)
            todo.extend(_successors(blocks[block].terminator))
    predecessors: dict[int, set[int]] = {b: set() for b in reachable}
    for b in reachable:
        for successor in _successors(blocks[b].terminator):
            predecessors[successor].add(b)
    generated: dict[int, set[int]] = {}
    for b in reachable:
        generated[b] = {write for code in blocks[b].instructions
                        for _, write in [_uses_and_write(code)] if write is not None}
    universe = set(range(len(names)))
    initial = set(parameters)
    incoming = {b: (set(initial) if b == entry else set(universe)) for b in reachable}
    outgoing = {b: incoming[b] | generated[b] for b in reachable}
    changed = True
    while changed:
        changed = False
        for b in sorted(reachable):
            new_in = (set(initial) if b == entry else
                      set.intersection(*(outgoing[p] for p in predecessors[b])))
            new_out = new_in | generated[b]
            if new_in != incoming[b] or new_out != outgoing[b]:
                incoming[b], outgoing[b] = new_in, new_out
                changed = True
    for b in sorted(reachable):
        initialized = set(incoming[b])
        for index, code in enumerate(blocks[b].instructions):
            reads, write = _uses_and_write(code)
            for read in reads:
                if read not in initialized:
                    _fail(f"blocks[{b}].instructions[{index}]",
                          f"register {names[read]!r} is not initialized on every path")
            if write is not None:
                initialized.add(write)
        term = blocks[b].terminator
        reads = ((term[1],) if term[0] == 101 or (term[0] == 102 and len(term) == 2)
                 else ())
        for read in reads:
            if read not in initialized:
                _fail(f"blocks[{b}].terminator",
                      f"register {names[read]!r} is not initialized on every path")


def validate_ir(document: Any, catalog: Any) -> CompiledProgram:
    """Check the complete document and all reachable paths without invoking capabilities."""
    operations, by_name, digest = _catalog(catalog)
    _fields(document, {"version", "registers", "parameters", "return_type", "entry", "blocks"},
            "program")
    if type(document["version"]) is not int or document["version"] != 0:
        _fail("version", "expected integer version 0")
    declarations = document["registers"]
    if type(declarations) is not dict:
        _fail("registers", "expected an object of unique names and types")
    names = tuple(_name(n, "register name") for n in declarations)
    types = tuple(_type(t, f"registers[{n!r}]") for n, t in declarations.items())
    registers = {n: i for i, n in enumerate(names)}

    def reg(name: Any, path: str) -> int:
        _name(name, path)
        if name not in registers:
            _fail(path, f"undeclared register {name!r}")
        return registers[name]

    parameters = tuple(reg(n, "parameters") for n in _list(document["parameters"], "parameters"))
    if len(set(parameters)) != len(parameters):
        _fail("parameters", "duplicate parameter")
    return_type = _type(document["return_type"], "return_type", allow_void=True)
    raw_blocks = _list(document["blocks"], "blocks")
    if not raw_blocks:
        _fail("blocks", "at least one block is required")
    labels: dict[str, int] = {}
    for index, block in enumerate(raw_blocks):
        _fields(block, {"label", "instructions", "terminator"}, f"blocks[{index}]")
        label = _name(block["label"], f"blocks[{index}].label")
        if label in labels:
            _fail("blocks", f"duplicate label {label!r}")
        labels[label] = index

    def target(name: Any, path: str) -> int:
        _name(name, path)
        if name not in labels:
            _fail(path, f"unknown block {name!r}")
        return labels[name]

    entry = target(document["entry"], "entry")
    compiled: list[Block] = []
    for block_index, raw in enumerate(raw_blocks):
        instructions: list[tuple[Any, ...]] = []
        for index, inst in enumerate(_list(raw["instructions"], f"blocks[{block_index}].instructions")):
            path = f"blocks[{block_index}].instructions[{index}]"
            if type(inst) is not dict or type(inst.get("op")) is not str:
                _fail(path, "instruction needs a string op")
            op = inst["op"]
            if op == "const":
                _fields(inst, {"op", "dest", "value"}, path)
                dest = reg(inst["dest"], path + ".dest")
                if types[dest] not in SCALAR_TYPES:
                    _fail(path, "constants can initialize scalar registers only")
                _scalar(inst["value"], types[dest], path + ".value")
                code = (0, dest, inst["value"])
            elif op in ("move", "not"):
                _fields(inst, {"op", "dest", "src"}, path)
                dest, src = reg(inst["dest"], path + ".dest"), reg(inst["src"], path + ".src")
                if types[dest] != types[src] or (op == "not" and types[src] != "bool"):
                    _fail(path, "move requires identical types; not requires bool -> bool")
                code = (OPCODES[op], dest, src)
            elif op in ("add", "sub", "lt", "le", "eq"):
                _fields(inst, {"op", "dest", "left", "right"}, path)
                dest = reg(inst["dest"], path + ".dest")
                left, right = reg(inst["left"], path + ".left"), reg(inst["right"], path + ".right")
                if op == "eq":
                    valid = types[left] in SCALAR_TYPES and types[left] == types[right] and types[dest] == "bool"
                else:
                    valid = types[left] == types[right] == "int" and types[dest] == (
                        "int" if op in ("add", "sub") else "bool")
                if not valid:
                    _fail(path, "operand/result types do not match this operation")
                code = (OPCODES[op], dest, left, right)
            elif op == "call":
                _fields(inst, {"op", "fn", "args"}, path, frozenset(("dest",)))
                name = _name(inst["fn"], path + ".fn")
                if name not in by_name:
                    _fail(path, f"unknown catalog operation {name!r}")
                identifier = by_name[name]
                operation = operations[identifier]
                args = tuple(reg(n, path + ".args") for n in _list(inst["args"], path + ".args"))
                if tuple(types[r] for r in args) != operation.args:
                    _fail(path, "call argument count/types do not match catalog")
                if operation.return_type == "void":
                    if "dest" in inst:
                        _fail(path, "void call must omit dest")
                    dest = -1
                else:
                    if "dest" not in inst:
                        _fail(path, "nonvoid call requires dest")
                    dest = reg(inst["dest"], path + ".dest")
                    if types[dest] != operation.return_type:
                        _fail(path, "call destination type does not match catalog")
                code = (8, dest, identifier, args)
            else:
                _fail(path, f"unknown instruction {op!r}")
            instructions.append(code)
        term = raw["terminator"]
        path = f"blocks[{block_index}].terminator"
        if type(term) is not dict or type(term.get("op")) is not str:
            _fail(path, "terminator needs a string op")
        op = term["op"]
        if op == "jump":
            _fields(term, {"op", "target"}, path)
            code = (100, target(term["target"], path + ".target"))
        elif op == "branch":
            _fields(term, {"op", "cond", "then", "else"}, path)
            cond = reg(term["cond"], path + ".cond")
            if types[cond] != "bool":
                _fail(path, "branch condition must be bool")
            code = (101, cond, target(term["then"], path + ".then"),
                    target(term["else"], path + ".else"))
        elif op == "return":
            _fields(term, {"op"} if return_type == "void" else {"op", "value"}, path)
            if return_type == "void":
                code = (102,)
            else:
                value = reg(term["value"], path + ".value")
                if types[value] != return_type:
                    _fail(path, "returned register does not match return_type")
                code = (102, value)
        else:
            _fail(path, f"unknown terminator {op!r}")
        compiled.append(Block(tuple(instructions), code))
    blocks = tuple(compiled)
    _definite_initialization(blocks, entry, parameters, names)
    return CompiledProgram(names, types, parameters, return_type, entry, blocks,
                           MappingProxyType(operations), digest)


def encode_ain(document: Any, catalog: Any) -> list[Any]:
    """Encode checked IR as numeric references, preserving its CFG and catalog schema."""
    program = validate_ir(document, catalog)
    blocks = []
    for block in program.blocks:
        instructions = []
        for code in block.instructions:
            instructions.append([8, code[1], code[2], list(code[3])] if code[0] == 8 else list(code))
        blocks.append([instructions, list(block.terminator)])
    return [0, program.catalog_schema_sha256, [TYPE_CODES[t] for t in program.register_types],
            list(program.parameters), TYPE_CODES[program.return_type], program.entry, blocks]


def decode_ain(numeric_document: Any, catalog: Any) -> dict[str, Any]:
    """Decode and validate; cosmetic register/block names become r0/b0, etc."""
    operations, _, digest = _catalog(catalog)
    numeric = _list(numeric_document, "AIN")
    if len(numeric) != 7 or type(numeric[0]) is not int or numeric[0] != 0:
        _fail("AIN", "expected seven-field version-0 numeric document")
    if type(numeric[1]) is not str or numeric[1] != digest:
        _fail("AIN.catalog", "catalog schema identity mismatch")

    def type_name(code: Any, path: str, allow_void: bool = False) -> str:
        _integer(code, path)
        if code >= len(TYPE_NAMES):
            _fail(path, "unknown numeric type")
        return _type(TYPE_NAMES[code], path, allow_void=allow_void)

    register_types = [type_name(t, "AIN.register_types") for t in _list(numeric[2], "AIN.register_types")]

    def register(index: Any) -> str:
        _integer(index, "AIN register")
        if index >= len(register_types):
            _fail("AIN register", "out of range")
        return f"r{index}"

    raw_blocks = _list(numeric[6], "AIN.blocks")
    if not raw_blocks:
        _fail("AIN.blocks", "at least one block is required")

    def target(index: Any) -> str:
        _integer(index, "AIN block")
        if index >= len(raw_blocks):
            _fail("AIN block", "out of range")
        return f"b{index}"

    blocks = []
    for b, raw_block in enumerate(raw_blocks):
        block = _list(raw_block, f"AIN.blocks[{b}]")
        if len(block) != 2:
            _fail("AIN block", "expected [instructions, terminator]")
        instructions = []
        for raw_code in _list(block[0], "AIN.instructions"):
            code = _list(raw_code, "AIN instruction")
            if not code:
                _fail("AIN instruction", "empty instruction")
            op = _integer(code[0], "AIN opcode")
            if op == 0 and len(code) == 3:
                inst = {"op": "const", "dest": register(code[1]), "value": code[2]}
            elif op in (1, 7) and len(code) == 3:
                inst = {"op": "move" if op == 1 else "not", "dest": register(code[1]), "src": register(code[2])}
            elif op in (2, 3, 4, 5, 6) and len(code) == 4:
                inst = {"op": ("add", "sub", "lt", "le", "eq")[op - 2],
                        "dest": register(code[1]), "left": register(code[2]), "right": register(code[3])}
            elif op == 8 and len(code) == 4:
                dest = _integer(code[1], "AIN call dest", minimum=-1)
                identifier = _integer(code[2], "AIN catalog ID")
                if identifier not in operations:
                    _fail("AIN call", "unknown catalog ID")
                inst = {"op": "call", "fn": operations[identifier].name,
                        "args": [register(r) for r in _list(code[3], "AIN call args")]}
                if dest != -1:
                    inst["dest"] = register(dest)
            else:
                _fail("AIN instruction", "unknown opcode or wrong arity")
            instructions.append(inst)
        term = _list(block[1], "AIN terminator")
        if not term:
            _fail("AIN terminator", "empty terminator")
        op = _integer(term[0], "AIN terminator opcode")
        if op == 100 and len(term) == 2:
            terminator = {"op": "jump", "target": target(term[1])}
        elif op == 101 and len(term) == 4:
            terminator = {"op": "branch", "cond": register(term[1]),
                          "then": target(term[2]), "else": target(term[3])}
        elif op == 102 and len(term) in (1, 2):
            terminator = {"op": "return"}
            if len(term) == 2:
                terminator["value"] = register(term[1])
        else:
            _fail("AIN terminator", "unknown opcode or wrong arity")
        blocks.append({"label": f"b{b}", "instructions": instructions, "terminator": terminator})
    document = {"version": 0, "registers": {f"r{i}": t for i, t in enumerate(register_types)},
                "parameters": [register(r) for r in _list(numeric[3], "AIN.parameters")],
                "return_type": type_name(numeric[4], "AIN.return_type", allow_void=True),
                "entry": target(numeric[5]), "blocks": blocks}
    validate_ir(document, catalog)
    return document


def _arguments(program: CompiledProgram, arguments: Any) -> list[Any]:
    parameter_names = [program.register_names[i] for i in program.parameters]
    if type(arguments) is dict:
        if set(arguments) != set(parameter_names):
            _fail("arguments", "mapping must contain exactly the declared parameter names")
        values = [arguments[n] for n in parameter_names]
    elif type(arguments) in (list, tuple):
        values = list(arguments)
    else:
        _fail("arguments", "expected a positional list/tuple or parameter-name dict")
    if len(values) != len(program.parameters):
        _fail("arguments", "wrong argument count")
    for reg, value in zip(program.parameters, values):
        type_name = program.register_types[reg]
        if type_name in SCALAR_TYPES:
            _scalar(value, type_name, f"argument {program.register_names[reg]!r}")
    return values


def _run(program: CompiledProgram, arguments: Any, fuel: int) -> Any:
    _integer(fuel, "fuel")
    values = _arguments(program, arguments)
    uninitialized = object()
    registers = [uninitialized] * len(program.register_names)
    for index, value in zip(program.parameters, values):
        registers[index] = value
    remaining = fuel
    block = program.entry
    while True:
        current = program.blocks[block]
        for code in current.instructions:
            if remaining == 0:
                raise FuelExhausted(f"fuel exhausted after {fuel} VM steps")
            remaining -= 1
            op, dest = code[0], code[1]
            if op == 0:
                value = code[2]
            elif op == 1:
                value = registers[code[2]]
            elif op == 2:
                value = registers[code[2]] + registers[code[3]]
            elif op == 3:
                value = registers[code[2]] - registers[code[3]]
            elif op == 4:
                value = registers[code[2]] < registers[code[3]]
            elif op == 5:
                value = registers[code[2]] <= registers[code[3]]
            elif op == 6:
                value = registers[code[2]] == registers[code[3]]
            elif op == 7:
                value = not registers[code[2]]
            else:
                operation = program.operations[code[2]]
                value = operation.fn(*(registers[r] for r in code[3]))
                if operation.return_type == "void":
                    if value is not None:
                        _fail(f"catalog {operation.name}", "void callable returned a value")
                    continue
                if operation.return_type in SCALAR_TYPES:
                    _scalar(value, operation.return_type, f"catalog {operation.name} result")
            registers[dest] = value
        if remaining == 0:
            raise FuelExhausted(f"fuel exhausted after {fuel} VM steps")
        remaining -= 1
        term = current.terminator
        if term[0] == 100:
            block = term[1]
        elif term[0] == 101:
            block = term[2] if registers[term[1]] else term[3]
        else:
            return registers[term[1]] if len(term) == 2 else None


def run_ir(document: Any, catalog: Any, arguments: Any, fuel: int = 1_000_000) -> Any:
    """Validate before executing; capability exceptions propagate unchanged."""
    return _run(validate_ir(document, catalog), arguments, fuel)


def run_ain(numeric_document: Any, catalog: Any, arguments: Any,
            fuel: int = 1_000_000) -> Any:
    """Validate catalog identity, decode, then run exactly the readable CFG."""
    return run_ir(decode_ain(numeric_document, catalog), catalog, arguments, fuel)


def loads_json(source: str | bytes | bytearray) -> Any:
    """Parse JSON while rejecting duplicate object keys and nonfinite numbers."""
    if type(source) not in (str, bytes, bytearray):
        _fail("JSON", "expected text or UTF-encoded bytes")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in items:
            if key in result:
                _fail("JSON", f"duplicate object key {key!r}")
            result[key] = value
        return result

    def nonfinite(value: str) -> None:
        _fail("JSON", f"nonfinite number {value!r}")

    def floating(value: str) -> float:
        result = float(value)
        if not math.isfinite(result):
            nonfinite(value)
        return result

    try:
        return json.loads(source, object_pairs_hook=pairs, parse_constant=nonfinite,
                          parse_float=floating)
    except LanguageError:
        raise
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise LanguageError(f"JSON: {exc}") from exc


def load_json(path: str | Path) -> Any:
    """Read a UTF-8 JSON file, allowing an initial BOM, with strict parsing."""
    return loads_json(Path(path).read_text(encoding="utf-8-sig"))


def loads_ir(source: str | bytes | bytearray, catalog: Any) -> dict[str, Any]:
    document = loads_json(source)
    validate_ir(document, catalog)
    return document


def loads_ain(source: str | bytes | bytearray, catalog: Any) -> list[Any]:
    document = loads_json(source)
    decode_ain(document, catalog)
    return document
