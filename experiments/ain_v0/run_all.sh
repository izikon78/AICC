#!/usr/bin/env bash
# Reproduce every AIN v0 result. Run from experiments/ain_v0. Token counts need tiktoken (o200k_base).
set -u
sec() { echo; echo "================================================================ $*"; }
sec "Environment"; python3 -c "import sys, unicodedata; print('python', sys.version.split()[0], '| unicode', unicodedata.unidata_version)"
sec "Front ends: verbatim AIN sketch and IR parse to one AST"
python3 -c "
import sys; sys.path.insert(0, '.')
from ain_v0 import core
a = core.parse_ain(open('programs/workflow.ain').read()); i = core.parse_ir(open('programs/workflow.ir').read())
print('identical AST:', a == i, '| check:', core.check(a)['effects'], '| AIN round trip:', core.parse_ain(core.to_ain(a)) == a)"
sec "Conformance suite (hand, crash, random differential, type errors, sink)"; python3 conformance/run_conformance.py
sec "Mutation adequacy"; python3 conformance/mutants.py
sec "Lowering listing"; cat programs/workflow.lowered.txt
sec "Tokenizer counts (not billing)"; cat measurements/token_counts.txt
