"""Convert an angle from degrees to radians."""

import sympy


def rad(arguments: list[sympy.Expr]) -> sympy.Expr:
    """RAD(degrees) returns the angle in radians."""
    if len(arguments) != 1:
        raise ValueError("RAD requires exactly one argument.")

    return arguments[0] * sympy.pi / 180
