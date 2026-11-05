# Type errors: identical mutations through both front ends

| Level | Mutation | IR error | AIN error | Same code |
|---|---|---|---|---|
| AST | arity: epoch.group missing config | `E_ARITY`: !107 epoch.group: expected 3 arguments, got 2 | `E_ARITY`: !107 epoch.group: expected 3 arguments, got 2 | yes |
| AST | type: dedupe before admission | `E_TYPE`: !103 event.dedupe arg 1: expected Admitted, got Valid | `E_TYPE`: !103 event.dedupe arg 1: expected Admitted, got Valid | yes |
| AST | type: commit through policy handle (effect bypass) | `E_TYPE`: !113 txn.commit arg 2: expected Sink, got Policy | `E_TYPE`: !113 txn.commit arg 2: expected Sink, got Policy | yes |
| AST | type: policy and pinned swapped | `E_TYPE`: !109 policy.score arg 2: expected Policy, got Pinned | `E_TYPE`: !109 policy.score arg 2: expected Policy, got Pinned | yes |
| AST | literal: integer where Config expected | `E_LITERAL`: !105 arg 3: value of type Config required, got literal | `E_LITERAL`: !105 arg 3: value of type Config required, got literal | yes |
| AST | literal: severity 4 | `E_LITERAL`: !105 arg 2: severity literal 0..3 required | `E_LITERAL`: !105 arg 2: severity literal 0..3 required | yes |
| AST | literal: eight-value configuration | `E_LITERAL`: !010 arg 1: nine-integer list required | `E_LITERAL`: !010 arg 1: nine-integer list required | yes |
| AST | linear: stream consumed twice | `E_LINEAR_REUSE`: !107 arg 1: stream of type Epochs consumed twice | `E_LINEAR_REUSE`: !107 arg 1: stream of type Epochs consumed twice | yes |
| AST | return: returns a stream, not Outcome | `E_RETURN`: return type Retired, expected Outcome | `E_RETURN`: return type Retired, expected Outcome | yes |
| text | undefined value | `E_UNDEFINED`: stat | `E_UNDEFINED`: %29 | yes |
| text | redefined value | `E_REDEFINED`: records | `E_REDEFINED`: %03 | yes |
| text | unknown operation | `E_UNKNOWN_OP`: event.dedup | `E_UNKNOWN_OP`: !199 | yes |
| text | missing semicolon | `E_SYNTAX`: expected ;, got 'pinned' | `E_SYNTAX`: expected ;, got '%01' | yes |
| text | wrong entry signature | `E_PARAMS`: expected ('Source', 'Manifest', 'Policy', 'Sink', 'Cancel'), got ('Sink', 'Manifest', 'Policy', 'Sink', 'Cancel') | `E_UNDEFINED`: %94 | **no** |
