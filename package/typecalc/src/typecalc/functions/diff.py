"""Differentiate an expression, optionally evaluating it at a point."""

import sympy


def diff(
    expression: sympy.Expr, variable: sympy.Expr, point: sympy.Expr | None = None
) -> sympy.Expr:
    """DIFF(expression, variable[, point]); nest calls for higher derivatives."""
    if not isinstance(variable, sympy.Symbol):
        raise ValueError("DIFF variable must be a symbol.")

    result = sympy.diff(expression, variable)
    if point is not None:
        # Differentiate before substituting the evaluation point.
        result = result.subs(variable, point)

    return result
