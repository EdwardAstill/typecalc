"""Browse the TUI's named equations and add them to the workspace."""

import tomllib
from importlib.resources import files

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Footer, Tree

from .equation_list import EquationList
from .equation_row import EquationRow


def load_library() -> dict[str, dict[str, str]]:
    """Read the bundled topic files as dictionaries of named equations."""
    library = {}
    directory = files("typecalc_tui").joinpath("equation_library")
    for resource in sorted(directory.iterdir(), key=lambda resource: resource.name):
        if resource.name.endswith(".toml"):
            with resource.open("rb") as source:
                topic = tomllib.load(source)
            library[topic["name"]] = topic["equations"]
    return library


class LibraryScreen(ModalScreen[EquationRow]):
    BINDINGS = [
        Binding("space", "add_equation", "Add equation", priority=True),
        Binding("escape,l", "close", "Close"),
        Binding("q", "app.quit", "Quit"),
    ]
    DEFAULT_CSS = """
    LibraryScreen {
        align: center middle;
    }
    LibraryScreen Tree {
        width: 90%;
        max-width: 90;
        height: 80%;
        border: solid $panel;
        border-title-color: $foreground;
        background: $surface;
        padding: 0 1;
    }
    """

    def __init__(self, equations: EquationList) -> None:
        super().__init__()
        self.equations = equations
        self.last_added: EquationRow | None = None

    def compose(self) -> ComposeResult:
        tree = Tree[str]("Equation library", id="library-tree")
        tree.show_root = False
        tree.root.expand()
        for topic, equations in load_library().items():
            branch = tree.root.add(topic)
            for name, equation in equations.items():
                label = f"{name.replace('_', ' ').capitalize()}: {equation}"
                branch.add_leaf(label, data=equation)
        tree.border_title = "Equation library"
        yield tree
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one(Tree)
        tree.move_cursor(tree.root.children[0])
        tree.focus()

    async def action_add_equation(self) -> None:
        node = self.query_one(Tree).cursor_node
        if node is None:
            return
        if node.data is None:
            node.toggle()
        else:
            self.last_added = await self.equations.add_equation(node.data, edit=False)

    def action_close(self) -> None:
        self.dismiss(self.last_added)
