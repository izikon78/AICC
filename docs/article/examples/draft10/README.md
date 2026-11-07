# Real approved-core examples for Draft 10

The source is events-00 in the frozen trace-inputs.json. Build composes five
approved functions. Change raises minimum severity from 2 to 3. Repair changes
the injected timestamp comparison back from filter_gte to filter_lt. The actions
are supplied correct traces, not new model-generated code.

projection.py is a new article-only numeric display codec. Opcode IDs follow
catalog_schema insertion order, starting at 1. Symbol IDs follow the frozen
63-entry static_symbols list, starting at 1. Explicit typed value tags make the
printed numeric JSON lossless. These extra display tags are not the ideal units
charged by the original test. The display is not a finalized AIN grammar.

snippets.json contains the article excerpts and their complete legend. The Python
view changes whitespace only, verified through AST equality. The unchanged shared
dedupe_by function demonstrates the real approved loop. All 144 semantic episodes
round-trip the new display projection, preserve actions and final artifacts, and
match the approved execution oracle; qualification.json preserves the checks.

Run from the repository root with Python 3.12:

    python docs/article/examples/draft10/projection.py

Do not compare the token count of this printed numeric display with Python text
and present it as the test's result. The reported 24.0% and 12.8% reductions are
derived from the separately frozen code-unit accounting and complete ledgers.
