"""Seeded representation checks complement hand-derived semantic traces."""
import random
import unittest

from ain.runner import execute


class GeneratedParity(unittest.TestCase):
    def test_eighty_seeded_streams(self):
        for seed in range(80):
            rng = random.Random(97000 + seed)
            rows = []
            watermark = 0
            for _ in range(80):
                if rng.random() < .17:
                    watermark += rng.randrange(0, 35)
                    row = {"kind": "watermark", "timestamp": watermark}
                else:
                    row = {"kind": "event", "event": {
                        "tenant": rng.choice(["t", "T"]),
                        "event_id": str(rng.randrange(0, 30)),
                        "timestamp": max(0, watermark + rng.randrange(-20, 55)),
                        "severity": rng.randrange(4),
                        "device": rng.choice([" Pump ", "Ｐｕｍｐ", "PUMP", "motor"]),
                        "kind": rng.choice([" Alarm ", "alarm", "ALARM"]),
                        "message": rng.choice(["Review\tthis", "Review this", "review this"]),
                    }}
                row["offset"] = len(rows) + 1
                rows.append(row)
            rows.append({"offset": len(rows) + 1, "kind": "end"})
            with self.subTest(seed=seed):
                outputs = [execute(rows, mode=mode) for mode in ("python", "ir", "ain")]
                self.assertEqual(outputs[0]["status"], "COMPLETE")
                self.assertEqual(outputs[0], outputs[1])
                self.assertEqual(outputs[0], outputs[2])

    def test_malformed_discard_candidates(self):
        # Invalid data must fail even when lateness or duplicate/filter shortcuts
        # could otherwise discard it. Equality here is not an independent oracle.
        malformed = [True, -1, 4, "2", None]
        for severity in malformed:
            rows = [{"offset": 1, "kind": "watermark", "timestamp": 1000},
                    {"offset": 2, "kind": "event", "event": {
                        "tenant": "t", "event_id": "x", "timestamp": 0,
                        "severity": severity, "device": "d", "kind": "k", "message": "m"}}]
            with self.subTest(severity=severity):
                outputs = [execute(rows, mode=mode) for mode in ("python", "ir", "ain")]
                self.assertEqual(outputs[0]["status"], "ERROR")
                self.assertEqual(outputs[0], outputs[1])
                self.assertEqual(outputs[0], outputs[2])


if __name__ == "__main__":
    unittest.main()
