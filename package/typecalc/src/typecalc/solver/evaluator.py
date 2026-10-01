"""Evaluate function calls in engine equations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import isfinite

import sympy

from ..ast.equation import Equation
from ..ast.expressions import BinaryOperation, Expression, FunctionCall, Number, Symbol
from .sympy_variable_solver import _to_sympy


def _evaluate_expression(
    expression: Expression, values: dict[sympy.Symbol, sympy.Expr | float]
) -> Expression:
    """Copy an expression, replacing function calls with numeric results."""
    match expression:
        case Number(value=value):
            return Number(value)

        case Symbol(name=name):
            return Symbol(name)

        case BinaryOperation(left=left, operator=operator, right=right):
            return BinaryOperation(
                left=_evaluate_expression(left, values),
                operator=operator,
                right=_evaluate_expression(right, values),
            )

        case FunctionCall(name=name):
            # Compute functions symbolically before substituting values, so
            # DIFF(X^2, X) differentiates X^2 rather than a numeric constant.
            value = _to_sympy(expression, {}).subs(values)
            try:
                number = float(value)
            except (TypeError, OverflowError) as error:
                raise ValueError(
                    f"{name} result cannot be stored as a finite real number."
                ) from error

            if not isfinite(number):
                raise ValueError(
                    f"{name} result cannot be stored as a finite real number."
                )

            return Number(number)

        case _:
            raise ValueError(f"Unknown expression node: {expression!r}")


def evaluate_equations(
    equations: Sequence[Equation], values: Mapping[str, sympy.Expr | float]
) -> list[Equation]:
    """Return new equations with function calls replaced by numbers.

    ``values`` maps variable names to solved values, as returned by solve.
    Function calls are computed symbolically before substituting values, so
    DIFF(X^2, X) differentiates X^2 rather than a numeric constant. Results
    use floats, and no node is shared with the input equations.
    """
    symbols = {sympy.Symbol(name): value for name, value in values.items()}

    return [
        Equation(
            left=_evaluate_expression(equation.left, symbols),
            right=_evaluate_expression(equation.right, symbols),
        )
        for equation in equations
    ]
