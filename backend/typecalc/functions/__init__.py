"""Mathematical functions available to the AST converter."""

from collections.abc import Callable

import sympy

from .diff import diff


FUNCTIONS: dict[str, Callable[[list[sympy.Expr]], sympy.Expr]] = {
    "DIFF": diff,
}


def apply_function(name: str, arguments: list[sympy.Expr]) -> sympy.Expr:
    """Dispatch a function call after its arguments have been converted."""
    function = FUNCTIONS.get(name.upper())
    if function is None:
        raise ValueError(f"Unsupported function: {name!r}")

    return function(arguments)
