"""Scalar mathematical functions through the public equation solver."""

import math
import unittest
from unittest.mock import patch

from sympy import Rational, pi

from typecalc import solve
from typecalc.parser import parse_equations
from typecalc.solver import _solve_equations


class ScalarFunctionTests(unittest.TestCase):
    def test_numeric_functions_and_case_insensitive_names(self):
        for expression, expected in (
            ("ABS(-5)", 5),
            ("ABS(0)", 0),
            ("ABS(5)", 5),
            ("RAD(180)", math.pi),
            ("DEG(PI()/2)", 90),
            ("ASIN(0.5)", math.asin(0.5)),
            ("ACOS(0.5)", math.acos(0.5)),
            ("ATAN(0.5)", math.atan(0.5)),
            ("ATAN2(1, -1)", 3 * math.pi / 4),
            ("ROUND(PI(), 2)", 3.14),
            ("PI()", math.pi),
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
            ("DIFF(ABS(X) | X=-2)", -1),
            ("DIFF(ABS(X) | X=2)", 1),
            ("DIFF(RAD(X) | X=0)", math.pi / 180),
            ("DIFF(DEG(X) | X=0)", 180 / math.pi),
            ("DIFF(ASIN(X) | X=0)", 1),
            ("DIFF(ACOS(X) | X=0)", -1),
            ("DIFF(ATAN(X) | X=0)", 1),
            ("DIFF(ATAN2(X, 1) | X=0)", 1),
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
        for name in ("ABS", "RAD", "DEG", "ASIN", "ACOS", "ATAN", "SIN", "COS", "TAN", "LN", "EXP"):
            for arguments in ("", "1, 2"):
                with self.subTest(function=name, arguments=arguments):
                    with self.assertRaisesRegex(ValueError, f"{name} requires"):
                        solve([f"A = {name}({arguments})"])
        for name in ("ATAN2", "ROUND", "LOG"):
            for arguments in ("", "10", "10, 2, 3"):
                with self.subTest(function=name, arguments=arguments):
                    with self.assertRaisesRegex(ValueError, f"{name} requires"):
                        solve([f"A = {name}({arguments})"])
        for arguments in ("1", "1, 2"):
            with self.subTest(function="PI", arguments=arguments):
                with self.assertRaisesRegex(ValueError, "PI requires no arguments"):
                    solve([f"A = PI({arguments})"])

    def test_logarithms_reject_invalid_numeric_values_and_bases(self):
        for expression in (
            "LN(0)", "LN(-1)", "LOG(0, 10)", "LOG(-1, 10)",
            "LOG(2, 0)", "LOG(2, -1)", "LOG(2, 1)", "LOG(1, 1)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, "positive"):
                    solve([f"A = {expression}"])


class AbsoluteValueAndAngleTests(unittest.TestCase):
    def test_functions_use_values_solved_from_other_equations(self):
        equations = [
            "Magnitude = ABS(X)",
            "Radians = RAD(Angle)",
            "Degrees = DEG(Radians)",
            "S = ASIN(Ratio)",
            "C = ACOS(Ratio)",
            "T = ATAN(Ratio)",
            "Direction = DEG(ATAN2(Ratio, X))",
            "X + 2 = 0",
            "Angle = 30",
            "Ratio = 0.5",
        ]
        values = solve(equations)

        for name, expected in (
            ("Magnitude", 2),
            ("Radians", math.pi / 6),
            ("Degrees", 30),
            ("S", math.asin(0.5)),
            ("C", math.acos(0.5)),
            ("T", math.atan(0.5)),
            ("Direction", math.degrees(math.atan2(0.5, -2))),
        ):
            with self.subTest(variable=name):
                self.assertAlmostEqual(values[name], expected)
        self.assertEqual(solve(list(reversed(equations))), values)

    def test_pi_and_angle_conversions_preserve_exact_values(self):
        equations = parse_equations([
            "P = PI()", "R = RAD(180)", "D = DEG(PI())",
            "S = SIN(RAD(30))", "C = COS(PI())", "T = TAN(RAD(45))",
        ])

        self.assertEqual(
            _solve_equations(equations),
            {"P": pi, "R": pi, "D": 180, "S": Rational(1, 2), "C": -1, "T": 1},
        )

    def test_pi_function_does_not_reserve_the_variable_name(self):
        values = solve(["PI = 4", "A = PI", "B = PI()"])

        self.assertEqual(values["PI"], 4)
        self.assertEqual(values["A"], 4)
        self.assertAlmostEqual(values["B"], math.pi)

    def test_atan2_accounts_for_all_quadrants_and_axes(self):
        for y, x, degrees in (
            (1, 1, 45), (1, -1, 135), (-1, -1, -135), (-1, 1, -45),
            (0, 1, 0), (1, 0, 90), (0, -1, 180), (-1, 0, -90),
        ):
            with self.subTest(y=y, x=x):
                self.assertEqual(solve([f"A = DEG(ATAN2({y}, {x}))"]), {"A": degrees})

    def test_inverse_sine_and_cosine_include_their_domain_endpoints(self):
        self.assertEqual(
            solve([
                "A = DEG(ASIN(-1))", "B = DEG(ASIN(1))",
                "C = DEG(ACOS(-1))", "D = DEG(ACOS(1))",
            ]),
            {"A": -90, "B": 90, "C": 180, "D": 0},
        )

    def test_invalid_inverse_trig_inputs_are_rejected(self):
        for expression in ("ASIN(2)", "ACOS(-2)", "ATAN2(0, 0)"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve([f"A = {expression}"])
        for expression in ("ASIN(X)", "ACOS(X)", "ATAN2(Y, Y)"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve([f"A = {expression}", "X = 2", "Y = 0"])

    def test_absolute_value_still_requires_a_unique_real_solution(self):
        with self.assertRaisesRegex(ValueError, "multiple solutions"):
            solve(["ABS(X) = 2"])
        self.assertEqual(solve(["ABS(X) = 0"]), {"X": 0})


class RoundTests(unittest.TestCase):
    def test_rounds_decimal_places_and_negative_places_with_ties_to_even(self):
        for value, places, expected in (
            ("1/3", 2, 0.33), ("2.675", 2, 2.68), ("2.685", 2, 2.68),
            ("2.6749", 2, 2.67), ("2.6751", 2, 2.68),
            ("-2.675", 2, -2.68), ("-2.685", 2, -2.68),
            ("2.5", 0, 2), ("3.5", 0, 4), ("-2.5", 0, -2), ("-3.5", 0, -4),
            ("125", -1, 120), ("135", -1, 140), ("-125", -1, -120),
            ("0", 2, 0),
        ):
            with self.subTest(value=value, places=places):
                self.assertEqual(solve([f"A = ROUND({value}, {places})"]), {"A": expected})

    def test_value_and_precision_can_come_from_other_equations(self):
        equations = ["A = ROUND(X, P)", "2*X = 5.35", "P = 1 + 1"]

        self.assertEqual(solve(equations), {"A": 2.68, "X": 2.675, "P": 2})
        self.assertEqual(solve(list(reversed(equations))), solve(equations))

    def test_rounding_can_be_nested_and_used_by_later_equations(self):
        self.assertEqual(
            solve(["A = ROUND(SIN(RAD(30)), 2)", "B = ROUND(PI(), 2)*A"]),
            {"A": 0.5, "B": 1.57},
        )

    def test_rounding_preserves_exact_decimal_results_before_float_conversion(self):
        equations = parse_equations(["A = ROUND(2.675, 2)"])

        self.assertEqual(_solve_equations(equations), {"A": Rational(67, 25)})

    def test_noninteger_precision_is_rejected_even_when_solved_later(self):
        for precision in ("0.5", "PI()"):
            for equations in (
                [f"A = ROUND(1.23, {precision})"],
                ["A = ROUND(X, P)", "X = 1.23", f"P = {precision}"],
            ):
                with self.subTest(equations=equations):
                    with self.assertRaisesRegex(ValueError, "ROUND places must be an integer"):
                        solve(equations)


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

    def test_integrals_preserve_exact_fractions_before_float_conversion(self):
        equations = parse_equations(["A = INTEGRATE(X^2, X, 0, 1)"])

        self.assertEqual(_solve_equations(equations), {"A": Rational(1, 3)})

    def test_integrates_nested_functions_and_derivatives(self):
        for expression, expected in (
            ("INTEGRATE(ABS(X), X, -1, 1)", 1),
            ("INTEGRATE(SIN(X), X, 0, PI())", 2),
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

    def test_resolving_the_same_equations_samples_again_without_changing_them(self):
        equations = ["A = rand()"]
        original = equations.copy()
        with patch("typecalc.functions.rand.random.random", side_effect=[0.25, 0.75]):
            self.assertEqual(solve(equations), {"A": 0.25})
            self.assertEqual(solve(equations), {"A": 0.75})

        self.assertEqual(equations, original)

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
