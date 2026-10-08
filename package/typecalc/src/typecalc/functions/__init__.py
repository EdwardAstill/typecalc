"""Mathematical functions available to the AST converter."""

from collections.abc import Callable

import sympy

from .atan2 import atan2
from .diff import diff
from .integrate import integrate
from .ln import ln
from .log import log
from .rand import rand
from .round import _Round


type Handler = Callable[..., sympy.Expr]

FUNCTIONS: dict[str, tuple[tuple[int, ...], Handler]] = {
    "ABS": ((1,), sympy.Abs),
    "ACOS": ((1,), sympy.acos),
    "ASIN": ((1,), sympy.asin),
    "ATAN": ((1,), sympy.atan),
    "ATAN2": ((2,), atan2),
    "COS": ((1,), sympy.cos),
    "DEG": ((1,), sympy.deg),
    "DIFF": ((2, 3), diff),
    "EXP": ((1,), sympy.exp),
    "INTEGRATE": ((4,), integrate),
    "LN": ((1,), ln),
    "LOG": ((2,), log),
    "PI": ((0,), lambda: sympy.pi),
    "RAD": ((1,), sympy.rad),
    "RAND": ((0,), rand),
    "ROUND": ((2,), _Round),
    "SIN": ((1,), sympy.sin),
    "TAN": ((1,), sympy.tan),
}


def apply_function(name: str, arguments: list[sympy.Expr]) -> sympy.Expr:
    """Dispatch a function call after its arguments have been converted."""
    entry = FUNCTIONS.get(name.upper())
    if entry is None:
        raise ValueError(f"Unsupported function: {name!r}")
    counts, function = entry
    if len(arguments) not in counts:
        expected = "no" if counts == (0,) else " or ".join(map(str, counts))
        noun = "argument" if counts == (1,) else "arguments"
        raise ValueError(f"{name.upper()} requires {expected} {noun}.")
    return function(*arguments)
