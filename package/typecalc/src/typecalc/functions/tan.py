"""Calculate the tangent of an angle in radians."""

import sympy


def tan(arguments: list[sympy.Expr]) -> sympy.Expr:
    """TAN(angle), with the angle in radians."""
    if len(arguments) != 1:
        raise ValueError("TAN requires exactly one argument.")

    return sympy.tan(arguments[0])
