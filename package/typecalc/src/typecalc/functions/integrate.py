"""Integrate an expression over a definite interval."""

import sympy


def integrate(arguments: list[sympy.Expr]) -> sympy.Expr:
    """INTEGRATE(expression, variable, lower, upper)."""
    if len(arguments) != 4:
        raise ValueError(
            "INTEGRATE requires an expression, a variable, and lower and upper bounds."
        )

    expression, variable, lower, upper = arguments
    if not isinstance(variable, sympy.Symbol):
        raise ValueError("INTEGRATE variable must be a symbol.")

    return sympy.integrate(expression, (variable, lower, upper))
