"""Calculate the exponential with base e."""

import sympy


def exp(arguments: list[sympy.Expr]) -> sympy.Expr:
    """EXP(value) returns e raised to the given value."""
    if len(arguments) != 1:
        raise ValueError("EXP requires exactly one argument.")

    return sympy.exp(arguments[0])
