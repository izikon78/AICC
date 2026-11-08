# AIN language theory and example contracts

Concept, architecture and research direction by Izik Bachar. This standalone
description is sufficient background for the reproduction package. It contains
no expected experiment totals. No earlier article is required.

## The premise

AIN means AI Native Language and is the reference name for a theoretical language and compilation architecture. The complete proposed system is conceptual; the current repository contains bounded implementations and experiments. The research asks whether an agent that already
knows a precise, compact computational representation can complete software work
with fewer total resources. Approved implementations of reusable operations are
available before evaluation. Their established internal code can contain
functions, methods, branches, for loops, while loops and other control flow.

An operation reference carries meaning through a stable contract. Its printed
identifier is a human-visible projection of that reference. Arguments, new
literal values, operation order, branches and any newly authored logic still
carry information. A short string does not establish a particular tokenizer
length or a particular inference cost. Experiments must state which representation
they execute and which unit they count.

AIN concerns the agent's authoring, editable records and interaction interface.
AICC, the AI Computational Commons, concerns discovering, approving, binding,
versioning and reusing the operations. Conventional languages must receive the
same approved implementations and information in a fair comparison.

## Native compilation and learned method references

The concept compiles AIN source to native machine code, using approved native
implementations where appropriate. Internal IR and optimization passes remain
compatible with this aim. The agent does not need to generate a human-language
source program as an intermediate output.

AI may construct and optimize the language/compiler and learn reusable
implementation decompositions. Under the reference premise those mappings are
already known before compilation. The compiler resolves a short operation ID,
expands or lowers its known functionality, or links an approved native method.
Changes produced by further learning have versioned implementations and contracts.

For the database example, `!501(config)` has the high-level meaning
`ConnectToDB(config)`. It can stand for reading configuration, allocating owned
connection state, opening a driver connection, handling failures and returning
the owned handle. The caller sees a black box with a known contract; the compiler
and catalog know how it is implemented. It can compile to many instructions and
native calls. The identifier itself is neither the implementation nor a single
CPU instruction. Operation 502 executes the explicit SQL; 503 releases ownership.

The database decomposition is illustrative. The existing compact arithmetic
compiler provides a bounded actual source-to-native example. The reference
concept makes no claim that a complete database-capable AIN compiler exists.
Conventional languages receive the same approved implementations in comparisons.

## The illustrated notation

| Form | Meaning |
|---|---|
| `@50(c) { ... }` | Define a function with an identifier and ordered parameters |
| `d=!501(c);` | Invoke an operation with explicit operands and assign its result |
| `!503(d);` | Invoke an effectful operation without assigning a value |
| `?(condition):^[value]` | Return the stated result bundle when the condition holds |
| `e[2]` | Access a contract-defined field or slot |
| `^[r];` | Return a bundle containing the result |

These forms describe the article's symbolic view. They are a theory sketch with
example-local operation assignments, rather than a complete standardized
grammar. Function IDs and operation IDs have separate roles. Their spelling
does not grant permission to execute an operation. A host must resolve the
reference under the current contract and authority.

## A database example

```text
@50(c) {
  d=!501(c);
  r=!502(d,"SELECT * FROM Users");
  !503(d);
  ^[r];
}
```

Operation 501 opens the supplied SQL Server configuration. Operation 502 runs
the explicit query and returns a fully materialized table. Its implementation
owns the command and reader. Operation 503 closes the connection. The assumed
function ownership contract also releases resources on connection failure,
query failure and early exit. Configuration and SQL remain explicit inputs.

The [example catalog](examples/examples.json) defines five source/AIN pairs for
C#, Python, C++, Ruby and Java. It supplies operation arities, argument meaning,
resource obligations, result ordering and bounded data assumptions. The examples
illustrate behavior through mock contract checks. They do not provide implemented
database, network or concurrency frontends for a complete AIN system.

## Semantics that compact notation must retain

Compact references require the same behavioral precision as source code. A
materialized query must remain usable after its connection closes. An owned
thread must have defined join and abnormal-exit behavior. Sorting must state its
ordering domain. Integer arithmetic must declare its range and overflow rule.
An event pipeline must state whether lateness, duplicate reservation and filtering
occur before or after one another. Changing any such order can change results.

New combinations remain an authoring task even when their components are
approved. Core approval establishes component behavior. It does not guarantee
that an agent selects the right component, arguments or control flow. A theory
experiment may supply correct compositions to isolate representation demand;
a learned-agent experiment must measure composition failures and repair work.

## From notation to measurement

The reproduction instructions distinguish executable source, semantic traces,
ordinary tokenizer counts and modeled learned-code units. The symbolic examples
are not the serialization used by every experiment. A result must identify its
actual format and counting rule. Equal cost per counted unit is an explicit
modeling assumption when measured text tokens are compared with ideal units.

Independent reconstruction should implement the specified accounting from its
contracts and semantic inputs before inspecting expected outputs. Reading this
theory document does not reveal those totals. Reading the article, prior results
or supplied expected ledgers is prior exposure and must be disclosed by a
reproducer.
