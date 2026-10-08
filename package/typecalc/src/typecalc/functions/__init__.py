"""Mathematical functions available to the AST converter."""

from collections.abc import Callable

import sympy

from .cos import cos
from .diff import diff
from .exp import exp
from .integrate import integrate
from .ln import ln
from .log import log
from .rand import rand
from .sin import sin
from .tan import tan


FUNCTIONS: dict[str, Callable[[list[sympy.Expr]], sympy.Expr]] = {
    "COS": cos,
    "DIFF": diff,
    "EXP": exp,
    "INTEGRATE": integrate,
    "LN": ln,
    "LOG": log,
    "RAND": rand,
    "SIN": sin,
    "TAN": tan,
}


def apply_function(name: str, arguments: list[sympy.Expr]) -> sympy.Expr:
    """Dispatch a function call after its arguments have been converted."""
    function = FUNCTIONS.get(name.upper())
    if function is None:
        raise ValueError(f"Unsupported function: {name!r}")

    return function(arguments)
