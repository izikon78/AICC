# AIN language theory and example contracts

Concept, architecture and research direction by Izik Bachar. This standalone
description is sufficient background for the reproduction package. It contains
no expected experiment totals. No earlier article is required.

## The premise

AIN means AI Native Language. The research asks whether an agent that already
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
