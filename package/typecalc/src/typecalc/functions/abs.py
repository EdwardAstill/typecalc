"""Calculate the absolute value of an expression."""

import sympy


def abs(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ABS(value) returns its nonnegative magnitude."""
    if len(arguments) != 1:
        raise ValueError("ABS requires exactly one argument.")

    return sympy.Abs(arguments[0])
