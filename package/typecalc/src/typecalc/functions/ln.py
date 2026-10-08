"""Calculate a natural logarithm."""

import sympy


def ln(arguments: list[sympy.Expr]) -> sympy.Expr:
    """LN(value), for a positive value."""
    if len(arguments) != 1:
        raise ValueError("LN requires exactly one argument.")

    value = arguments[0]
    if value.is_positive is False:
        raise ValueError("LN requires a positive value.")

    return sympy.log(value)
