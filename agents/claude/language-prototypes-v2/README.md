# Language A / Language B prototypes (v2 review, 2026-11-02)

The runtime the archive review lists as missing (`/home/claude/sym`). Research prototypes, not a standard.
- `lang.py`: shared AST, Language A parser, type checker, interpreter, Language B opcode encoder and decoder, Python and C# projections.
- `spec_a.txt`: the 317-token Language A reference sheet.
- `a_b_results.json`: serialized Language B token streams and templates for the controller example (`b_tokens`, `b_templates`).
- `run_traces.py`, `mutate.py`, `prod.py`, `measure.py`, `b_extra.py`, `variants.py`: traces, mutation tests, production-scale estimate, token measurements.
- `count.js`, `countlist.js`, `tokstr.js`, `tok.py`: tokenizer helpers (npm gpt-tokenizer, llama3-tokenizer-js, @lenml tokenizers).
- `progs/`: baseline programs (C#, Python, Forth, APL, Racket, WAT) used in the token comparison.
Results are reported in the v2 review document (Claude Docs). No trained model was used.
