"""Calculate an angle from its y and x components."""

import sympy


def atan2(y: sympy.Expr, x: sympy.Expr) -> sympy.Expr:
    """ATAN2(y, x) returns an angle in (-pi, pi], accounting for the quadrant."""
    if y == 0 and x == 0:
        raise ValueError("ATAN2 is undefined when both arguments are zero.")

    return sympy.atan2(y, x)
