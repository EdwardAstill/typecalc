"""Calculate a natural logarithm."""

import sympy


def ln(value: sympy.Expr) -> sympy.Expr:
    """LN(value), for a positive value."""
    if value.is_positive is False:
        raise ValueError("LN requires a positive value.")

    return sympy.log(value)
