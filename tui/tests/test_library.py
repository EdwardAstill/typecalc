"""Exercise the bundled equation dictionaries and floating library picker."""

import unittest

from textual.widgets import Input, Static, Tree

from typecalc.parser import parse_equation
from typecalc_tui.app import TypecalcApp
from typecalc_tui.equation_list import EquationList
from typecalc_tui.equation_row import EquationRow
from typecalc_tui.library import LibraryScreen, load_library


class LibraryDataTests(unittest.TestCase):
    def test_bundled_topics_contain_named_parseable_equations(self):
        library = load_library()
        self.assertEqual(set(library), {"Motion", "Electricity"})
        self.assertEqual(library["Motion"]["final_velocity"], "v = u + a * t")
        self.assertEqual(library["Electricity"]["ohms_law"], "V = I * R")
        for topic, equations in library.items():
            self.assertIsInstance(equations, dict)
            self.assertTrue(equations)
            for name, expression in equations.items():
                with self.subTest(topic=topic, equation=name):
                    self.assertTrue(name)
                    parse_equation(expression)


class LibraryScreenTests(unittest.IsolatedAsyncioTestCase):
    async def test_space_adds_multiple_equations_without_leaving_the_tree(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            workspace = app.screen
            equations = app.query_one(EquationList)
            first = app.query_one(EquationRow)
            await pilot.press("space", "l")
            self.assertIsInstance(app.screen, LibraryScreen)
            tree = app.screen.query_one(Tree)
            self.assertIs(app.focused, tree)
            self.assertEqual(
                [str(branch.label) for branch in tree.root.children],
                ["Electricity", "Motion"],
            )

            await pilot.press("enter", "down", "space", "down", "space")
            self.assertEqual(equations.equations, ["", "V = I * R", "P = V * I"])
            self.assertIsInstance(app.screen, LibraryScreen)
            self.assertIs(app.focused, tree)
            self.assertTrue(first.selected)
            rows = list(equations.query(EquationRow))
            self.assertEqual([row.number for row in rows], [1, 2, 3])
            self.assertFalse(rows[-1].editing)

            await pilot.press("escape")
            self.assertIs(app.screen, workspace)
            self.assertIs(app.focused, rows[-1])
            await pilot.press("e")
            self.assertIsInstance(app.focused, Input)
            self.assertEqual(app.focused.value, "P = V * I")
            app.focused.value = "P = 20"
            await pilot.press("enter")
            self.assertEqual(equations.equations[-1], "P = 20")
            self.assertEqual(load_library()["Electricity"]["power"], "P = V * I")
            await pilot.press("delete")
            self.assertEqual(equations.equations, ["", "V = I * R"])

    async def test_topics_and_cancel_do_not_add_rows_or_run_workspace_commands(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            workspace = app.screen
            equations = app.query_one(EquationList)
            results = app.query_one("#results", Static)
            first = app.query_one(EquationRow)
            await pilot.press("l", "a", "e", "delete", "ctrl+s", "space")
            self.assertIsInstance(app.screen, LibraryScreen)
            self.assertTrue(app.screen.query_one(Tree).cursor_node.is_expanded)
            self.assertEqual(equations.equations, [""])
            self.assertEqual(results.content, "")
            self.assertFalse(first.selected)
            await pilot.press("escape")
            self.assertIs(app.screen, workspace)
            self.assertIs(app.focused, first)
            await pilot.press("l", "l")
            self.assertIs(app.screen, workspace)
            self.assertEqual(len(app.screen_stack), 1)

    async def test_motion_equation_can_be_added_to_an_empty_workspace_and_solved(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            equations = app.query_one(EquationList)
            await pilot.press("delete", "l")
            tree = app.screen.query_one(Tree)
            tree.move_cursor(tree.root.children[1])
            await pilot.press("enter", "down", "space", "l")
            self.assertEqual(equations.equations, ["v = u + a * t"])
            row = equations.query_one(EquationRow)
            self.assertEqual(row.number, 1)
            self.assertIs(app.focused, row)

            for value in ("u = 1", "a = 2", "t = 3"):
                await pilot.press("a")
                app.focused.value = value
                await pilot.press("enter")
            await pilot.press("ctrl+s")
            self.assertEqual(
                app.query_one("#results", Static).content,
                "a = 2.0\nt = 3.0\nu = 1.0\nv = 7.0",
            )

    async def test_q_quits_while_the_library_is_open(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            await pilot.press("l", "q")
            self.assertFalse(app.is_running)


if __name__ == "__main__":
    unittest.main()
