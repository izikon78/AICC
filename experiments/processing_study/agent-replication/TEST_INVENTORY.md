# Frozen automated-test inventory

Generated from the Python test definitions at measured implementation commit `75de32b757b8bdc43886213ee6b9dd9470717918`. This inventory is not a new execution record. The original run passed 44 unittest methods; individual methods contain additional subcases.

Run `python -m unittest discover -s tests -v` from the study directory to obtain the actual result on your own environment. Preserve stdout/stderr and exit status. The nine binding scenarios and 8,096 granularity inputs are separate checks and must not be added to the unittest-method total.

## test_kernels.py: 16 methods

Source: [test implementation](../tests/test_kernels.py).

- `KernelContractTests.test_empty_and_singleton`
- `KernelContractTests.test_first_input_duplicate_wins_before_filter_and_sort`
- `KernelContractTests.test_anchored_window_uses_strict_boundary`
- `KernelContractTests.test_creation_order_is_timestamp_then_original_ordinal`
- `KernelContractTests.test_unicode_normalization_and_message_case_are_distinct`
- `KernelContractTests.test_message_is_not_nfkc_normalized`
- `KernelContractTests.test_minimum_severity_and_duplicate_id_case_sensitivity`
- `KernelContractTests.test_event_id_whitespace_is_not_normalized`
- `KernelContractTests.test_large_integer_timestamps_do_not_lose_precision`
- `KernelContractTests.test_rows_are_not_mutated_and_mapping_objects_are_accepted`
- `KernelContractTests.test_one_pass_generators`
- `KernelContractTests.test_invalid_rows_are_checked_even_if_duplicate_or_filtered`
- `KernelContractTests.test_invalid_container_and_parameters`
- `KernelContractTests.test_ordered_checks_discarded_rows_too`
- `KernelContractTests.test_dispatch_and_unknown_variant`
- `KernelContractTests.test_seeded_differential_populations`

## test_learning.py: 4 methods

Source: [test implementation](../tests/test_learning.py).

- `LearningTests.test_numeric_gradients_and_mask`
- `LearningTests.test_training_and_serialization`
- `LearningTests.test_invalid_measurements_are_not_imputed`
- `LearningTests.test_static_is_best_of_four_policies`

## test_runtime.py: 24 methods

Source: [test implementation](../tests/test_runtime.py).

- `RuntimeBindingTests.test_alias_reuse_and_json_record`
- `RuntimeBindingTests.test_unknown_and_incompatible_requirements_are_distinct`
- `RuntimeBindingTests.test_cached_validation_cannot_weaken_different_requirements`
- `RuntimeBindingTests.test_unrelated_registration_does_not_invalidate`
- `RuntimeBindingTests.test_replacing_capability_invalidates_existing_alias`
- `RuntimeBindingTests.test_contract_update_invalidates_existing_alias`
- `RuntimeBindingTests.test_dependency_change_invalidates_existing_alias`
- `RuntimeBindingTests.test_environment_change_invalidates_existing_alias`
- `RuntimeBindingTests.test_identical_environment_or_grant_update_does_not_invalidate`
- `RuntimeBindingTests.test_expiry_boundary_is_rejected`
- `RuntimeBindingTests.test_invalid_ttl_is_rejected`
- `RuntimeBindingTests.test_revocation_and_fresh_rebinding`
- `RuntimeBindingTests.test_policy_change_invalidates_only_that_principal`
- `RuntimeBindingTests.test_scope_claim_does_not_create_host_authority`
- `RuntimeBindingTests.test_effect_claim_does_not_create_host_authority`
- `RuntimeBindingTests.test_artifact_and_contract_pins_refuse_mismatch`
- `RuntimeBindingTests.test_loaded_function_code_replacement_is_rejected`
- `RuntimeBindingTests.test_loaded_function_default_replacement_is_rejected`
- `RuntimeBindingTests.test_handoff_revalidates_against_receiving_runtime`
- `RuntimeBindingTests.test_private_record_does_not_transfer_authority`
- `RuntimeBindingTests.test_handoff_rejects_tampered_identity_and_policy_metadata`
- `RuntimeBindingTests.test_external_metadata_mutation_does_not_change_record`
- `RuntimeBindingTests.test_receiving_task_pins_survive_weakened_handoff_record`
- `RuntimeBindingTests.test_call_precondition_enforced_and_identity_pinned`
