"""Public string-equation solving and JSON numeric boundaries."""

import json
import unittest

from typecalc import solve


class SolveTests(unittest.TestCase):
    def test_parse_errors_name_the_offending_line(self):
        with self.assertRaisesRegex(ValueError, "Line 3"):
            solve(["A = 1", "", "B $ C"])

    def test_returns_a_value_for_every_variable(self):
        self.assertEqual(solve(["A + B = 10", "", "  ", "A = 6"]), {"A": 6.0, "B": 4.0})

    def test_returns_strict_json_numbers(self):
        values = solve(["A = 1/3"])

        self.assertEqual(json.loads(json.dumps(values, allow_nan=False)), {"A": 1 / 3})

    def test_reports_unresolved_variables(self):
        with self.assertRaisesRegex(ValueError, "not fully determined"):
            solve(["A + B = 10"])

    def test_rejects_values_outside_finite_real_floats(self):
        for equation in ("A = 10^400", "A = (-1)^(1/2)"):
            with self.subTest(equation=equation):
                with self.assertRaises(ValueError):
                    solve([equation])

    def test_rejects_a_single_string_instead_of_equation_rows(self):
        with self.assertRaises(TypeError):
            solve("A = 6")

    def test_rejects_a_non_string_row(self):
        with self.assertRaises(TypeError):
            solve(["A = 6", 4])


if __name__ == "__main__":
    unittest.main()
