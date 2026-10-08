"""Calculate the sine of an angle in radians."""

import sympy


def sin(arguments: list[sympy.Expr]) -> sympy.Expr:
    """SIN(angle), with the angle in radians."""
    if len(arguments) != 1:
        raise ValueError("SIN requires exactly one argument.")

    return sympy.sin(arguments[0])
