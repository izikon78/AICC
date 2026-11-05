# Research binding runtime

`aicc_processing/runtime.py` implements an in-process host-side binding experiment. It is not a production security boundary, authentication system, effect sandbox, signature verifier, or formal compatibility prover.

## API

```python
runtime = Runtime(environment={"dataset_contract": "v1"})
capability = runtime.register(
    "events.aggregate@1", process_function,
    obligations=("exact-grouping",),
    properties={"window_rule": "anchored-strict"},
    dependencies={"kernel_bundle": "a version or trusted digest"},
)
alias = runtime.bind(
    "events.aggregate@1",
    obligations=("exact-grouping",),
    requirements={"window_rule": "anchored-strict"},
)
groups = alias(events, window=600)
record = alias.export_record()
```

Default anonymous access can bind public, pure capabilities. For restricted capability scopes/effects, a trusted host first calls `authorize(principal, scopes=(...), allowed_effects=(...))`. A bind request can narrow those grants, but cannot enlarge them. The caller's supplied principal is assumed to come from a trusted host context; a string is not authentication, and code in the same interpreter can call host-administration methods.

Capabilities are plain Python functions without closures; immutable scalar/tuple defaults are supported. Their loaded code/default identity and declared dependency metadata are hashed at registration and binding. A provided `expected_artifact_digest` is compared with that identity. Contract identity is supplied or derived from declared version, obligations, properties, effects, and scope. Those declarations are evidence identifiers, not proof that the function actually meets the contract; the workload conformance suite must establish the tested behavior.

Optional preconditions obey the same plain-function/default restrictions. Their loaded code/default identity is included in the artifact digest and pinned for per-call mutation checks. Their transitive helpers and data still require the declared dependency bundle.

## Compatibility decisions

- Missing capabilities, obligations without declared evidence, and unspecified required properties raise `ReuseUnknown`.
- A known property/contract/artifact mismatch raises `IncompatibleCapability`.
- Authority beyond host grants, missing required scope/effects, and binding a revoked capability raise `PermissionDenied`.
- A call precondition may return `True`, `False`, or `None`; false raises incompatibility and unknown raises `ReuseUnknown` before executing the function.

## Reuse and invalidation

Every invocation checks expiry, per-capability entry identity, the relevant principal's policy revision, environment revision, revocation, and the loaded function code/default identity. It does not reread or rehash a source file on each call. Twenty calls may therefore reuse one full validation. An unrelated capability registration does not invalidate the current binding.

Repeated bindings can memoize the declared compatibility verdict for the exact artifact/contract/revision, requirement, requested authority, host grant, and environment tuple. Loaded-code identity, current grants, revocation, and requested expected digests are still checked at bind time. `full_validations` and `validation_cache_hits` expose that limited metadata work, not model inference or proof construction. The memoization set is bounded and may be discarded without changing semantics.

`register` replaces one capability and invalidates its existing bindings. `update_dependencies(id, mapping)` changes only that capability's dependency identity. `set_environment(mapping)` invalidates bindings when the declared environment changes. `authorize` invalidates that principal's bindings when grants change. `revoke` prevents both existing calls and new binding; `unrevoke` permits revalidation but leaves prior aliases stale. An expired/stale alias raises `StaleBinding`.

The export record contains identity and compatibility requirements, not code, keys, permissions, or a serialized executable. `restore(record, principal=..., scopes=..., allowed_effects=..., requirements=current_requirements, obligations=current_obligations)` revalidates against the receiving runtime's current capabilities, environment, host grants, and trusted receiving-task constraints, with a fresh locally chosen TTL. Requirements from the record are untrusted descriptive hints: they are combined with the caller's trusted current requirements, conflicting values are rejected, and obligations are unioned. A record weakened by removing its original constraints cannot remove constraints supplied by the receiving task. Tampering with the record cannot enlarge host grants. Omitting the optional receiving-task fields retains backward-compatible record-only checking and does not establish compatibility with an unspecified new task. This is a deterministic state-transfer demonstration, not evidence of independently authored agents understanding the record.

## Important bounds

The runtime checks registered function code/defaults and explicitly declared dependency versions. It does not automatically discover all mutable globals, imported helpers, extension modules, transitive data, or external service changes. Those must be represented by a trusted artifact/dependency bundle and updates signaled by the host. In-process code can alter private runtime state or administrative methods, and declared effects are not OS-enforced. Cross-process isolation, authenticated workload identity, signed evidence, complete loaded-dependency assurance, concurrent-update atomicity, and host-wide revocation propagation require a separate implementation and tests.

The benchmark must compare direct and AICC calls using the same underlying kernels and equivalent execution authority. Ordinary algorithm optimization or host policy enforcement must not be attributed uniquely to the registry.
