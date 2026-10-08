"""Calculate the inverse sine in radians."""

import sympy


def asin(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ASIN(value) returns the principal angle in [-pi/2, pi/2]."""
    if len(arguments) != 1:
        raise ValueError("ASIN requires exactly one argument.")

    return sympy.asin(arguments[0])
