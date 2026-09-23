"""Derivative syntax, variable scope, and document evaluation."""

from copy import deepcopy
import unittest

from typecalc import (
    FunctionCall,
    Number,
    Symbol,
    evaluate_document,
    parse_document,
    parse_equation,
    parse_expression,
    solve_variables,
)


class DiffTests(unittest.TestCase):
    def test_point_syntax_builds_an_ordinary_function_call(self):
        self.assertEqual(
            parse_expression("DIFF(X^2 | X=10)"),
            FunctionCall("DIFF", [parse_expression("X^2"), Symbol("X"), Number(10)]),
        )

    def test_equation_parser_distinguishes_inner_and_outer_equals(self):
        equation = parse_equation("DIFF(X^2 | X=3) = DIFF(Y^2 | Y=3)")

        self.assertEqual(equation.left, parse_expression("DIFF(X^2 | X=3)"))
        self.assertEqual(equation.right, parse_expression("DIFF(Y^2 | Y=3)"))

    def test_idea_example_solves_and_evaluates_without_a_global_x(self):
        document = parse_document(
            "EQUATIONS\nA + B = 10\nA = DIFF(X^2 | X=10)\nB = SOLVE(B)\n\n"
            "TEXT\nKeep this explanation."
        )
        original = deepcopy(document)

        self.assertEqual(solve_variables(document), {"A": 20, "B": -10})
        result = evaluate_document(document)

        self.assertEqual(result.blocks[0].equations[0], document.blocks[0].equations[0])
        self.assertEqual(result.blocks[0].equations[1].right, Number(20))
        self.assertEqual(result.blocks[0].equations[2].right, Number(-10))
        self.assertEqual(result.blocks[1], document.blocks[1])
        self.assertEqual(document, original)

    def test_differentiates_before_substituting_solved_variable_values(self):
        document = parse_document("EQUATIONS\nA = DIFF(X^2, X)\nX = 10")

        self.assertEqual(solve_variables(document), {"A": 20, "X": 10})
        self.assertEqual(
            evaluate_document(document),
            parse_document("EQUATIONS\nA = 20\nX = 10"),
        )

    def test_point_is_local_and_does_not_change_the_document_variable(self):
        document = parse_document("EQUATIONS\nX = 3\nA = DIFF(X^2 | X=10)")

        self.assertEqual(solve_variables(document), {"X": 3, "A": 20})

    def test_coefficients_and_point_expressions_use_document_values(self):
        document = parse_document(
            "EQUATIONS\nA = DIFF(C*X^2 | X=P + 1)\nC = 3\nP = 4"
        )

        self.assertEqual(solve_variables(document), {"A": 30, "C": 3, "P": 4})
        self.assertEqual(evaluate_document(document).blocks[0].equations[0].right, Number(30))

    def test_supports_nested_derivatives(self):
        document = parse_document("EQUATIONS\nA = DIFF(DIFF(X^3, X) | X=2)")

        self.assertEqual(solve_variables(document), {"A": 12})
        self.assertEqual(evaluate_document(document).blocks[0].equations[0].right, Number(12))

    def test_diff_and_solve_can_be_nested_in_either_order(self):
        for expression in ("SOLVE(DIFF(X^2, X))", "DIFF(SOLVE(X^2), X)"):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = {expression}\nX = 3")

                self.assertEqual(
                    evaluate_document(document).blocks[0].equations[0].right,
                    Number(6),
                )

    def test_derivative_can_remove_the_need_for_a_variable_value(self):
        for expression, expected in (("DIFF(X, X)", 1), ("DIFF(7, X)", 0)):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = {expression}")

                self.assertEqual(solve_variables(document), {"A": expected})

    def test_lowercase_diff_uses_the_same_function(self):
        document = parse_document("EQUATIONS\nA = diff(X^2 | X=3)")

        self.assertEqual(evaluate_document(document).blocks[0].equations[0].right, Number(6))

    def test_negative_points_and_unary_minus_preserve_power_precedence(self):
        for expression, expected in (
            ("DIFF(X^2 | X=-2)", -4),
            ("DIFF(-X^2 | X=2)", -4),
            ("DIFF(X^-2 | X=2)", -0.25),
        ):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = {expression}")

                self.assertEqual(
                    evaluate_document(document).blocks[0].equations[0].right,
                    Number(expected),
                )

    def test_unresolved_derivative_values_still_report_missing_information(self):
        document = parse_document("EQUATIONS\nA = DIFF(X^2, X)")

        with self.assertRaisesRegex(ValueError, "not fully determined"):
            evaluate_document(document)

    def test_invalid_diff_arguments_report_clear_errors(self):
        for expression, message in (
            ("DIFF()", "DIFF requires"),
            ("DIFF(X)", "DIFF requires"),
            ("DIFF(X, X, 1, 2)", "DIFF requires"),
            ("DIFF(X^2, 2)", "variable must be a symbol"),
            ("DIFF(X^2, X + Y)", "variable must be a symbol"),
        ):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = {expression}")

                with self.assertRaisesRegex(ValueError, message):
                    solve_variables(document)

    def test_invalid_condition_syntax_is_rejected(self):
        for expression in (
            "DIFF(X^2 | 10=2)",
            "DIFF(X^2 | X)",
            "DIFF(X^2 | X=)",
            "DIFF(X^2 | X=10, Y=2)",
            "DIFF(X^2 | X$=10)",
            "SOLVE(X | X=10)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    parse_expression(expression)

    def test_multiple_outer_equals_are_still_rejected(self):
        with self.assertRaises(ValueError):
            parse_equation("A = DIFF(X^2 | X=10) = 20")


if __name__ == "__main__":
    unittest.main()
