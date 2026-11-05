"""Same-session tests of the trusted-host binding prototype, not a security audit."""
from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aicc_processing.runtime import (
    Runtime, CapabilityError, PermissionDenied, StaleBinding,
    IncompatibleCapability, ReuseUnknown,
)


def add(left, right):
    return left + right


def multiply(left, right):
    return left * right


def shifted(value, offset=1):
    return value + offset


def positive_inputs(left, right):
    return left >= 0 and right >= 0


def negative_inputs(left, right):
    return left < 0 and right < 0


class RuntimeBindingTests(unittest.TestCase):
    def setUp(self):
        self.now = [100.0]
        self.runtime = Runtime(environment={"unicode": "test-v1", "runtime": "python-test"},
                               clock=lambda: self.now[0])
        self.capability = self.runtime.register("math.add@1", add, contract_version="1",
                                               obligations=("exact-add",),
                                               properties={"operation": "addition"},
                                               dependencies={"arithmetic": "v1"})

    def bind(self, **kwargs):
        return self.runtime.bind("math.add@1", **kwargs)

    def test_alias_reuse_and_json_record(self):
        binding = self.bind(requirements={"operation": "addition"}, obligations=("exact-add",))
        self.assertEqual([binding(i, 2) for i in range(20)], list(range(2, 22)))
        record = json.loads(json.dumps(binding.export_record()))
        self.assertIsInstance(record, dict)
        self.assertNotIn("function", record)

    def test_unknown_and_incompatible_requirements_are_distinct(self):
        with self.assertRaises(ReuseUnknown):
            self.bind(requirements={"unknown_property": "requested"})
        with self.assertRaises(IncompatibleCapability):
            self.bind(requirements={"operation": "multiplication"})

    def test_cached_validation_cannot_weaken_different_requirements(self):
        self.bind(requirements={"operation": "addition"}, obligations=("exact-add",))
        self.bind(requirements={"operation": "addition"}, obligations=("exact-add",))
        self.assertEqual(self.runtime.full_validations, 1)
        self.assertEqual(self.runtime.validation_cache_hits, 1)
        with self.assertRaises(ReuseUnknown):
            self.bind(obligations=("unproven-obligation",))
        with self.assertRaises(IncompatibleCapability):
            self.bind(requirements={"operation": "multiplication"})

    def test_unrelated_registration_does_not_invalidate(self):
        binding = self.bind()
        self.runtime.register("math.multiply@1", multiply)
        self.assertEqual(binding(3, 4), 7)
        self.runtime.revoke("math.multiply@1")
        self.assertEqual(binding(3, 4), 7)

    def test_replacing_capability_invalidates_existing_alias(self):
        binding = self.bind()
        self.runtime.register("math.add@1", multiply, contract_version="2")
        with self.assertRaises(StaleBinding):
            binding(3, 4)

    def test_contract_update_invalidates_existing_alias(self):
        binding = self.bind()
        self.runtime.register("math.add@1", add, contract_version="2")
        with self.assertRaises(StaleBinding):
            binding(3, 4)

    def test_dependency_change_invalidates_existing_alias(self):
        binding = self.bind()
        self.runtime.update_dependencies("math.add@1", {"arithmetic": "v2"})
        with self.assertRaises(StaleBinding):
            binding(3, 4)

    def test_environment_change_invalidates_existing_alias(self):
        binding = self.bind()
        self.runtime.set_environment({"unicode": "test-v2", "runtime": "python-test"})
        with self.assertRaises(StaleBinding):
            binding(3, 4)

    def test_identical_environment_or_grant_update_does_not_invalidate(self):
        binding = self.bind()
        self.runtime.set_environment({"runtime": "python-test", "unicode": "test-v1"})
        self.runtime.authorize("anonymous", scopes=(), allowed_effects=())
        self.assertEqual(binding(3, 4), 7)

    def test_expiry_boundary_is_rejected(self):
        binding = self.bind(ttl_seconds=2.0)
        self.now[0] = 101.999
        self.assertEqual(binding(1, 2), 3)
        self.now[0] = 102.0
        with self.assertRaises(StaleBinding):
            binding(1, 2)

    def test_invalid_ttl_is_rejected(self):
        for ttl in [0, -1, True, False, float("nan"), float("inf"), "1", None]:
            with self.subTest(ttl=ttl):
                with self.assertRaises(ValueError):
                    self.bind(ttl_seconds=ttl)

    def test_revocation_and_fresh_rebinding(self):
        binding = self.bind()
        self.runtime.revoke("math.add@1")
        with self.assertRaises(CapabilityError):
            binding(1, 2)
        with self.assertRaises(CapabilityError):
            self.bind()
        self.runtime.unrevoke("math.add@1")
        self.assertEqual(self.bind()(1, 2), 3)

    def test_policy_change_invalidates_only_that_principal(self):
        self.runtime.authorize("alice", scopes=(), allowed_effects=())
        self.runtime.authorize("bob", scopes=(), allowed_effects=())
        alice = self.bind(principal="alice")
        bob = self.bind(principal="bob")
        self.runtime.authorize("alice", scopes=("project-a",), allowed_effects=())
        with self.assertRaises(StaleBinding):
            alice(1, 2)
        self.assertEqual(bob(1, 2), 3)

    def test_scope_claim_does_not_create_host_authority(self):
        self.runtime.register("private.add@1", add, scope="project-a")
        with self.assertRaises(PermissionDenied):
            self.runtime.bind("private.add@1", principal="mallory", scopes=("project-a",))
        self.runtime.authorize("alice", scopes=("project-a",), allowed_effects=())
        bound = self.runtime.bind("private.add@1", principal="alice", scopes=("project-a",))
        self.assertEqual(bound(2, 3), 5)

    def test_effect_claim_does_not_create_host_authority(self):
        self.runtime.register("write.add@1", add, effects=("filesystem.write",))
        with self.assertRaises(PermissionDenied):
            self.runtime.bind("write.add@1", allowed_effects=("filesystem.write",))
        self.runtime.authorize("alice", scopes=(), allowed_effects=("filesystem.write",))
        binding = self.runtime.bind("write.add@1", principal="alice", allowed_effects=("filesystem.write",))
        self.assertEqual(binding(2, 3), 5)

    def test_artifact_and_contract_pins_refuse_mismatch(self):
        with self.assertRaises(CapabilityError):
            self.bind(expected_artifact_digest="0" * 64)
        with self.assertRaises(CapabilityError):
            self.bind(expected_contract_digest="0" * 64)

    def test_loaded_function_code_replacement_is_rejected(self):
        binding = self.bind()
        original = add.__code__
        try:
            add.__code__ = multiply.__code__
            with self.assertRaises(StaleBinding):
                binding(3, 4)
        finally:
            add.__code__ = original

    def test_loaded_function_default_replacement_is_rejected(self):
        self.runtime.register("shift@1", shifted)
        binding = self.runtime.bind("shift@1")
        self.assertEqual(binding(3), 4)
        original = shifted.__defaults__
        try:
            shifted.__defaults__ = (10,)
            with self.assertRaises(StaleBinding):
                binding(3)
        finally:
            shifted.__defaults__ = original

    def test_handoff_revalidates_against_receiving_runtime(self):
        binding = self.bind(requirements={"operation": "addition"})
        record = json.loads(json.dumps(binding.export_record()))
        receiving = Runtime(environment={"unicode": "test-v1", "runtime": "python-test"},
                            clock=lambda: self.now[0])
        receiving.register("math.add@1", add, contract_version="1", obligations=("exact-add",),
                           properties={"operation": "addition"}, dependencies={"arithmetic": "v1"})
        restored = receiving.restore(record, principal="anonymous")
        self.assertEqual(restored(3, 4), 7)
        receiving.update_dependencies("math.add@1", {"arithmetic": "v2"})
        with self.assertRaises(CapabilityError):
            receiving.restore(record, principal="anonymous")

    def test_private_record_does_not_transfer_authority(self):
        self.runtime.register("private.add@1", add, scope="project-a")
        self.runtime.authorize("alice", scopes=("project-a",), allowed_effects=())
        record = self.runtime.bind("private.add@1", principal="alice", scopes=("project-a",)).export_record()
        receiving = Runtime(environment={"unicode": "test-v1", "runtime": "python-test"})
        receiving.register("private.add@1", add, scope="project-a")
        with self.assertRaises(PermissionDenied):
            receiving.restore(record, principal="mallory", scopes=("project-a",))

    def test_handoff_rejects_tampered_identity_and_policy_metadata(self):
        record = self.bind().export_record()
        for field, value in [("artifact_digest", "0" * 64), ("contract_digest", "0" * 64),
                             ("environment_digest", "0" * 64), ("required_scope", "another-project"),
                             ("required_effects", ["filesystem.write"]), ("record_version", 999)]:
            changed = dict(record, **{field: value})
            with self.subTest(field=field):
                with self.assertRaises(CapabilityError):
                    self.runtime.restore(changed, principal="anonymous")

    def test_external_metadata_mutation_does_not_change_record(self):
        properties = {"operation": "addition"}
        dependencies = {"arithmetic": "v1"}
        self.runtime.register("snapshot@1", add, properties=properties, dependencies=dependencies)
        properties["operation"] = "multiplication"
        dependencies["arithmetic"] = "v2"
        self.assertEqual(self.runtime.bind("snapshot@1", requirements={"operation": "addition"})(3, 4), 7)

    def test_receiving_task_pins_survive_weakened_handoff_record(self):
        record = self.bind().export_record()
        record['requirements'] = {}
        record['obligations'] = []
        with self.assertRaises(IncompatibleCapability):
            self.runtime.restore(record, principal='anonymous', requirements={'operation': 'multiplication'})
        with self.assertRaises(ReuseUnknown):
            self.runtime.restore(record, principal='anonymous', obligations=('not-proven',))
        restored = self.runtime.restore(record, principal='anonymous', requirements={'operation': 'addition'}, obligations=('exact-add',))
        self.assertEqual(restored(2, 3), 5)

    def test_call_precondition_enforced_and_identity_pinned(self):
        original = positive_inputs.__code__
        self.runtime.register('guarded@1', add, precondition=positive_inputs)
        binding = self.runtime.bind('guarded@1')
        self.assertEqual(binding(2, 3), 5)
        with self.assertRaises(IncompatibleCapability): binding(-1, 3)
        try:
            positive_inputs.__code__ = negative_inputs.__code__
            with self.assertRaises(StaleBinding): binding(2, 3)
        finally:
            positive_inputs.__code__ = original


if __name__ == "__main__":
    unittest.main()
