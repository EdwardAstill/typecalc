"""Convert an angle from radians to degrees."""

import sympy


def deg(arguments: list[sympy.Expr]) -> sympy.Expr:
    """DEG(radians) returns the angle in degrees."""
    if len(arguments) != 1:
        raise ValueError("DEG requires exactly one argument.")

    return arguments[0] * 180 / sympy.pi
