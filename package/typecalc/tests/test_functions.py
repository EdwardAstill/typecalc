"""Scalar mathematical functions through the public equation solver."""

import math
import unittest
from unittest.mock import patch

from sympy import Rational

from typecalc import solve
from typecalc.text import parse_document, solve_document


class ScalarFunctionTests(unittest.TestCase):
    def test_numeric_functions_and_case_insensitive_names(self):
        for expression, expected in (
            ("SIN(0.5)", math.sin(0.5)),
            ("COS(0.5)", math.cos(0.5)),
            ("TAN(0.5)", math.tan(0.5)),
            ("LN(2)", math.log(2)),
            ("LOG(8, 2)", 3),
            ("LOG(100, 10)", 2),
            ("LOG(4, 0.5)", -2),
            ("EXP(1)", math.e),
        ):
            for source in (expression, expression.lower()):
                with self.subTest(expression=source):
                    self.assertAlmostEqual(solve([f"A = {source}"])["A"], expected)

    def test_arguments_can_use_variables_solved_by_other_equations(self):
        values = solve([
            "S = SIN(X)",
            "C = COS(X)",
            "T = TAN(X)",
            "L = LN(Y)",
            "B = LOG(Y, Base)",
            "E = EXP(X)",
            "X = 0.5",
            "Y = 8",
            "Base = 2",
        ])

        for name, expected in (
            ("S", math.sin(0.5)),
            ("C", math.cos(0.5)),
            ("T", math.tan(0.5)),
            ("L", math.log(8)),
            ("B", 3),
            ("E", math.exp(0.5)),
        ):
            with self.subTest(variable=name):
                self.assertAlmostEqual(values[name], expected)

    def test_functions_remain_symbolic_for_differentiation(self):
        for expression, expected in (
            ("DIFF(SIN(X) | X=0)", 1),
            ("DIFF(COS(X) | X=0)", 0),
            ("DIFF(TAN(X) | X=0)", 1),
            ("DIFF(LN(X) | X=2)", 0.5),
            ("DIFF(LOG(X, 2) | X=2)", 1 / (2 * math.log(2))),
            ("DIFF(EXP(X) | X=0)", 1),
        ):
            with self.subTest(expression=expression):
                self.assertAlmostEqual(solve([f"A = {expression}"])["A"], expected)

    def test_nested_logarithms_and_exponentials(self):
        self.assertEqual(solve(["A = LN(EXP(3))", "B = EXP(LN(2))"]), {"A": 3, "B": 2})

    def test_invalid_argument_counts_report_the_function(self):
        for name in ("SIN", "COS", "TAN", "LN", "EXP"):
            for arguments in ("", "1, 2"):
                with self.subTest(function=name, arguments=arguments):
                    with self.assertRaisesRegex(ValueError, f"{name} requires"):
                        solve([f"A = {name}({arguments})"])
        for arguments in ("", "10", "10, 2, 3"):
            with self.subTest(function="LOG", arguments=arguments):
                with self.assertRaisesRegex(ValueError, "LOG requires"):
                    solve([f"A = LOG({arguments})"])

    def test_logarithms_reject_invalid_numeric_values_and_bases(self):
        for expression in (
            "LN(0)", "LN(-1)", "LOG(0, 10)", "LOG(-1, 10)",
            "LOG(2, 0)", "LOG(2, -1)", "LOG(2, 1)", "LOG(1, 1)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, "positive"):
                    solve([f"A = {expression}"])


class IntegrateTests(unittest.TestCase):
    def test_definite_integral_does_not_require_a_global_variable(self):
        self.assertEqual(solve(["A = INTEGRATE(X^2, X, 0, 3)"]), {"A": 9})

    def test_lowercase_integrate_and_reversed_or_equal_bounds(self):
        self.assertEqual(
            solve(["A = integrate(X^2, X, 3, 0)", "B = INTEGRATE(X^2, X, 2, 2)"]),
            {"A": -9, "B": 0},
        )

    def test_integration_variable_does_not_use_or_assign_its_global_value(self):
        self.assertEqual(
            solve(["X = 10", "A = INTEGRATE(X^2, X, 0, 3)"]),
            {"X": 10, "A": 9},
        )

    def test_coefficients_and_bound_expressions_use_solved_values(self):
        self.assertEqual(
            solve(["A = INTEGRATE(C*X, X, L, U + 1)", "C = 2", "L = 1", "U = 2"]),
            {"A": 8, "C": 2, "L": 1, "U": 2},
        )

    def test_bound_can_use_a_global_variable_with_the_integration_variable_name(self):
        self.assertEqual(solve(["A = INTEGRATE(X, X, 0, X)", "X = 2"]), {"A": 2, "X": 2})

    def test_document_integrals_preserve_exact_fractions(self):
        document = parse_document("EQUATIONS\nA = INTEGRATE(X^2, X, 0, 1)")

        self.assertEqual(solve_document(document), {"A": Rational(1, 3)})

    def test_integrates_nested_functions_and_derivatives(self):
        for expression, expected in (
            ("INTEGRATE(SIN(X), X, 0, 1)", 1 - math.cos(1)),
            ("INTEGRATE(EXP(X), X, 0, 1)", math.e - 1),
            ("INTEGRATE(DIFF(X^3, X), X, 0, 2)", 8),
            ("DIFF(INTEGRATE(T^2, T, 0, X) | X=2)", 4),
        ):
            with self.subTest(expression=expression):
                self.assertAlmostEqual(solve([f"A = {expression}"])["A"], expected)

    def test_free_coefficients_still_need_values(self):
        with self.assertRaisesRegex(ValueError, "not fully determined"):
            solve(["A = INTEGRATE(C*X, X, 0, 1)"])

    def test_invalid_arguments_report_clear_errors(self):
        for arguments in ("", "X", "X, X", "X, X, 0", "X, X, 0, 1, 2"):
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, "INTEGRATE requires"):
                    solve([f"A = INTEGRATE({arguments})"])
        for variable in ("2", "X + Y"):
            with self.subTest(variable=variable):
                with self.assertRaisesRegex(ValueError, "INTEGRATE variable must be a symbol"):
                    solve([f"A = INTEGRATE(X, {variable}, 0, 1)"])


class RandTests(unittest.TestCase):
    def test_one_sample_is_shared_when_referencing_the_same_variable(self):
        with patch("typecalc.functions.rand.random.random", return_value=0.25) as sample:
            values = solve(["A = 10*R", "B = 20*R", "R = RAND()"])

        self.assertEqual(values, {"A": 2.5, "B": 5, "R": 0.25})
        sample.assert_called_once_with()

    def test_each_occurrence_is_sampled_independently(self):
        with patch("typecalc.functions.rand.random.random", side_effect=[0.25, 0.75]) as sample:
            values = solve(["A = RAND() + RAND()"])

        self.assertEqual(values, {"A": 1})
        self.assertEqual(sample.call_count, 2)

    def test_resolving_the_same_document_samples_again_without_changing_it(self):
        document = parse_document("EQUATIONS\nA = rand()")
        with patch("typecalc.functions.rand.random.random", side_effect=[0.25, 0.75]):
            self.assertEqual(solve_document(document), {"A": Rational(1, 4)})
            self.assertEqual(solve_document(document), {"A": Rational(3, 4)})

        self.assertEqual(document, parse_document("EQUATIONS\nA = rand()"))

    def test_samples_remain_in_range_and_are_not_rounded_by_symbolic_solving(self):
        for number in (0.0, 2**-53, math.nextafter(1.0, 0.0)):
            with self.subTest(number=number):
                with patch("typecalc.functions.rand.random.random", return_value=number):
                    self.assertEqual(solve(["A = RAND()"]), {"A": number})

    def test_arguments_are_rejected(self):
        for arguments in ("1", "1, 2"):
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, "RAND requires no arguments"):
                    solve([f"A = RAND({arguments})"])


if __name__ == "__main__":
    unittest.main()
