# Source and AIN examples

Research direction and concept by Izik Bachar. Example preparation and contract
checks by Codex with collaboration agents.

`examples.json` is the single source for five article pairs. Each pair contains
conventional source, a symbolic AIN sketch, its approved operation catalog,
typed input/result contracts and its validation status. The source snippets are
at most twelve lines and the AIN sketches at most eight lines.

| Example | Conventional source | AIN function | Approved operations |
|---|---|---|---|
| Read all Users | C# with Microsoft.Data.SqlClient and DataTable | @50 | 501 open, 502 materialized query, 503 close |
| Read JSON API | Python urllib and json | @51 | 511 GET, 512 materialized JSON, 513 close |
| Manage two workers | C++20 std::jthread | @52 | 521 spawn, 523 join |
| Sum paid orders | Ruby Hash and each | @53 | 531 boolean filter, 532 integer-cent sum, 533 sorted keys |
| Active user emails | Java 17 record and streams | @54 | 541 boolean filter, 542 field projection, 543 distinct, 544 sorted immutable sequence |

The numeric operation identifiers are example-local assignments with explicit
contracts. Function identifiers and operation references occupy separate roles.
The displayed @/!/return notation follows the standalone theory sketch. Argument
and resource obligations remain explicit. Approved implementations supply those
obligations under the article's premise.

Database and HTTP operations return materialized results before explicit close.
Their assumed ownership contract also performs cleanup on failed operations or
early scope exits. The C++ example supplies approved cooperative workers with
internal exception handling. Abnormal scope exit requests stop and joins any
remaining owned workers. Completion order stays unconstrained.

The Ruby example uses boolean paid flags, ASCII customer names and exact integer
cents, including refunds. Its result has ascending key iteration order. The Java
example uses non-null ASCII email values. Equality and ordering are case-sensitive,
and its final sequence is immutable. These bounded data contracts make the
documentary comparisons and deterministic mock expectations precise.

## Check the examples

From the repository root using Python 3.12,

```text
python publication/examples/validate_examples.py
```

The helper checks every displayed operation identifier, approved arity, catalog
uniqueness, expected call order, return bundle and print line budget. It runs
thirteen deterministic mock contract scenarios, including connection and query
failure cleanup, HTTP parsing/decoding failures, reverse worker completion,
failed second spawn, integer refunds and empty/duplicate email cases.

`validation.json` records the checks and the hash of `examples.json`. The helper
does no DB/network work, starts no OS threads and performs no AIN compilation.
It checks the declared illustrative contracts rather than establishing actual
multi-language or model-generated execution performance. The C#, C++, Ruby and
Java snippets are documentary source examples reviewed against their API
contracts. The current experiment has no native implementation of these new
example-local catalog operations.

The final article uses one symbolic style for all five examples. Its measured
result charts use the saved experimental ledgers, independently of how these
sketches are printed. See [the standalone theory](../AIN_THEORY.md).

## Run the existing AICC binding example

`aicc_binding.py` exercises the preserved processing prototype in process. From
the repository root,

```text
python publication/examples/aicc_binding.py
```

The three checks compare a bound call with the reference implementation, restore
its exported record on a compatible receiving host, and reject an incompatible
receiving requirement. `aicc-binding-validation.json` preserves the checked output
signature. This example uses fifty deterministic events and makes no model calls.
Its checks run within the prototype's trusted process.
