"""Same-session adversarial regression tests, not blind independent authoring trials.

Hand-written expected cases are combined with seeded differential/property checks.
The optimized variants must preserve the frozen observable event contract.
"""
from copy import deepcopy
from pathlib import Path
import random
import sys
import unittest
from types import MappingProxyType

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from aicc_processing import kernels


def event(event_id, timestamp, severity=1, device="pump", kind="alert", message="high pressure"):
    return dict(event_id=event_id, timestamp=timestamp, severity=severity,
                device=device, kind=kind, message=message)


def group(device, kind, message, first, last, count, severity_sum, first_ordinal):
    return dict(device=device, kind=kind, message=message, first=first, last=last,
                count=count, severity_sum=severity_sum, first_ordinal=first_ordinal)


class KernelContractTests(unittest.TestCase):
    def equivalent_variants(self, rows, window=10, minimum=0, expected=None):
        reference = kernels.process_reference(deepcopy(rows), window, minimum)
        if expected is not None:
            self.assertEqual(reference, expected)
        variants = [kernels.process_cached, kernels.process_partitioned]
        if all(rows[i - 1]["timestamp"] <= rows[i]["timestamp"] for i in range(1, len(rows))):
            variants.append(kernels.process_ordered)
        for fn in variants:
            with self.subTest(variant=fn.__name__):
                self.assertEqual(fn(deepcopy(rows), window, minimum), reference)
        return reference

    def test_empty_and_singleton(self):
        self.equivalent_variants([], expected=[])
        self.equivalent_variants([event("a", -3, 2)], expected=[
            group("pump", "alert", "high pressure", -3, -3, 1, 2, 0)])

    def test_first_input_duplicate_wins_before_filter_and_sort(self):
        rows = [event("repeat", 20, 0), event("b", 4, 2),
                event("repeat", 0, 3), event("c", 3, 1)]
        self.equivalent_variants(rows, window=10, minimum=1, expected=[
            group("pump", "alert", "high pressure", 3, 4, 2, 3, 3)])

    def test_anchored_window_uses_strict_boundary(self):
        # Sliding a window from the previous event would incorrectly merge t=18.
        rows = [event("a", 0, 1), event("b", 9, 2), event("c", 18, 3), event("d", 28, 0)]
        self.equivalent_variants(rows, window=10, expected=[
            group("pump", "alert", "high pressure", 0, 9, 2, 3, 0),
            group("pump", "alert", "high pressure", 18, 18, 1, 3, 2),
            group("pump", "alert", "high pressure", 28, 28, 1, 0, 3)])

    def test_creation_order_is_timestamp_then_original_ordinal(self):
        rows = [event("a", 10, device="z"), event("b", 0, device="y"),
                event("c", 0, device="x"), event("d", 10, device="y")]
        self.equivalent_variants(rows, window=5, expected=[
            group("y", "alert", "high pressure", 0, 0, 1, 1, 1),
            group("x", "alert", "high pressure", 0, 0, 1, 1, 2),
            group("z", "alert", "high pressure", 10, 10, 1, 1, 0),
            group("y", "alert", "high pressure", 10, 10, 1, 1, 3)])

    def test_unicode_normalization_and_message_case_are_distinct(self):
        rows = [event("a", 0, device=" Straße ", kind="\ufb01", message=" high\u00a0 pressure "),
                event("b", 1, device="STRASSE", kind="fi", message="high pressure"),
                event("c", 2, device="strasse", kind="fi", message="High pressure"),
                event("d", 3, device="strasse", kind="fi", message="high\x1cpressure"),
                event("e", 4, device="strasse", kind="fi", message="high\ufeffpressure")]
        self.equivalent_variants(rows, window=10, expected=[
            group("strasse", "fi", "high pressure", 0, 3, 3, 3, 0),
            group("strasse", "fi", "High pressure", 2, 2, 1, 1, 2),
            group("strasse", "fi", "high\ufeffpressure", 4, 4, 1, 1, 4)])

    def test_message_is_not_nfkc_normalized(self):
        rows = [event("a", 0, message="\ufb01"), event("b", 1, message="fi")]
        self.equivalent_variants(rows, expected=[
            group("pump", "alert", "\ufb01", 0, 0, 1, 1, 0),
            group("pump", "alert", "fi", 1, 1, 1, 1, 1)])

    def test_minimum_severity_and_duplicate_id_case_sensitivity(self):
        rows = [event("A", 0, 1), event("a", 1, 2), event("b", 2, 3)]
        self.equivalent_variants(rows, minimum=2, expected=[
            group("pump", "alert", "high pressure", 1, 2, 2, 5, 1)])

    def test_event_id_whitespace_is_not_normalized(self):
        rows = [event("a", 0), event(" a ", 1)]
        self.equivalent_variants(rows, expected=[
            group("pump", "alert", "high pressure", 0, 1, 2, 2, 0)])

    def test_large_integer_timestamps_do_not_lose_precision(self):
        start = 2 ** 60
        rows = [event("a", start), event("b", start + 1), event("c", start + 2)]
        self.equivalent_variants(rows, window=2, expected=[
            group("pump", "alert", "high pressure", start, start + 1, 2, 2, 0),
            group("pump", "alert", "high pressure", start + 2, start + 2, 1, 1, 2)])

    def test_rows_are_not_mutated_and_mapping_objects_are_accepted(self):
        rows = [event("a", 0), event("b", 2)]
        original = deepcopy(rows)
        for fn in kernels.VARIANTS.values():
            fn([MappingProxyType(x) for x in rows], 10, 0)
            self.assertEqual(rows, original)

    def test_one_pass_generators(self):
        class OnePass:
            def __init__(self):
                self.used = False
            def __iter__(self):
                if self.used:
                    raise AssertionError("input iterable was consumed twice")
                self.used = True
                yield event("a", 0)
                yield event("b", 2)
        expected = [group("pump", "alert", "high pressure", 0, 2, 2, 2, 0)]
        for fn in kernels.VARIANTS.values():
            with self.subTest(variant=fn.__name__):
                self.assertEqual(fn(OnePass(), 10), expected)

    def test_invalid_rows_are_checked_even_if_duplicate_or_filtered(self):
        cases = []
        for field, value in [("timestamp", True), ("timestamp", 0.0), ("severity", False),
                             ("event_id", 3), ("device", None), ("kind", []), ("message", b"x")]:
            invalid = event("same", 1, 0)
            invalid[field] = value
            cases.append((invalid, TypeError))
        invalid = event("same", 1, 4)
        cases.append((invalid, ValueError))
        invalid = event("same", 1, 0)
        del invalid["kind"]
        cases.append((invalid, TypeError))
        for fn in kernels.VARIANTS.values():
            for invalid, error in cases:
                with self.subTest(variant=fn.__name__, invalid=invalid):
                    with self.assertRaises(error):
                        fn([event("same", 0, 0), invalid], 10, 3)

    def test_invalid_container_and_parameters(self):
        for fn in kernels.VARIANTS.values():
            for rows in [None, [None], ["event"], [3]]:
                with self.subTest(variant=fn.__name__, rows=rows):
                    with self.assertRaises(TypeError):
                        fn(rows, 10)
            for window in [0, -1, True, False, 1.5, "10", None]:
                with self.subTest(variant=fn.__name__, window=window):
                    with self.assertRaises(ValueError):
                        fn([], window)
            for minimum in [-1, 4, True, False, 1.5, "1", None]:
                with self.subTest(variant=fn.__name__, minimum=minimum):
                    with self.assertRaises(ValueError):
                        fn([], 10, minimum)

    def test_ordered_checks_discarded_rows_too(self):
        # The second raw row is a filtered duplicate but still violates order.
        with self.assertRaises(kernels.OrderPreconditionError):
            kernels.process_ordered([event("same", 10, 0), event("same", 0, 0)], 5, 3)
        with self.assertRaises(kernels.OrderPreconditionError):
            kernels.process_ordered([event("a", 1), event("b", 0)], 5)

    def test_dispatch_and_unknown_variant(self):
        rows = [event("a", 0)]
        for name in kernels.VARIANTS:
            self.assertEqual(kernels.process(rows, 5, variant=name), kernels.process_reference(rows, 5))
        with self.assertRaises((ValueError, KeyError)):
            kernels.process(rows, 5, variant="missing")

    def test_seeded_differential_populations(self):
        rng = random.Random(871942)
        devices = ["p", " P ", "Straße", "STRASSE", "p\x1cq", "p q", "p\ufeffq", "\ufb01"]
        kinds = ["alert", " ALERT ", "\u03a3\u0391\u03a3", "\u03c3\u03b1\u03c3"]
        messages = ["m", " M ", "a  b", "a\u2028b", "a\ufeffb", "\ufb01", "fi"]
        for case in range(150):
            count = rng.randint(0, 90)
            rows = [event(str(rng.randrange(max(1, count // 2))), rng.randint(-20, 100),
                          rng.randrange(4), rng.choice(devices), rng.choice(kinds), rng.choice(messages))
                    for _ in range(count)]
            window, minimum = rng.choice([1, 2, 10, 31, 500]), rng.randrange(4)
            with self.subTest(case=case, order="shuffled"):
                result = self.equivalent_variants(rows, window, minimum)
                self.assertEqual([(g["first"], g["first_ordinal"]) for g in result],
                                 sorted((g["first"], g["first_ordinal"]) for g in result))
                self.assertTrue(all(g["last"] - g["first"] < window for g in result))
            ordered = sorted(rows, key=lambda row: row["timestamp"])
            with self.subTest(case=case, order="sorted"):
                self.equivalent_variants(ordered, window, minimum)


if __name__ == "__main__":
    unittest.main()
