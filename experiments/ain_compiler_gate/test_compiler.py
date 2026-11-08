"""Regression checks for validated native compilation and its bounded domain."""
import gc
import unittest

from experiments.ain_compiler_gate.compiler import compile_program, parse_program
from experiments.ain_v0.ain.language import run_ir


class CompilerTests(unittest.TestCase):
    def test_all_frontends_compile_to_equivalent_native_code(self):
        programs = {"python": "x+7-4", "ir": "add 7;sub 4", "ain": "2 7;3 4"}
        assemblies = []
        for arm, text in programs.items():
            document = parse_program(arm, text)
            native = compile_program(arm, text)
            assemblies.append(native.assembly)
            self.assertIn("solve", native.assembly)
            self.assertIn("define i64 @solve", native.llvm_ir)
            self.assertGreater(native.compile_seconds, 0)
            for value in (-1_000_000, -17, 0, 31, 1_000_000):
                with self.subTest(arm=arm, value=value):
                    self.assertEqual(native.run(value), value + 3)
                    self.assertEqual(native.run(value), run_ir(document, {}, [value]))
        self.assertEqual(assemblies[0], assemblies[1])
        self.assertEqual(assemblies[1], assemblies[2])

    def test_signed_zero_literals_and_prior_python_function(self):
        programs = {"python": "def solve(x):\n    return ((x + -7) - 0)",
                    "ir": "add -7;sub 0", "ain": "2 -7;3 0"}
        for arm, text in programs.items():
            native = compile_program(arm, text)
            self.assertEqual(native.run(-1_000_000), -1_000_007)
            self.assertEqual(native.run(1_000_000), 999_993)
        self.assertEqual(compile_program("ain", "2 +7").run(0), 7)
        self.assertEqual(compile_program("python", "x").run(123), 123)

    def test_malformed_instructions_and_unsafe_python_are_rejected(self):
        for arm, text in (("ain", "4 7"), ("ain", "2 7;"), ("ain", "2 7 8"),
                          ("ir", "ADD 7"), ("ir", "add 2.0"), ("ain", "2 True"),
                          ("python", "__import__('os').system('dir')"),
                          ("python", "x*x"), ("python", "x+x"),
                          ("python", "x+True"), ("python", "lambda x: x+1"),
                          ("python", "def solve(x):\n    import os\n    return x"),
                          ("ain", ""), ("unknown", "2 1")):
            with self.subTest(arm=arm, text=text), self.assertRaises((ValueError, SyntaxError)):
                compile_program(arm, text)

    def test_exact_domain_limits_prevent_native_overflow(self):
        for arm, text in (("ain", "2 1000001"), ("ir", "sub -1000001"),
                          ("python", "x+1000001"), ("ain", ";".join(["2 1"] * 17))):
            with self.subTest(arm=arm), self.assertRaises(ValueError):
                compile_program(arm, text)
        native = compile_program("ain", ";".join(["2 1000000"] * 16))
        self.assertEqual(native.run(1_000_000), 17_000_000)
        signed_python = "x" + "+(-1000000)" * 16
        self.assertEqual(compile_program("python", signed_python).run(1_000_000), -15_000_000)
        self.assertEqual(compile_program("ir", ";".join(["add -1000000"] * 16)).run(1_000_000),
                         -15_000_000)
        for value in (1_000_001, -1_000_001, True, 1.0, 2**64):
            with self.subTest(value=value), self.assertRaises(ValueError):
                native.run(value)

    def test_function_remains_valid_when_other_engines_are_collected(self):
        first = compile_program("ain", "3 9")
        second = compile_program("ain", "2 12")
        del second
        gc.collect()
        self.assertEqual(first.run(30), 21)


if __name__ == "__main__":
    unittest.main()
