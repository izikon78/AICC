# AIN v0: typed register VM

This is an implemented engineering foundation for the proposed AIN research. It is **not** a trained native-token model, a representation-efficiency result, a new compiler architecture, or a production sandbox. Readable IR and numeric AIN v0 deliberately describe the **same mutable-register control-flow graph**. The numeric form is the mechanical-spelling control proposed in the [research plan](../../docs/ain/RESEARCH_PLAN.md).

`ain/language.py` validates and interprets data. It does not evaluate Python source, import modules named by programs, or turn a string into executable code. Programs can call only functions supplied in the trusted capability catalog. A capability can itself perform effects, so the catalog and host remain part of the trust boundary.

## Public API

```python
validate_ir(document, catalog) -> CompiledProgram
encode_ain(document, catalog) -> list
decode_ain(numeric_document, catalog) -> dict
run_ir(document, catalog, arguments, fuel=1_000_000) -> value
run_ain(numeric_document, catalog, arguments, fuel=1_000_000) -> value
loads_json(text_or_bytes) -> decoded_json
load_json(path) -> decoded_json
loads_ir(text_or_bytes, catalog) -> checked_readable_document
loads_ain(text_or_bytes, catalog) -> checked_numeric_document
```

`LanguageError` reports syntax, type, catalog, initialization, argument, or scalar-result contract errors. `FuelExhausted` is its subclass. Host exceptions propagate unchanged; the workflow runner, rather than this VM, decides how declared workflow errors become canonical status results. Unexpected implementation exceptions must remain visible.

Arguments are a positional list/tuple in declared parameter order. A readable program also accepts a dict containing exactly its parameter names. Numeric decoding generates names `r0`, `r1`, etc.; use positional arguments when sharing one call site between forms.

Source-file loading must use the strict JSON helpers. They reject duplicate object keys at every depth, `NaN`, infinities, and floating literals that overflow to infinity. The language has no floating-point type; even finite floats are invalid instruction constants. A caller passing an already-decoded Python dict is responsible for having preserved this parsing rule: duplicate keys already erased by a permissive parser cannot be recovered by later validation. `load_json` reads UTF-8 and permits an initial byte-order mark.

## Readable IR

The program object has exactly these fields:

```json
{
  "version": 0,
  "registers": {"a": "int", "b": "int", "answer": "int"},
  "parameters": ["a", "b"],
  "return_type": "int",
  "entry": "start",
  "blocks": [{
    "label": "start",
    "instructions": [{"op": "add", "dest": "answer", "left": "a", "right": "b"}],
    "terminator": {"op": "return", "value": "answer"}
  }]
}
```

Names are nonempty strings. Register and block names occupy separate namespaces. Registers are declared once and may be **written repeatedly**, including loop counters and registers updated across blocks. This is not SSA; duplicate declarations, block labels, parameter names, JSON keys, and catalog operation names are rejected. No instruction implicitly declares a register.

Types are exact `int`, `bool`, `str`, plus opaque `host`, `state`, `record`, `groups`, `reports`, and `result`. `void` is allowed only as a function/program return type. Integer arithmetic is exact Python-integer arithmetic, without fixed-width wraparound; the workflow host must enforce any narrower timestamp/result bounds in its own contract. Booleans are never integers for arithmetic, IDs, indices, versions, fuel, or scalar arguments/results.

| Instruction | Exact operand fields after `op` | Rule |
|---|---|---|
| `const` | `dest`, `value` | Literal exact int/bool/str; same scalar type as destination |
| `move` | `dest`, `src` | Identical source/destination types; aliases opaque values |
| `add`, `sub` | `dest`, `left`, `right` | int × int → int |
| `lt`, `le` | `dest`, `left`, `right` | int × int → bool |
| `eq` | `dest`, `left`, `right` | Equal scalar operand types → bool; no opaque comparisons |
| `not` | `dest`, `src` | bool → bool |
| `call` | `fn`, `args`, plus `dest` for a nonvoid result | Readable catalog name and ordered register-name arguments |

Every block ends with exactly one terminator:

- `{"op":"jump","target":"label"}`
- `{"op":"branch","cond":"bool_register","then":"label","else":"label"}`
- `{"op":"return","value":"register"}` for a nonvoid program
- `{"op":"return"}` for a void program

A void call **omits** `dest`; `"dest": null` is invalid. Likewise a void return omits `value`. Unknown/missing keys, undeclared references, wrong arity, incompatible types, unknown operations, and targets outside the program are errors.

## Validation before effects

Validation checks syntax and types for **all** blocks before any catalog call executes, including unreachable blocks. Every target must name a declared block. The forward must-analysis checks definite register initialization at every instruction and terminator reachable from entry. It intersects predecessor exit sets and iterates to a fixed point over loop backedges; a value produced only on a later iteration cannot justify its first read. Entry always has the parameter-only initial state, even if a backedge targets entry. Instructions read their operands before writing the destination.

Unreachable blocks remain syntax/type checked; definite initialization there is vacuous because no entry path reaches them. There is no constant-folding exception for a branch with a literal condition: both CFG edges participate in the must-analysis. The checker can conservatively reject a program whose safety would require proving a condition always true. It does not prove termination or capability semantics.

The returned `CompiledProgram` contains immutable normalized instruction/terminator tuples and a read-only snapshot of catalog records. Later mutation of the supplied dicts does not rewrite that compiled structure. Callable bodies, closures, and opaque host objects remain trusted and mutable; this is not code-integrity enforcement.

## Catalog and opaque values

The supplied catalog is a dict of nonnegative integer IDs to records with exactly `name`, `args`, `return`, `effect`, and `fn`. For example:

```python
{12: {"name": "normalize", "args": ["record"], "return": "record",
      "effect": "pure", "fn": normalize_record}}
```

Argument type lists cannot contain `void`. Effects are `pure`, `state`, `input`, `policy`, or `commit`. They are declarations and part of identity; the VM cannot inspect a function to establish that it is pure or authorized. The host decides which capabilities exist and checks dynamic authority.

Static typing keeps opaque register kinds and capability signatures distinct. The VM cannot infer a Python implementation type for an opaque value from this ABI. It therefore does not authenticate or inspect opaque arguments/results. The host's primitives must validate their records, checkpoints, scopes, and internal invariants. There is no ownership, linear-type, isolation, or secret-protection proof. Scalar arguments and scalar capability return values are checked by exact Python type at runtime; a void capability must return `None`. A bad runtime result can only be detected after that capability call, not before any effects it performed.

## Numeric AIN v0 format

The entire numeric document is a JSON list, with no JSON objects:

```text
[0, catalog_schema_sha256, register_type_codes, parameter_register_indices,
 return_type_code, entry_block_index, blocks]
```

Registers are numbered by declaration order; blocks by their list order. Each block is `[instruction_lists, terminator_list]`. All operation, register, block, and type references are integers. String constants and the catalog hash are strings; boolean constants remain booleans.

| Type | Code | Type | Code |
|---|---:|---|---:|
| int | 0 | bool | 1 |
| str | 2 | host | 3 |
| state | 4 | record | 5 |
| groups | 6 | reports | 7 |
| result | 8 | void | 9 |

| Instruction/terminator | Numeric list |
|---|---|
| const | `[0, dest, literal]` |
| move | `[1, dest, src]` |
| add / sub | `[2, dest, left, right]` / `[3, dest, left, right]` |
| lt / le / eq | `[4, dest, left, right]` / `[5, dest, left, right]` / `[6, dest, left, right]` |
| not | `[7, dest, src]` |
| call | `[8, dest_or_minus_one, catalog_ID, [arg_registers...]]` |
| jump | `[100, block]` |
| branch | `[101, condition_register, then_block, else_block]` |
| return | `[102, value_register]`; `[102]` for void |

`-1` is allowed only as a void call's destination sentinel; it is not a register index. Numeric documents undergo structural validation, catalog-identity checking, decoding, and the same full IR checker before execution. Boolean IDs/indices and out-of-range indices are rejected. There is no implicit type coercion.

Decoding reconstructs names `r0`, `r1`, … and `b0`, `b1`, … rather than retaining cosmetic source names. `encode_ain(decode_ain(encoded, catalog), catalog)` preserves the canonical numeric document. The two forms intentionally retain the same blocks, branches, calls, and effects; numeric encoding does not hide a whole workflow in a new primitive.

### Catalog identity

The hash pins the **complete supplied catalog schema**, including unused entries. Its input is a list sorted by numeric ID, each row:

```text
[ID, readable_name, [argument_type_codes...], return_type_code, effect_code]
```

Effect codes are pure=0, state=1, input=2, policy=3, commit=4. Serialize that list with Python JSON `ensure_ascii=True` and separators `(',', ':')`, then SHA-256 its ASCII bytes. Any change to an ID, name, signature, effect, or catalog membership requires re-encoding. A numeric ID cannot silently be rebound to an incompatible declared operation.

This is a schema-consistency check, not a signature or a callable implementation hash. Replacing a callable while keeping its declared metadata produces the same schema hash. Code identity and host provenance require separate frozen-source records or a stronger future mechanism. Do not describe this digest as production compatibility or security certification.

## Fuel and other limits

Each executed instruction and terminator consumes one fuel unit, including a catalog call. Fuel is a nonnegative exact integer. Zero fuel raises before the first step; exhaustion raises before the next step and never implicitly returns a partial result. A return itself consumes fuel. Fuel does not roll back previously performed effects; transactional rollback belongs to the workflow host.

Fuel bounds VM dispatch, not validation time, source size, integer allocation, wall-clock time, or work inside a capability. A blocked or expensive host function is not preempted by the VM. The host's bounded scheduler, state capacities, cancellation checks, and sink contract remain necessary.

## Executable arithmetic control-flow example

[Readable example](programs/arithmetic-example.ir.json) and [numeric example](programs/arithmetic-example.ain.json) compute the sum of integers `0 <= i < n` for a nonnegative input `n`. They contain explicit initialization, comparison, loop branch, addition, mutable-register updates, and return; their catalog is empty. For `n=10`, both return 45. A negative `n` performs zero loop iterations and returns zero.

From `experiments/ain_v0`, using the project's chosen Python interpreter:

```python
from ain.language import load_json, run_ir, run_ain
readable = load_json("programs/arithmetic-example.ir.json")
numeric = load_json("programs/arithmetic-example.ain.json")
assert run_ir(readable, {}, [10]) == 45
assert run_ain(numeric, {}, [10]) == 45
```

Run the standalone checks with `python -m unittest discover -s tests -p test_language.py -v`. Those tests cover arithmetic/loop equivalence, parsing, codec identity, type and initialization errors, invalid full programs before effects, fuel, and declared catalog/result boundaries. They do not establish that a model learns or edits this notation better than source or IR; that requires the separately frozen pilot and later research protocol.
