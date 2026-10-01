"""Differentiate an expression, optionally evaluating it at a point."""

import sympy


def diff(arguments: list[sympy.Expr]) -> sympy.Expr:
    """DIFF(expression, variable[, point]); nest calls for higher derivatives."""
    if len(arguments) not in (2, 3):
        raise ValueError(
            "DIFF requires an expression and a variable, with an optional point."
        )

    expression, variable = arguments[:2]
    if not isinstance(variable, sympy.Symbol):
        raise ValueError("DIFF variable must be a symbol.")

    result = sympy.diff(expression, variable)
    if len(arguments) == 3:
        # Differentiate before substituting the evaluation point.
        result = result.subs(variable, arguments[2])

    return result
