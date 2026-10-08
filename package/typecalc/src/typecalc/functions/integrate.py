"""Integrate an expression over a definite interval."""

import sympy


def integrate(
    expression: sympy.Expr, variable: sympy.Expr, lower: sympy.Expr, upper: sympy.Expr
) -> sympy.Expr:
    """INTEGRATE(expression, variable, lower, upper)."""
    if not isinstance(variable, sympy.Symbol):
        raise ValueError("INTEGRATE variable must be a symbol.")

    return sympy.integrate(expression, (variable, lower, upper))
