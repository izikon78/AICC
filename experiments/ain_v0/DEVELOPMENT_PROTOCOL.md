# AIN v0 first execution: development protocol

This file is written before the first measured AIN v0 run. This is an engineering
development study, not an independently preregistered comparison. All three
programs use the same semantic host functions. The readable typed IR and numeric
AIN are mechanically equivalent representations of one register language.

## Questions this run can answer

1. Can explicit language control flow express the complex streaming contract,
   including admission order, drain loops, policy effects and checkpoint commits?
2. Do expected traces, adversarial cases, replay/fault tests and seeded generated
   streams agree across Python, readable IR and numeric AIN?
3. What are source size, load/check cost and observed local processing costs for
   this particular Python interpreter implementation?

The study cannot establish that an AI has learned a native language, that numeric
opcodes reduce billed tokens, that a custom tokenizer is useful, or that money
or energy has been saved. It cannot isolate the semantics implemented by shared
primitives as an effect of syntax. Private policy is a local fixture, not a
production security boundary. There is no compiler/JIT performance claim.

## Development, freezing and recording

Implement the host, direct Python program, typed validator/interpreter, numeric
codec, and expected-outcome tests. Record material development failures and fixes
in DEVELOPMENT_LOG.md. Run conformance first. Freeze all study source files by
SHA-256 in each recorded result set; retain the protocol hash. A changed source
requires a new result set, never rewriting old measurements as if unchanged.

For the local performance pilot use seeded complex event streams: repeated keys,
many keys and late/duplicate/filter-heavy input; 20,000 events each, three
fresh-worker repetitions per form, nine cells and 27 workers. Use the same event
stream in all forms. Every worker measures generation separately, program
construction separately, validation/decode separately where supported, and
execution with the program's checking included. Report full worker time and
Python allocation peak in addition to execution. No selective deletion of slow
runs. Canonical output checksums must match for all arms of each workload. Check
correctness before measuring. Record failures rather than replacing them silently.

Concurrency bounds are an independent correctness fixture; the throughput fixture
uses a deterministic local policy with no paid model endpoint. Randomize worker
order with a fixed seed. Timings describe this machine and implementation only;
the interpreter is expected to have overhead compared with direct Python.

The separate check timing is diagnostic, additional work: readable IR is checked
there and again by its run entry point; numeric AIN is checked during encoding,
decoded/checked during preflight and decoded/checked by execution. Full worker
time includes those preflight passes, generation and result hashing. Execution
time includes host construction, validation and checks inside the run entry
point. `tracemalloc` is enabled only for host construction/execution and adds
overhead. Process peak memory includes the full copied input, committed reports,
transaction trace/history and checkpoint copies; it is not isolated active-stream
memory and does not establish constant process memory. These scopes are retained
for all 27 workers rather than selected after observing results.

## Optional agent editing pilot

Only after freezing a working implementation and its judge, a small same-session
editing pilot may ask fresh agent contexts to make bounded edits in each form.
Use the same task and semantic services, explicit equivalent metadata and a
fixed attempt limit. Record instructions, returned artifacts, judge outcomes and
observable time. This is a public development pilot, not a securely blinded
heldout comparison: the agents share a host/filesystem and underlying model
identity, billed tokens and dollar cost may not be exposed. If unavailable,
leave authoring performance unmeasured. Model adaptation and dedicated native
token training remain separate future phases.
