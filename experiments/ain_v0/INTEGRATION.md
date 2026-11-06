# AIN v0 engineering integration contract

This is a development implementation of the 5 November AIN plan. It is not a
trained native-token model or a preregistered provider comparison. The readable
IR and numeric AIN v0 are deliberately the same control-flow language under two
serializations. Do not invent a third independent representation benefit.

## Files and interfaces

`ain/language.py` owns the standalone typed register VM. Public functions:

- `validate_ir(document, catalog) -> compiled_program`
- `encode_ain(document, catalog) -> numeric_document`
- `decode_ain(numeric_document, catalog) -> readable_document`
- `run_ir(document, catalog, arguments, fuel=1000000) -> value`
- `run_ain(numeric_document, catalog, arguments, fuel=1000000) -> value`
- `LanguageError` and `FuelExhausted` exceptions.

The catalog is a dict of integer operation IDs to dicts containing `name`,
`args` (list of type-name strings), `return` (type-name string), `effect`
(`pure`, `state`, `input`, `policy`, or `commit`), and `fn` (callable).
Void return type is `void` and omits the destination key. All other destinations
have their declared type. Opaque host types: `host`, `state`, `record`,
`groups`, `reports`, `result`. Scalar types: `int`, `bool`, `str`.

Readable document shape:

```json
{"version":0,"registers":{"h":"host","s":"state"},
 "parameters":["h"],"return_type":"result","entry":"entry",
 "blocks":[{"label":"entry","instructions":[],
            "terminator":{"op":"return","value":"r"}}]}
```

This shape example is intentionally incomplete/invalid: its undeclared `r`
must be rejected. Instructions use `op` values `const`, `move`, `add`, `sub`,
`lt`, `le`, `eq`, `not`, and `call`. Operand keys:
`const(dest,value)`, `move(dest,src)`, arithmetic/comparison `(dest,left,right)`,
`not(dest,src)`, and `call(dest,fn,args)`. `fn` is the catalog's readable name.
Terminators are `jump(target)`, `branch(cond,then,else)`, and `return(value)`.
All data references are register names. Reject extra/unknown keys and duplicate
definitions. Call argument ordering is significant. The checker must verify
types, reachable block targets, definite register initialization on every path,
and return types before executing effects. Integer arithmetic is exact; bool
is not int. Use no Python eval/exec of source programs. Fuel bounds loops.
Source-file JSON parsing must reject duplicate keys and nonfinite values.

The numeric form is defined by language.py's author and documented there; it
must preserve this exact control flow and catalog identity rather than hide a
complete workflow behind one instruction. Include a simple arithmetic/loop
program to demonstrate authorable control flow outside host capabilities.

## Workflow host ABI

`ain/engine.py` owns `Host`, `Config`, `Sink`, `WorkflowError`, and the shared
primitives. `Host(records, config=None, sink=None, **options)` accepts decoded
record dictionaries. `Config` has window, lateness, dedupe_horizon, concurrency,
queue, buffered_events, dedupe_entries, open_groups, epoch_reports, minimum.
Use the values in docs/ain/COMPLEX_TASK.md as defaults. End users/tests may
use small limits. Records are envelopes:

```json
{"offset":1,"kind":"event","event":{"tenant":"t","event_id":"A","timestamp":100,"severity":0,"device":"pump","kind":"alert","message":"m"}}
```

Watermark: `{"offset":2,"kind":"watermark","timestamp":900}`.
End: `{"offset":3,"kind":"end"}`. Strict keys and bounded primitive data;
no user-defined mapping callbacks. Return results must be canonical JSON data.

`Host.catalog()` returns this shared catalog:

| ID | Name | Arguments | Return |
|---:|---|---|---|
| 0 | restore | host | state |
| 1 | has_next | host | bool |
| 2 | next_record | host | record |
| 3 | check_cancel | host | void |
| 4 | validate_record | host,state,record | void |
| 5 | record_kind | record | int |
| 6 | frontier | state | int |
| 7 | timestamp | record | int |
| 8 | seen | host,state,record | bool |
| 9 | reserve | host,state,record | void |
| 10 | severity | record | int |
| 11 | minimum | host | int |
| 12 | normalize | record | record |
| 13 | buffer | host,state,record | void |
| 14 | count | host,state,int | void |
| 15 | advance | host,state,record | void |
| 16 | pending_ready | host,state | bool |
| 17 | pop_pending | host,state | record |
| 18 | aggregate | host,state,record | void |
| 19 | ready_groups | host,state | groups |
| 20 | score | host,state,groups | reports |
| 21 | commit | host,state,reports | void |
| 22 | result | host,state | result |

Record-kind codes are event=0, watermark=1, end=2. Count categories are
late=0, duplicate=1, filtered=2, accepted=3. `advance` computes the frontier
and finite-ID eviction; end uses an internal infinity flag rather than a
sentinel integer. `frontier` is queried on the event path only. `aggregate`
implements anchored grouping; `score` owns the bounded scheduler and private
interface; `commit` owns atomic/idempotent publication and checkpointing. These
are explicitly shared semantic services, not effects invented by numeric syntax.

The language-level program itself owns the record loop, cancellation/admission
branches, first-ID-before-filter ordering, drain loop, and commit sequencing.
It does not call a whole-workflow primitive. The Python reference uses the same
catalog functions in directly written control flow. Shared primitives limit
the independence of differential comparisons; expected traces and adversarial
tests must additionally check their semantics.

`ain/reference.py` exports `run(host) -> result` for that direct program.
`ain/programs.py` (root integration) exports `workflow_ir()` and `workflow_ain()`.
`ain/runner.py` (root integration) exports
`execute(records, mode='python', config=None, sink=None, **options) -> result`,
converting expected workflow errors/cancellation into canonical status results.
Unexpected implementation errors must remain visible as test/run failures.

Host options should support deterministic test policy fixtures and fault hooks,
documented by the engine author. Required observable cases: private policy
version pinning, per-policy/pre-commit authority, deterministic smallest-index
policy error, bounded asynchronous scheduling, caller cancellation, capacity
failure, checkpoint integrity/config mismatch, fencing, failure before commit,
and lost acknowledgment after commit. Model policies remain local fixtures,
not production isolation. Keep operational scheduler telemetry separate from
canonical output/effect traces if completion timing is nondeterministic.

## Evidence boundaries

Freeze implementation/source and the development protocol before recording the
first measured run. Preserve failures and revisions. Same-session engineering
and any subsequent same-host agent-edit pilot are development evidence, not
blind independent provider trials. All monetary and billed-token fields that
are unavailable stay unmeasured. No paid API call or model adaptation is needed.
