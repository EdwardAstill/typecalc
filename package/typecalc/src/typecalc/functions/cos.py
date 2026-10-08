"""Calculate the cosine of an angle in radians."""

import sympy


def cos(arguments: list[sympy.Expr]) -> sympy.Expr:
    """COS(angle), with the angle in radians."""
    if len(arguments) != 1:
        raise ValueError("COS requires exactly one argument.")

    return sympy.cos(arguments[0])
