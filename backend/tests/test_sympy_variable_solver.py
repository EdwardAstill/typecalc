"""Tests for solving AST equations with the SymPy variable solver."""

from copy import deepcopy
import unittest

from sympy import Rational

from typecalc import parse_document, solve_variables


class SolveVariablesTests(unittest.TestCase):
    def solve(self, equations):
        return solve_variables(parse_document("EQUATIONS\n" + equations))

    def test_solves_across_blocks_without_changing_the_document(self):
        document = parse_document(
            "EQUATIONS\nA + B = 10\nB = SOLVE(B)\n\n"
            "TEXT\nKeep this text.\n\n"
            "EQUATIONS\nA = 6\n"
        )
        original = deepcopy(document)

        self.assertEqual(solve_variables(document), {"A": 6, "B": 4})
        self.assertEqual(document, original)

    def test_solves_simultaneous_equations(self):
        self.assertEqual(self.solve("X + Y = 10\nX - Y = 2"), {"X": 6, "Y": 4})

    def test_solve_accepts_expressions_and_nested_calls(self):
        self.assertEqual(
            self.solve("C = 2 * SOLVE(A + SOLVE(B))\nA = 1\nB = 2"),
            {"A": 1, "B": 2, "C": 6},
        )

    def test_solve_can_reference_a_different_variable(self):
        self.assertEqual(self.solve("A = SOLVE(B)\nB = 3"), {"A": 3, "B": 3})

    def test_supports_all_binary_operations(self):
        self.assertEqual(
            self.solve("A = (2 + 3) * 4 / 5 - 1\nB = A^2^2"),
            {"A": 3, "B": 81},
        )

    def test_keeps_decimal_results_exact(self):
        self.assertEqual(
            self.solve("A = 0.1\nB = 0.2\nC = A + B"),
            {"A": Rational(1, 10), "B": Rational(1, 5), "C": Rational(3, 10)},
        )

    def test_accepts_redundant_equations(self):
        self.assertEqual(self.solve("A = 6\nA = 6\n2*A = 12"), {"A": 6})

    def test_accepts_a_unique_nonlinear_solution(self):
        self.assertEqual(self.solve("A^2 = 0"), {"A": 0})

    def test_reports_unresolved_variables(self):
        for equations in (
            "A + B = 10",
            "B = SOLVE(B)",
            "A = 6\nB = SOLVE(B)",
            "A = A\nB = 2",
            "(A + 1)^2 = A^2 + 2*A + 1",
        ):
            with self.subTest(equations=equations):
                with self.assertRaisesRegex(ValueError, "not fully determined"):
                    self.solve(equations)

    def test_reports_inconsistent_equations(self):
        for equations in (
            "A = 6\nA = 7",
            "A + B = 10\n2*A + 2*B = 21",
            "A = SOLVE(A + 1)",
            "1 = 2",
        ):
            with self.subTest(equations=equations):
                with self.assertRaisesRegex(ValueError, "no solution"):
                    self.solve(equations)

    def test_reports_multiple_solutions(self):
        with self.assertRaisesRegex(ValueError, "multiple solutions"):
            self.solve("A^2 = 4")

    def test_empty_and_text_only_documents_have_no_variable_values(self):
        for source in ("", "TEXT\nOnly text.", "EQUATIONS\n1 = 1\n1 + 1 = 2"):
            with self.subTest(source=source):
                self.assertEqual(solve_variables(parse_document(source)), {})

    def test_solve_requires_one_argument(self):
        for expression in ("SOLVE()", "SOLVE(A, B)"):
            with self.subTest(expression=expression):
                with self.assertRaisesRegex(ValueError, "exactly one argument"):
                    self.solve("A = " + expression)

    def test_rejects_unsupported_functions(self):
        with self.assertRaisesRegex(ValueError, "Unsupported function.*SIN"):
            self.solve("A = SIN(B)")

    def test_solver_limitations_are_distinct_from_inconsistent_equations(self):
        with self.assertRaises(NotImplementedError):
            self.solve("X + 2^X + 3^X = 0")


if __name__ == "__main__":
    unittest.main()
