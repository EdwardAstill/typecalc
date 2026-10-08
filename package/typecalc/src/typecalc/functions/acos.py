"""Calculate the inverse cosine in radians."""

import sympy


def acos(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ACOS(value) returns the principal angle in [0, pi]."""
    if len(arguments) != 1:
        raise ValueError("ACOS requires exactly one argument.")

    return sympy.acos(arguments[0])
