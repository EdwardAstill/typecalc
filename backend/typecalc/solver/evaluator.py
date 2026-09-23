"""Evaluate function calls while preserving the rest of a document AST."""

from __future__ import annotations

from math import isfinite

import sympy

from ..ast.document import Block, Document, Equation, EquationBlock, TextBlock
from ..ast.expressions import BinaryOperation, Expression, FunctionCall, Number, Symbol
from .sympy_variable_solver import _to_sympy, solve_variables


def _evaluate_expression(
    expression: Expression, values: dict[sympy.Symbol, sympy.Expr]
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


def evaluate_document(document: Document) -> Document:
    """Return a new document AST with function calls replaced by values.

    Solve the variables once, then evaluate calls on either side of each
    equation. Other expressions and all text retain their original structure.
    No mutable nodes are shared with the input document.

    Results use the existing Number node's float representation. Fractions
    and roots may be approximate; results that cannot fit a finite real
    float raise ValueError. Errors from solve_variables propagate unchanged.
    """
    variables = solve_variables(document)
    values = {sympy.Symbol(name): value for name, value in variables.items()}
    blocks: list[Block] = []

    for block in document.blocks:
        match block:
            case TextBlock(text=text):
                blocks.append(TextBlock(text))

            case EquationBlock(equations=equations):
                blocks.append(EquationBlock([
                    Equation(
                        left=_evaluate_expression(equation.left, values),
                        right=_evaluate_expression(equation.right, values),
                    )
                    for equation in equations
                ]))

            case _:
                raise ValueError(f"Unknown document block: {block!r}")

    return Document(blocks)
