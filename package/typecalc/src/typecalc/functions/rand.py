"""Sample a random number when a function call is converted for solving."""

import random

import sympy


def rand() -> sympy.Expr:
    """RAND() returns a uniformly sampled value in [0, 1)."""
    # Preserve the sample exactly so symbolic solving cannot round it to 1.
    return sympy.Rational(random.random())
