"""Exercise equation rows, their list, and solving in the TUI."""

import unittest
from unittest.mock import patch

from textual.app import App, ComposeResult
from textual.widgets import Input, Static

from typecalc_tui.app import TypecalcApp, main
from typecalc_tui.equation_list import EquationList
from typecalc_tui.equation_row import EquationRow


class RowsApp(App):
    def __init__(self, equations: list[str]):
        super().__init__()
        self.equations = equations

    def compose(self) -> ComposeResult:
        yield EquationList(self.equations)


class AppTests(unittest.IsolatedAsyncioTestCase):
    async def edit_equation(self, app, pilot, equation):
        await pilot.press("e")
        self.assertIsInstance(app.focused, Input)
        app.focused.value = equation
        await pilot.press("enter")

    async def test_plain_list_populates_rows_and_tracks_edits(self):
        equations = ["x = 1", "x = 1", "z = 3"]
        app = RowsApp(equations)
        async with app.run_test() as pilot:
            rows = list(app.query(EquationRow))
            self.assertEqual([row.equation for row in rows], equations)
            self.assertEqual([row.number for row in rows], [1, 2, 3])
            self.assertTrue(all(row.size.height == 1 for row in rows))

            rows[1].focus()
            await self.edit_equation(app, pilot, "y = 2")
            self.assertEqual(equations, ["x = 1", "y = 2", "z = 3"])
            await pilot.press("delete")
            self.assertEqual(equations, ["x = 1", "z = 3"])
            self.assertIs(app.focused, rows[2])
            self.assertEqual(rows[2].number, 2)
            self.assertEqual(rows[2].query_one(".number", Static).content, "2")

    async def test_selection_persists_while_navigating(self):
        app = RowsApp(["x = 1", "y = 2"])
        async with app.run_test() as pilot:
            first, second = app.query(EquationRow)
            first.focus()
            await pilot.press("space", "down", "space")
            self.assertIs(app.focused, second)
            self.assertTrue(first.selected)
            self.assertTrue(second.selected)
            self.assertTrue(first.has_class("-selected"))
            await pilot.press("up", "space")
            self.assertFalse(first.selected)
            self.assertTrue(second.selected)
            await pilot.press("up")
            self.assertIs(app.focused, first)

    async def test_editing_keys_do_not_trigger_row_or_app_actions(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            row = app.query_one(EquationRow)
            await pilot.press("space", "e", "e", "a", "q", "d", "l", "space")
            editor = row.query_one(Input)
            self.assertIs(app.focused, editor)
            self.assertEqual(editor.value, "eaqdl ")
            self.assertTrue(row.selected)
            self.assertEqual(len(app.query(EquationRow)), 1)

            await pilot.press("up", "down", "home", "delete")
            self.assertIs(app.focused, editor)
            self.assertEqual(editor.value, "aqdl ")
            await pilot.press("escape")
            self.assertEqual(row.equation, "")
            self.assertEqual(app.query_one(EquationList).equations, [""])
            self.assertFalse(editor.display)
            self.assertIs(app.focused, row)

    async def test_edit_save_and_cancel_restore_the_row(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            row = app.query_one(EquationRow)
            await self.edit_equation(app, pilot, "x + y = 10")
            self.assertEqual(row.equation, "x + y = 10")
            self.assertEqual(
                row.query_one(".expression", Static).content, "x + y = 10"
            )
            self.assertIs(app.focused, row)
            await pilot.press("e")
            self.assertEqual(app.focused.value, "x + y = 10")
            app.focused.value = "discard this"
            await pilot.press("escape")
            self.assertEqual(row.equation, "x + y = 10")
            self.assertEqual(app.query_one(EquationList).equations, ["x + y = 10"])

    async def test_add_delete_and_recover_from_an_empty_list(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            await self.edit_equation(app, pilot, "x = 1")
            await pilot.press("a")
            self.assertIsInstance(app.focused, Input)
            app.focused.value = "x = 1"
            await pilot.press("enter", "up", "delete")
            remaining = app.query_one(EquationRow)
            self.assertEqual(remaining.number, 1)
            self.assertIs(app.focused, remaining)
            self.assertEqual(app.query_one(EquationList).equations, ["x = 1"])

            await pilot.press("delete", "ctrl+s")
            self.assertEqual(len(app.query(EquationRow)), 0)
            self.assertEqual(app.query_one(EquationList).equations, [])
            self.assertEqual(
                app.query_one("#results", Static).content, "No equations to solve."
            )
            await pilot.press("a")
            app.focused.value = "y = 2"
            await pilot.press("enter")
            self.assertEqual(app.query_one(EquationRow).number, 1)
            self.assertEqual(app.query_one(EquationList).equations, ["y = 2"])

    async def test_clicking_another_row_saves_the_active_edit(self):
        app = RowsApp(["x = 1", "y = 2"])
        async with app.run_test() as pilot:
            first, second = app.query(EquationRow)
            first.focus()
            await pilot.press("e")
            app.focused.value = "x = 3"
            await pilot.click(second)
            self.assertIs(app.focused, second)
            self.assertFalse(first.editing)
            self.assertEqual(app.equations, ["x = 3", "y = 2"])

    async def test_navigation_scrolls_to_rows_beyond_the_viewport(self):
        app = RowsApp([f"x = {number}" for number in range(30)])
        async with app.run_test(size=(60, 10)) as pilot:
            rows = list(app.query(EquationRow))
            rows[0].focus()
            await pilot.press(*(["down"] * 29))
            await pilot.pause()
            self.assertIs(app.focused, rows[-1])
            self.assertGreater(app.query_one(EquationList).scroll_y, 0)
            self.assertLess(rows[-1].region.y, 10)

    async def test_solve_command_displays_sorted_values(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            await self.edit_equation(app, pilot, "B + A = 10")
            await pilot.press("a")
            app.focused.value = "A = 6"
            await pilot.press("ctrl+s")
            self.assertEqual(
                app.query_one("#results", Static).content, "A = 6.0\nB = 4.0"
            )

    async def test_keyboard_solving_recovers_from_an_error(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            await self.edit_equation(app, pilot, "A + B = 10")
            await pilot.press("ctrl+s")
            self.assertIn(
                "not fully determined", app.query_one("#results", Static).content
            )

            await pilot.press("a")
            app.focused.value = "A = 6"
            await pilot.press("ctrl+s")
            self.assertEqual(
                app.query_one(EquationList).equations, ["A + B = 10", "A = 6"]
            )
            self.assertEqual(
                app.query_one("#results", Static).content, "A = 6.0\nB = 4.0"
            )

    async def test_empty_editor_and_quit_shortcut(self):
        app = TypecalcApp()
        async with app.run_test() as pilot:
            await pilot.press("ctrl+s")
            self.assertEqual(
                app.query_one("#results", Static).content, "No equations to solve."
            )
            await pilot.press("ctrl+q")
            self.assertTrue(app.is_running)
            await pilot.press("q")
            self.assertFalse(app.is_running)

    def test_launcher_starts_the_tui(self):
        with patch("typecalc_tui.app.TypecalcApp.run") as run:
            main()
        run.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
