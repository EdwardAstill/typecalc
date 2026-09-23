"""Tests for replacing SOLVE calls in a document AST."""

from copy import deepcopy
import unittest

from typecalc import Number, evaluate_document, parse_document


class EvaluateDocumentTests(unittest.TestCase):
    def test_replaces_solve_calls_and_preserves_blocks(self):
        document = parse_document(
            "EQUATIONS\nA + B = 10\nB = SOLVE(B)\n\n"
            "TEXT\nKeep this text.\nAnd this line.\n\n"
            "EQUATIONS\nA = 6"
        )
        original = deepcopy(document)
        expected = parse_document(
            "EQUATIONS\nA + B = 10\nB = 4\n\n"
            "TEXT\nKeep this text.\nAnd this line.\n\n"
            "EQUATIONS\nA = 6"
        )

        result = evaluate_document(document)

        self.assertEqual(result, expected)
        self.assertEqual(document, original)
        self.assertIsNot(result, document)

        # Editing the returned tree must not change the input tree.
        result.blocks[0].equations[0].left.left.name = "changed"
        result.blocks[1].text = "changed"
        result.blocks[2].equations[0].right.value = 99
        self.assertEqual(document, original)

    def test_evaluates_nested_calls_and_preserves_surrounding_arithmetic(self):
        document = parse_document(
            "EQUATIONS\nC = 2 * SOLVE(A + SOLVE(B))\nA = 1\nB = 2"
        )
        expected = parse_document("EQUATIONS\nC = 2 * 3\nA = 1\nB = 2")

        self.assertEqual(evaluate_document(document), expected)

    def test_evaluates_calls_on_both_sides(self):
        document = parse_document("EQUATIONS\nSOLVE(A) = SOLVE(B)\nA = 3")
        expected = parse_document("EQUATIONS\n3 = 3\nA = 3")

        self.assertEqual(evaluate_document(document), expected)

    def test_evaluates_arithmetic_inside_solve(self):
        document = parse_document(
            "EQUATIONS\nA = 3\nB = SOLVE((A + 1) * 2 / 4 - 1 + A^2)"
        )
        expected = parse_document("EQUATIONS\nA = 3\nB = 10")

        self.assertEqual(evaluate_document(document), expected)

    def test_evaluates_constant_calls_without_variables(self):
        document = parse_document("EQUATIONS\nSOLVE(1 + 2) = 3")
        expected = parse_document("EQUATIONS\n3 = 3")

        self.assertEqual(evaluate_document(document), expected)

    def test_returns_numeric_values_for_fractions_roots_and_negative_results(self):
        for expression, expected in (("1/3", 1/3), ("2^(1/2)", 2**0.5), ("1-3", -2)):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = SOLVE({expression})")
                result = evaluate_document(document).blocks[0].equations[0].right

                self.assertIsInstance(result, Number)
                self.assertAlmostEqual(result.value, expected)

    def test_preserves_equations_without_solve(self):
        document = parse_document("EQUATIONS\nA = 2 + 3\nB = A * 2")

        self.assertEqual(evaluate_document(document), document)

    def test_handles_empty_and_text_only_documents(self):
        for source in ("", "TEXT\nOnly text."):
            with self.subTest(source=source):
                document = parse_document(source)
                result = evaluate_document(document)

                self.assertEqual(result, document)
                self.assertIsNot(result, document)

    def test_propagates_solver_errors_without_changing_the_document(self):
        for equations, message in (
            ("B = SOLVE(B)", "not fully determined"),
            ("A = 1\nA = 2\nA = SOLVE(A)", "no solution"),
            ("A^2 = 4\nA = SOLVE(A)", "multiple solutions"),
        ):
            with self.subTest(equations=equations):
                document = parse_document("EQUATIONS\n" + equations)
                original = deepcopy(document)

                with self.assertRaisesRegex(ValueError, message):
                    evaluate_document(document)

                self.assertEqual(document, original)

    def test_reports_results_that_cannot_fit_a_number_node(self):
        for expression in ("(0 - 1)^(1/2)", "10^400"):
            with self.subTest(expression=expression):
                document = parse_document(f"EQUATIONS\nA = SOLVE({expression})")

                with self.assertRaisesRegex(ValueError, "finite real number"):
                    evaluate_document(document)


if __name__ == "__main__":
    unittest.main()
