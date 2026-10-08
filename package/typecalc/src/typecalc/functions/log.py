"""Calculate a logarithm with an explicit base."""

import sympy


def log(arguments: list[sympy.Expr]) -> sympy.Expr:
    """LOG(value, base), with positive inputs and a base other than one."""
    if len(arguments) != 2:
        raise ValueError("LOG requires a value and a base.")

    value, base = arguments
    if value.is_positive is False:
        raise ValueError("LOG requires a positive value.")
    if base.is_positive is False or base == 1:
        raise ValueError("LOG base must be positive and different from 1.")

    return sympy.log(value, base)
