"""Sample a random number when a function call is converted for solving."""

import random

import sympy


def rand(arguments: list[sympy.Expr]) -> sympy.Expr:
    """RAND() returns a uniformly sampled value in [0, 1)."""
    if arguments:
        raise ValueError("RAND requires no arguments.")

    # Preserve the sample exactly so symbolic solving cannot round it to 1.
    return sympy.Rational(random.random())
