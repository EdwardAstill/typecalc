"""A numbered equation with selection and inline editing actions."""

from __future__ import annotations

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.events import Click
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static


class EquationRow(Widget, can_focus=True):
    BINDINGS = [
        Binding("space", "select", "Select"),
        Binding("e", "edit", "Edit"),
        Binding("delete", "delete", "Delete"),
        Binding("escape", "cancel_edit", "Cancel edit"),
    ]
    DEFAULT_CSS = """
    EquationRow {
        layout: horizontal;
        height: 1;
        width: 1fr;
    }
    EquationRow:focus {
        background: $boost;
    }
    EquationRow.-selected .number {
        text-style: reverse;
    }
    EquationRow .number {
        width: 4;
        height: 1;
        text-align: right;
        padding-right: 1;
    }
    EquationRow .expression {
        width: 1fr;
        height: 1;
        text-wrap: nowrap;
        text-overflow: ellipsis;
    }
    EquationRow Input {
        display: none;
        width: 1fr;
        background: transparent;
    }
    """

    number = reactive(1)
    selected = reactive(False, toggle_class="-selected")

    @dataclass
    class Edited(Message):
        row: EquationRow

    @dataclass
    class DeleteRequested(Message):
        row: EquationRow

    def __init__(self, number: int, equation: str) -> None:
        super().__init__()
        self.number = number
        self.equation = equation
        self.editing = False

    def compose(self) -> ComposeResult:
        yield Static(str(self.number), classes="number")
        yield Static(self.equation, classes="expression", markup=False)
        yield Input(self.equation, compact=True, select_on_focus=False)

    def watch_number(self, number: int) -> None:
        if self.is_mounted:
            self.query_one(".number", Static).update(str(number))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        if action == "cancel_edit":
            return self.editing
        if action in {"select", "edit", "delete"}:
            return not self.editing
        return True

    def action_select(self) -> None:
        """Toggle selection independently of keyboard focus."""
        self.selected = not self.selected

    def action_edit(self) -> None:
        """Replace the equation display with an input in the same row."""
        if self.editing:
            return
        self.editing = True
        editor = self.query_one(Input)
        editor.value = self.equation
        self.query_one(".expression").display = False
        editor.display = True
        editor.focus()
        editor.cursor_position = len(editor.value)

    def finish_edit(self, *, save: bool, focus: bool = True) -> None:
        if not self.editing:
            return
        editor = self.query_one(Input)
        if save:
            self.equation = editor.value
            self.query_one(".expression", Static).update(editor.value)
            self.post_message(self.Edited(self))
        self.editing = False
        editor.display = False
        self.query_one(".expression").display = True
        if focus:
            self.focus()

    def action_cancel_edit(self) -> None:
        self.finish_edit(save=False)

    def action_delete(self) -> None:
        """Ask the equation list to remove this row."""
        self.post_message(self.DeleteRequested(self))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.finish_edit(save=True)

    def on_input_blurred(self, event: Input.Blurred) -> None:
        event.stop()
        self.finish_edit(save=True, focus=False)

    def on_click(self, event: Click) -> None:
        if not self.editing:
            self.focus()
