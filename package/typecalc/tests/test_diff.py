"""Derivative syntax, variable scope, and solving."""

import unittest

from typecalc import solve
from typecalc.ast import FunctionCall, Number, Symbol
from typecalc.parser import parse_equation, parse_expression


class DiffTests(unittest.TestCase):
    def test_point_syntax_builds_an_ordinary_function_call(self):
        self.assertEqual(
            parse_expression("DIFF(X^2 | X=10)"),
            FunctionCall("DIFF", [parse_expression("X^2"), Symbol("X"), Number("10")]),
        )

    def test_equation_parser_distinguishes_inner_and_outer_equals(self):
        equation = parse_equation("DIFF(X^2 | X=3) = DIFF(Y^2 | Y=3)")

        self.assertEqual(equation.left, parse_expression("DIFF(X^2 | X=3)"))
        self.assertEqual(equation.right, parse_expression("DIFF(Y^2 | Y=3)"))

    def test_idea_example_solves_without_a_global_x(self):
        equations = ["A + B = 10", "A = DIFF(X^2 | X=10)"]
        original = equations.copy()

        self.assertEqual(solve(equations), {"A": 20, "B": -10})
        self.assertEqual(equations, original)

    def test_differentiates_before_substituting_solved_variable_values(self):
        equations = ["A = DIFF(X^2, X)", "X = 10"]

        self.assertEqual(solve(equations), {"A": 20, "X": 10})

    def test_point_is_local_and_does_not_change_the_global_variable(self):
        equations = ["X = 3", "A = DIFF(X^2 | X=10)"]

        self.assertEqual(solve(equations), {"X": 3, "A": 20})

    def test_coefficients_and_point_expressions_use_solved_values(self):
        equations = ["A = DIFF(C*X^2 | X=P + 1)", "C = 3", "P = 4"]

        self.assertEqual(solve(equations), {"A": 30, "C": 3, "P": 4})

    def test_supports_nested_derivatives(self):
        equations = ["A = DIFF(DIFF(X^3, X) | X=2)"]

        self.assertEqual(solve(equations), {"A": 12})

    def test_derivative_can_remove_the_need_for_a_variable_value(self):
        for expression, expected in (("DIFF(X, X)", 1), ("DIFF(7, X)", 0)):
            with self.subTest(expression=expression):
                equations = [f"A = {expression}"]

                self.assertEqual(solve(equations), {"A": expected})

    def test_lowercase_diff_uses_the_same_function(self):
        equations = ["A = diff(X^2 | X=3)"]

        self.assertEqual(solve(equations), {"A": 6})

    def test_negative_points_and_unary_minus_preserve_power_precedence(self):
        for expression, expected in (
            ("DIFF(X^2 | X=-2)", -4),
            ("DIFF(-X^2 | X=2)", -4),
            ("DIFF(X^-2 | X=2)", -0.25),
        ):
            with self.subTest(expression=expression):
                equations = [f"A = {expression}"]

                self.assertEqual(solve(equations), {"A": expected})

    def test_unresolved_derivative_values_still_report_missing_information(self):
        equations = ["A = DIFF(X^2, X)"]

        with self.assertRaisesRegex(ValueError, "not fully determined"):
            solve(equations)

    def test_invalid_diff_arguments_report_clear_errors(self):
        for expression, message in (
            ("DIFF()", "DIFF requires"),
            ("DIFF(X)", "DIFF requires"),
            ("DIFF(X, X, 1, 2)", "DIFF requires"),
            ("DIFF(X^2, 2)", "variable must be a symbol"),
            ("DIFF(X^2, X + Y)", "variable must be a symbol"),
        ):
            with self.subTest(expression=expression):
                equations = [f"A = {expression}"]

                with self.assertRaisesRegex(ValueError, message):
                    solve(equations)

    def test_invalid_condition_syntax_is_rejected(self):
        for expression in (
            "DIFF(X^2 | 10=2)",
            "DIFF(X^2 | X)",
            "DIFF(X^2 | X=)",
            "DIFF(X^2 | X=10, Y=2)",
            "DIFF(X^2 | X$=10)",
            "SIN(X | X=10)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    parse_expression(expression)

    def test_multiple_outer_equals_are_still_rejected(self):
        with self.assertRaises(ValueError):
            parse_equation("A = DIFF(X^2 | X=10) = 20")


if __name__ == "__main__":
    unittest.main()
