"""Conditional unit accounting for an already learned, fixed representation.

This is a resource model. It assigns no executable syntax and trains no model.
The illustrative vocabulary has 65,536 entries. Exactly 32,768 entries encode
15-bit payload values. Eight entries encode the list/dict/string/integer/float
types and the true/false/null atoms. Remaining entries can encode a frozen set
of approved names. The same payload entries encode lengths when a length is
expected, so lengths require no second vocabulary range.

Every new scalar uses one type unit, one byte-length unit and enough 15-bit
payload units for its UTF-8 bytes. Strings use their raw UTF-8 value. Integers
use exact decimal text and finite floats use canonical JSON text. Every list or
dict uses one type unit and one element-count unit, followed by its contents.
Every known static string, boolean or null uses one unit. Dictionary keys count.
Values and containers are bounded to 32,767 bytes/items, making each length fit
one payload unit. This fixed packing assumption applies identically to all
representations with equal semantic records. It predicts code units, not GPU
latency or the tokenizer behavior of an existing pretrained model.
"""
from __future__ import annotations

from functools import lru_cache
import json
import math


VOCABULARY_SIZE = 65_536
PAYLOAD_BITS = 15
PAYLOAD_ENTRIES = 1 << PAYLOAD_BITS
TYPE_ENTRIES = 8
MAX_LENGTH = PAYLOAD_ENTRIES - 1
MODEL = "Qwen/Qwen2.5-1.5B"
REVISION = "8faed761d45a263340a0528343f099c05c9a4323"


def _validate_symbols(static_symbols):
    symbols = frozenset(static_symbols)
    if not all(type(symbol) is str and symbol for symbol in symbols):
        raise TypeError("Static symbols must be nonempty strings")
    if len(symbols) + PAYLOAD_ENTRIES + TYPE_ENTRIES > VOCABULARY_SIZE:
        raise ValueError("Static symbols exceed the fixed vocabulary capacity")
    return symbols


def count_ideal(value, static_symbols):
    """Count a JSON-like semantic record under the frozen 15-bit unit model.

    Returned units equal static_units + structure_units + literal_units.
    literal_units is the packed payload count. literal_utf8_bytes records the
    uncompressed dynamic payload. byte_fallback_units is a sensitivity view
    charging one unit per payload byte with the same framing and static names.
    """
    symbols = _validate_symbols(static_symbols)
    counts = {"static_units": 0, "structure_units": 0,
              "literal_units": 0, "literal_utf8_bytes": 0}
    active = set()

    def scalar(payload):
        size = len(payload)
        if size > MAX_LENGTH:
            raise ValueError("Scalar payload exceeds the single-length-unit bound")
        counts["structure_units"] += 2
        counts["literal_utf8_bytes"] += size
        counts["literal_units"] += (size * 8 + PAYLOAD_BITS - 1) // PAYLOAD_BITS

    def visit(item, depth=0):
        if depth > 128:
            raise ValueError("Semantic record nesting exceeds 128 levels")
        if item is None or type(item) is bool:
            counts["static_units"] += 1
            return
        if type(item) is str:
            if item in symbols:
                counts["static_units"] += 1
            else:
                scalar(item.encode("utf-8"))
            return
        if type(item) is int:
            scalar(str(item).encode("ascii"))
            return
        if type(item) is float:
            if not math.isfinite(item):
                raise ValueError("Float payloads must be finite")
            scalar(json.dumps(item, allow_nan=False, separators=(",", ":")).encode("ascii"))
            return
        if type(item) not in (list, dict):
            raise TypeError(f"Unsupported semantic value {type(item).__name__}")
        if len(item) > MAX_LENGTH:
            raise ValueError("Container exceeds the single-length-unit bound")
        identity = id(item)
        if identity in active:
            raise ValueError("Cyclic semantic records are unsupported")
        active.add(identity)
        try:
            counts["structure_units"] += 2
            if type(item) is list:
                for child in item:
                    visit(child, depth + 1)
            else:
                if not all(type(key) is str for key in item):
                    raise TypeError("Semantic dictionary keys must be strings")
                for key in sorted(item):
                    visit(key, depth + 1)
                    visit(item[key], depth + 1)
        finally:
            active.remove(identity)

    visit(value)
    counts["units"] = counts["static_units"] + counts["structure_units"] + counts["literal_units"]
    counts["packed_literal_units"] = counts["literal_units"]
    counts["byte_fallback_units"] = (
        counts["static_units"] + counts["structure_units"] + counts["literal_utf8_bytes"])
    return counts


def count_call_stream(plan, static_symbols, schema):
    """Count an optimized approved-call ABI with fixed argument order/types.

    The program length occupies one unit. Each call uses one learned operation
    unit followed by its arguments in approved schema order. Approved parameter
    contracts supply operand types, including list element types. A signed
    integer in [-16384, 16383] occupies one 15-bit zigzag payload unit. Known
    strings and booleans occupy one unit. A list uses one length unit followed
    by its typed elements. New strings and larger scalars retain explicit type,
    length and packed payload charges. Dictionary operands use count_ideal.

    This is conditional accounting for a supplied optimized ABI. It neither
    selects new spellings nor measures an implemented model's inference units.
    The same approved-call stream applies to ideal Python and readable IR.
    """
    if type(plan) is not list or len(plan) > MAX_LENGTH:
        raise ValueError("Plan must be a bounded list of approved calls")
    if type(schema) is not dict or not all(type(name) is str for name in schema):
        raise TypeError("Schema must map operation names to ordered argument names")
    symbols = _validate_symbols(set(static_symbols) | set(schema))
    counts = {"static_units": 0, "structure_units": 1,
              "literal_units": 0, "literal_utf8_bytes": 0}
    active = set()

    def add_record(record):
        for key in counts:
            counts[key] += record[key]

    def operand(value, depth=0):
        if depth > 128:
            raise ValueError("Operand nesting exceeds 128 levels")
        if type(value) is int and -16_384 <= value <= 16_383:
            counts["literal_units"] += 1
            counts["literal_utf8_bytes"] += len(str(value).encode("ascii"))
            return
        if type(value) is list:
            if len(value) > MAX_LENGTH:
                raise ValueError("List operand exceeds the single-length-unit bound")
            if id(value) in active:
                raise ValueError("Cyclic operands are unsupported")
            active.add(id(value))
            try:
                counts["structure_units"] += 1
                for child in value:
                    operand(child, depth + 1)
            finally:
                active.remove(id(value))
            return
        add_record(count_ideal(value, symbols))

    for call in plan:
        if type(call) is not dict or set(call) != {"op", "args"}:
            raise ValueError("Each call requires exactly op and args fields")
        name = call["op"]
        if type(name) is not str or name not in schema:
            raise ValueError("Call refers to an unapproved operation")
        argument_names = schema[name]
        if (type(argument_names) not in (tuple, list)
                or not all(type(key) is str for key in argument_names)
                or len(argument_names) != len(set(argument_names))):
            raise ValueError("Approved argument schema must contain unique ordered names")
        arguments = call["args"]
        if type(arguments) is not dict or set(arguments) != set(argument_names):
            raise ValueError("Call arguments differ from the approved schema")
        counts["static_units"] += 1
        for key in argument_names:
            operand(arguments[key])
    counts["units"] = counts["static_units"] + counts["structure_units"] + counts["literal_units"]
    counts["packed_literal_units"] = counts["literal_units"]
    counts["byte_fallback_units"] = (
        counts["static_units"] + counts["structure_units"] + counts["literal_utf8_bytes"])
    return counts


def measure_message(message, python_text, static_symbols):
    """Compare text tokenization with equal-vocabulary semantic controls."""
    accounting = count_ideal(message, static_symbols)
    return {"python_text_tokens": text_token_count(python_text),
            "ideal_ain_units": accounting["units"],
            "ideal_ir_units": accounting["units"],
            "ideal_python_units": accounting["units"], **accounting}


@lru_cache(maxsize=1)
def _tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)


def text_token_count(text):
    """Count current Qwen text tokens as a separately labeled observation."""
    if type(text) is not str:
        raise TypeError("Token count input must be text")
    return len(_tokenizer().encode(text, add_special_tokens=False))
