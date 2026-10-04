"""Terminal workspace for editing and solving equations."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Static

from typecalc import solve

from .equation_list import EquationList
from .equation_row import EquationRow
from .library import LibraryScreen


class TypecalcApp(App, inherit_bindings=False):
    TITLE = "typecalc"
    BINDINGS = [
        Binding("a", "add_row", "Add"),
        Binding("l", "library", "Library"),
        Binding("ctrl+s", "solve", "Solve", priority=True),
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", show=False),
    ]
    CSS = """
    EquationList {
        width: 1fr;
        height: 1fr;
    }
    #results {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        border-left: solid $panel;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield EquationList([""], id="equations")
            yield Static("", id="results", markup=False)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(EquationRow).focus()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        return action == "quit" or not isinstance(self.screen, LibraryScreen)

    async def action_add_row(self) -> None:
        await self.query_one(EquationList).add_equation()

    def action_library(self) -> None:
        self.push_screen(
            LibraryScreen(self.query_one(EquationList)), self.on_library_closed
        )

    def on_library_closed(self, row: EquationRow | None) -> None:
        if row is not None:
            row.focus()

    def action_solve(self) -> None:
        equations = self.query_one(EquationList)
        equations.save_edits()
        results = self.query_one("#results", Static)
        if not any(equation.strip() for equation in equations.equations):
            results.update("No equations to solve.")
            return

        try:
            values = solve(equations.equations)
        except (ValueError, NotImplementedError) as error:
            results.update(str(error))
        else:
            results.update(
                "\n".join(f"{name} = {value}" for name, value in sorted(values.items()))
            )

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def main() -> None:
    TypecalcApp().run()
