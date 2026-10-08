"""Mathematical functions available to the AST converter."""

from collections.abc import Callable

import sympy

from .abs import abs
from .acos import acos
from .asin import asin
from .atan import atan
from .atan2 import atan2
from .cos import cos
from .deg import deg
from .diff import diff
from .exp import exp
from .integrate import integrate
from .ln import ln
from .log import log
from .pi import pi
from .rad import rad
from .rand import rand
from .round import round
from .sin import sin
from .tan import tan


FUNCTIONS: dict[str, Callable[[list[sympy.Expr]], sympy.Expr]] = {
    "ABS": abs,
    "ACOS": acos,
    "ASIN": asin,
    "ATAN": atan,
    "ATAN2": atan2,
    "COS": cos,
    "DEG": deg,
    "DIFF": diff,
    "EXP": exp,
    "INTEGRATE": integrate,
    "LN": ln,
    "LOG": log,
    "PI": pi,
    "RAD": rad,
    "RAND": rand,
    "ROUND": round,
    "SIN": sin,
    "TAN": tan,
}


def apply_function(name: str, arguments: list[sympy.Expr]) -> sympy.Expr:
    """Dispatch a function call after its arguments have been converted."""
    function = FUNCTIONS.get(name.upper())
    if function is None:
        raise ValueError(f"Unsupported function: {name!r}")

    return function(arguments)
