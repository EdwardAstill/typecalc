"""Return the exact mathematical constant pi."""

import sympy


def pi(arguments: list[sympy.Expr]) -> sympy.Expr:
    """PI() returns pi without introducing a variable."""
    if arguments:
        raise ValueError("PI requires no arguments.")

    return sympy.pi
