"""Tests for solving AST equations with the SymPy variable solver."""

from copy import deepcopy
import unittest

from sympy import Rational

from typecalc.parser import parse_equations
from typecalc.solver import _solve_equations


class SolveVariablesTests(unittest.TestCase):
    def solve(self, equations):
        return _solve_equations(parse_equations(equations))

    def test_solves_without_changing_the_equation_trees(self):
        equations = parse_equations(["A + B = 10", "B = SOLVE(B)", "A = 6"])
        original = deepcopy(equations)

        self.assertEqual(_solve_equations(equations), {"A": 6, "B": 4})
        self.assertEqual(equations, original)

    def test_solves_simultaneous_equations(self):
        self.assertEqual(self.solve(["X + Y = 10", "X - Y = 2"]), {"X": 6, "Y": 4})

    def test_solve_accepts_expressions_and_nested_calls(self):
        self.assertEqual(
            self.solve(["C = 2 * SOLVE(A + SOLVE(B))", "A = 1", "B = 2"]),
            {"A": 1, "B": 2, "C": 6},
        )

    def test_solve_can_reference_a_different_variable(self):
        self.assertEqual(self.solve(["A = SOLVE(B)", "B = 3"]), {"A": 3, "B": 3})

    def test_supports_all_binary_operations(self):
        self.assertEqual(
            self.solve(["A = (2 + 3) * 4 / 5 - 1", "B = A^2^2"]),
            {"A": 3, "B": 81},
        )

    def test_keeps_decimal_results_exact(self):
        self.assertEqual(
            self.solve(["A = 0.1", "B = 0.2", "C = A + B"]),
            {"A": Rational(1, 10), "B": Rational(1, 5), "C": Rational(3, 10)},
        )

    def test_accepts_redundant_equations(self):
        self.assertEqual(self.solve(["A = 6", "A = 6", "2*A = 12"]), {"A": 6})

    def test_accepts_a_unique_nonlinear_solution(self):
        self.assertEqual(self.solve(["A^2 = 0"]), {"A": 0})

    def test_reports_unresolved_variables(self):
        for equations in (
            ["A + B = 10"],
            ["B = SOLVE(B)"],
            ["A = 6", "B = SOLVE(B)"],
            ["A = A", "B = 2"],
            ["(A + 1)^2 = A^2 + 2*A + 1"],
        ):
            with self.subTest(equations=equations):
                with self.assertRaisesRegex(ValueError, "not fully determined"):
                    self.solve(equations)

    def test_reports_inconsistent_equations(self):
        for equations in (
            ["A = 6", "A = 7"],
            ["A + B = 10", "2*A + 2*B = 21"],
            ["A = SOLVE(A + 1)"],
            ["1 = 2"],
        ):
            with self.subTest(equations=equations):
                with self.assertRaisesRegex(ValueError, "no solution"):
                    self.solve(equations)

    def test_reports_multiple_solutions(self):
        with self.assertRaisesRegex(ValueError, "multiple solutions"):
            self.solve(["A^2 = 4"])

    def test_empty_and_identity_equations_have_no_variable_values(self):
        for equations in ([], ["", "  "], ["1 = 1", "1 + 1 = 2"]):
            with self.subTest(equations=equations):
                self.assertEqual(self.solve(equations), {})

    def test_solve_requires_one_argument(self):
        for expression in ("SOLVE()", "SOLVE(A, B)"):
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, "exactly one argument"):
                    self.solve(["A = " + expression])

    def test_rejects_unsupported_functions(self):
        with self.assertRaisesRegex(ValueError, "Unsupported function.*UNKNOWN"):
            self.solve(["A = UNKNOWN(B)"])

    def test_solver_limitations_are_distinct_from_inconsistent_equations(self):
        with self.assertRaises(NotImplementedError):
            self.solve(["X + 2^X + 3^X = 0"])


if __name__ == "__main__":
    unittest.main()
