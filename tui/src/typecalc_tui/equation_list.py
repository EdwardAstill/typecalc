"""A plain equation list displayed as scrollable row widgets."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Input

from .equation_row import EquationRow


class EquationList(VerticalScroll):
    BINDINGS = [
        Binding("up", "move_row(-1)", show=False),
        Binding("down", "move_row(1)", show=False),
    ]

    def __init__(self, equations: list[str], *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.equations = equations

    def compose(self) -> ComposeResult:
        for number, equation in enumerate(self.equations, start=1):
            yield EquationRow(number, equation)

    async def add_equation(self, equation: str = "", *, edit: bool = True) -> EquationRow:
        self.equations.append(equation)
        row = EquationRow(len(self.equations), equation)
        await self.mount(row)
        if edit:
            row.action_edit()
        return row

    def save_edits(self) -> None:
        rows = list(self.query(EquationRow))
        for row in rows:
            row.finish_edit(save=True)
        self.equations[:] = [row.equation for row in rows]

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        if action == "move_row":
            return not isinstance(self.app.focused, Input)
        return True

    def action_move_row(self, direction: int) -> None:
        rows = list(self.query(EquationRow))
        focused = self.app.focused
        if isinstance(focused, EquationRow):
            index = rows.index(focused)
            rows[max(0, min(index + direction, len(rows) - 1))].focus()

    def on_equation_row_edited(self, event: EquationRow.Edited) -> None:
        event.stop()
        self.equations[event.row.number - 1] = event.row.equation

    async def on_equation_row_delete_requested(
        self, event: EquationRow.DeleteRequested
    ) -> None:
        event.stop()
        rows = list(self.query(EquationRow))
        index = rows.index(event.row)
        del self.equations[index]
        await event.row.remove()
        rows.pop(index)
        for number, row in enumerate(rows, start=1):
            row.number = number
        if rows:
            rows[min(index, len(rows) - 1)].focus()
        else:
            self.focus()
