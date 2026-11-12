"""Vectors and matrices through the public equation solver."""

import json
import math
import unittest

from typecalc import solve


class ArrayTests(unittest.TestCase):
    def test_output_preserves_rank_and_uses_finite_python_floats(self):
        expected = {
            "scalar": 2.0,
            "vector": [1.0, 0.5],
            "matrix": [[1.0, 2.0], [3.0, 4.0]],
            "singleton": [7.0],
            "row": [[7.0, 8.0]],
            "column": [[7.0], [8.0]],
            "cell": [[7.0]],
        }
        values = solve([
            "scalar = 2", "vector = [1, 1/2]", "matrix = [[1,2],[3,4]]",
            "singleton = [7]", "row = [[7,8]]", "column = [[7],[8]]", "cell = [[7]]",
        ])
        self.assertEqual(values, expected)
        self.assertEqual(json.loads(json.dumps(values, allow_nan=False)), expected)
        for value in values.values():
            elements = value if isinstance(value, list) else [value]
            for element in elements:
                for number in element if isinstance(element, list) else [element]:
                    self.assertIs(type(number), float)
                    self.assertTrue(math.isfinite(number))

    def test_aliases_and_forward_references_are_order_independent(self):
        equations = ["result = alias + source", "alias = source", "[x, 2] = source", "x = 3"]
        expected = {"result": [6.0, 4.0], "alias": [3.0, 2.0], "source": [3.0, 2.0], "x": 3.0}
        for rows in (equations, list(reversed(equations)), equations[2:] + equations[:2]):
            with self.subTest(rows=rows):
                self.assertEqual(solve(rows), expected)

    def test_matrix_shapes_propagate_through_functions_and_aliases(self):
        self.assertEqual(solve([
            "result = [1,2] @ alias", "alias = transposed", "transposed = TRANSPOSE(source)",
            "source = [[1,2],[3,4],[5,6]]",
        ]), {
            "result": [5.0, 11.0, 17.0],
            "alias": [[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]],
            "transposed": [[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]],
            "source": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
        })

    def test_solves_explicit_unknown_vector_components(self):
        equations = ["v = [x,y]", "[[2,1],[1,-1]] @ v = [5,1]"]
        for rows in (equations, list(reversed(equations))):
            with self.subTest(rows=rows):
                self.assertEqual(solve(rows), {"v": [2.0, 1.0], "x": 2.0, "y": 1.0})

    def test_solves_explicit_unknown_matrix_components(self):
        self.assertEqual(solve(["A = [[x,2],[3,y]]", "A @ [1,1] = [5,7]"]), {
            "A": [[3.0, 2.0], [3.0, 4.0]], "x": 3.0, "y": 4.0,
        })

    def test_products_preserve_their_distinct_rank_rules(self):
        for expression, expected in (
            ("[1,2] @ [3,4]", 11.0),
            ("[[1,2],[3,4],[5,6]] @ [2,3]", [8.0, 18.0, 28.0]),
            ("[2,3] @ [[1,2,3],[4,5,6]]", [14.0, 19.0, 24.0]),
            ("[[1,2],[3,4]] @ [[5],[6]]", [[17.0], [39.0]]),
            ("[1,2] * [3,4]", [3.0, 8.0]),
            ("[[1,2],[3,4]] * [[5,6],[7,8]]", [[5.0, 12.0], [21.0, 32.0]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(solve([f"result = {expression}"]), {"result": expected})

    def test_matmul_shares_multiplication_precedence_and_is_left_associative(self):
        for expression, expected in (
            ("[1,2] @ [[1,2],[3,4]] * [2,3]", [14.0, 30.0]),
            ("[1,2] * [3,4] @ [5,6]", 63.0),
            ("[1,2] @ [[1,2],[3,4]] @ [2,3]", 44.0),
            ("1 + [1,2] @ [3,4]", 12.0),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(solve([f"result = {expression}"]), {"result": expected})

    def test_arithmetic_and_vector_matrix_conversions(self):
        for expression, expected in (
            ("[1,2] + [3,4] - [2,1]", [2.0, 5.0]),
            ("[[1,2]] + [[3,4]] - [[2,1]]", [[2.0, 5.0]]),
            ("2 * [1,2]", [2.0, 4.0]),
            ("[[1,2],[3,4]] * 2 / 4", [[0.5, 1.0], [1.5, 2.0]]),
            ("-([1,2]) + +[3,4]", [2.0, 2.0]),
            ("-[[1,2]]", [[-1.0, -2.0]]),
            ("dOt([1,2],[3,4])", 11.0),
            ("nOrM([3,4])", 5.0),
            ("TRANSPOSE([1,2])", [1.0, 2.0]),
            ("tRaNsPoSe([[1,2,3],[4,5,6]])", [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]]),
            ("rOw([1,2])", [[1.0, 2.0]]),
            ("cOl([1,2])", [[1.0], [2.0]]),
        ):
            with self.subTest(expression=expression):
                self.assertEqual(solve([f"result = {expression}"]), {"result": expected})

    def test_norm_uses_complex_component_magnitudes(self):
        for expression, expected in (
            ("NORM([(-1)^(1/2),1])", math.sqrt(2)),
            ("NORM([3+4*(-1)^(1/2)])", 5.0),
        ):
            with self.subTest(expression=expression):
                result = solve([f"result = {expression}"])["result"]
                self.assertAlmostEqual(result, expected)

    def test_norm_preserves_real_symbolic_solving_and_differentiation(self):
        self.assertEqual(solve(["NORM([x,4]) = x+2"]), {"x": 3.0})
        self.assertEqual(
            solve(["slope = DIFF(NORM([x,4])|x=-3)"]),
            {"slope": -0.6},
        )

    def test_scalar_functions_can_be_nested_inside_literals(self):
        self.assertEqual(solve([
            "v = [ABS(x), LN(EXP(2)), NORM([3,4])]", "x = -3",
            "A = [[SIN(0), COS(0)], [DOT([1,2],[3,4]), ABS(-2)]]",
        ]), {"v": [3.0, 2.0, 5.0], "x": -3.0, "A": [[0.0, 1.0], [11.0, 2.0]]})

    def test_rejects_invalid_shapes_ranks_and_operations(self):
        for expression in (
            "[]", "[[]]", "[[1,2],[3]]", "[1,[2]]", "[[[1]]]",
            "[1,2] + [3]", "[[1,2]] + [[3],[4]]", "[1,2] - [[3,4]]",
            "[1,2] * [3]", "[1,2] + 1", "1 - [1,2]",
            "[1,2] / [3,4]", "1 / [1,2]", "[1,2] ^ 2", "2 ^ [1,2]",
            "[1,2] @ [3]", "[[1,2]] @ [[3,4]]", "[[1,2]] @ [3]",
            "[1,2] @ [[3,4]]", "2 @ [1,2]", "[1,2] @ 2",
            "DOT([[1,2]], [[3,4]])", "DOT([1,2],[3])", "DOT([1,2])",
            "NORM([[3,4]])", "NORM(3)", "NORM([3],[4])",
            "TRANSPOSE(1)", "TRANSPOSE([1],[2])",
            "ROW([[1,2]])", "ROW()", "COL(1)", "COL([1],[2])",
            "SIN([1,2])", "ROUND([1,2], 0)",
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve([f"result = {expression}"])

    def test_rejects_scalar_array_conflicts_and_undeclared_array_unknowns(self):
        for equations in (
            ["v = [1,2]", "v = 1"],
            ["v = [x,2]", "x = [1,2]"],
            ["v = [1,2]", "v = [[1,2]]"],
            ["[[2,1],[1,-1]] @ v = [5,1]"],
            ["v = [x,y]", "x = 1"],
        ):
            with self.subTest(equations=equations):
                with self.assertRaises(ValueError):
                    solve(equations)

    def test_rejects_nonfinite_and_complex_elements(self):
        for expression in ("[10^400, 1]", "[[1,(-1)^(1/2)]]", "[1,2] / 0"):
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    solve([f"result = {expression}"])


if __name__ == "__main__":
    unittest.main()
