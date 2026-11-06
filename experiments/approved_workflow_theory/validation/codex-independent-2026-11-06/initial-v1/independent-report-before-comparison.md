# Independent recreation before reference comparison

I began without AIN background and read the start document, the replication
specification and semantic trace inputs. I wrote the counter and renderer from
the specification. I reused only workloads.py for approved component execution
and independent fixture expectations. No reference accounting.py, run.py,
report.py, article brief, reference ledger or aggregate file was read before
these outputs were frozen. reproduce.py was executed only with
--prepare-tokenizer; it verified all six pinned tokenizer hashes.

This directory preserves the first independent attempt. episodes.json contains
the complete supplied semantic episodes with independently derived request
ledgers. totals.json sums them. renderings.json preserves the actual text used
for Python counts. checks.json records boundary checks and all executable
results. manifest.json records inputs, environment and source hashes.

Python counts use the pinned Qwen tokenizer with add_special_tokens=False.
Ideal counts are declared accounting units, not measured native AIN tokens.
The common text and representation units are combined assuming equal cost per
position. Correct plans, approved components and fluency are supplied premises.
No model inference, model training, energy or planning success was measured.

Specification ambiguity: catalog_schema supplies argument names but contains no
explicit operand type schema, despite prose saying signatures supply types.
For these frozen inputs, typed rules are unambiguous from JSON value types and
the special write(program) rule. This would need elaboration for a general
implementation, particularly field-dependent equality operands.
