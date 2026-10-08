"""Calculate an angle from its y and x components."""

import sympy


def atan2(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ATAN2(y, x) returns an angle in (-pi, pi], accounting for the quadrant."""
    if len(arguments) != 2:
        raise ValueError("ATAN2 requires y and x arguments, in that order.")

    y, x = arguments
    if y == 0 and x == 0:
        raise ValueError("ATAN2 is undefined when both arguments are zero.")

    return sympy.atan2(y, x)
