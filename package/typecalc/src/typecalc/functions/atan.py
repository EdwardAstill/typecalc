"""Calculate the inverse tangent in radians."""

import sympy


def atan(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ATAN(value) returns the principal angle in (-pi/2, pi/2)."""
    if len(arguments) != 1:
        raise ValueError("ATAN requires exactly one argument.")

    return sympy.atan(arguments[0])
