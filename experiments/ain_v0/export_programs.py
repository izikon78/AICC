"""Export executable matched representations and the charged semantic codebook."""
import hashlib
import json
from pathlib import Path

from ain.engine import Host
from ain.language import OPCODES, TYPE_CODES, EFFECT_NAMES, decode_ain, validate_ir
from ain.programs import workflow_ir, workflow_ain


def export():
    root = Path(__file__).resolve().parent
    target = root / "programs"
    target.mkdir(exist_ok=True)
    catalog = Host([]).catalog()
    readable, numeric = workflow_ir(), workflow_ain(catalog)
    validate_ir(readable, catalog)
    validate_ir(decode_ain(numeric, catalog), catalog)
    codebook = {"operations": {str(k): {name: value for name, value in row.items() if name != "fn"}
                                for k, row in catalog.items()},
                "opcodes": dict(OPCODES), "types": dict(TYPE_CODES),
                "effects": list(EFFECT_NAMES),
                "terminators": {"jump": 100, "branch": 101, "return": 102},
                "note": "Include LANGUAGE.md, ENGINE.md and the complex task contract. IDs alone do not specify semantics."}
    files = {"workflow.ir.json": json.dumps(readable, indent=2) + "\n",
             "workflow.ain.json": json.dumps(numeric, separators=(",", ":")) + "\n",
             "catalog.json": json.dumps(codebook, indent=2) + "\n",
             "workflow.python.py": (root / "ain" / "reference.py").read_text(encoding="utf-8")}
    for name, content in files.items():
        (target / name).write_text(content, encoding="utf-8", newline="\n")
    sizes = {name: {"utf8_bytes": len(content.encode("utf-8")),
                    "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
             for name, content in files.items()}
    sizes["ir_canonical_json_bytes"] = len(json.dumps(readable, separators=(",", ":")).encode())
    sizes["ain_canonical_json_bytes"] = len(json.dumps(numeric, separators=(",", ":")).encode())
    sizes["billing_tokens"] = None
    sizes["note"] = "Artifact bytes are not tokens or complete authoring context. All forms require the same host contract; IR/AIN additionally require their grammar/codebook."
    (target / "sizes.json").write_text(json.dumps(sizes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(sizes, indent=2))


if __name__ == "__main__":
    export()
