"""Solve equation strings for finite real values using SymPy."""

from collections.abc import Sequence
from math import isfinite

import sympy

from .ast import BinaryOperation, Equation, Expression, FunctionCall, Number, Symbol
from .functions import apply_function
from .parser import parse_equations


def solve(equations: Sequence[str]) -> dict[str, float]:
    """Solve equation strings and return finite real floats.

    Blank rows are ignored and input rows are unchanged. Invalid equations,
    unresolved variables, or multiple returned solutions raise ValueError.
    SymPy's symbolic solving limitations apply; unsupported systems can raise
    NotImplementedError. Exact values become floats only at this boundary.
    """
    values = _solve_equations(parse_equations(equations))
    result: dict[str, float] = {}
    for name, value in values.items():
        try:
            number = float(value)
        except (TypeError, OverflowError) as error:
            raise ValueError(
                f"Value for {name} cannot be stored as a finite real number."
            ) from error
        if not isfinite(number):
            raise ValueError(
                f"Value for {name} cannot be stored as a finite real number."
            )
        result[name] = number
    return result


def _to_sympy(
    expression: Expression, variables: dict[str, sympy.Symbol]
) -> sympy.Expr:
    """Convert an expression, recording its global variables."""
    match expression:
        case Number(value=value):
            return sympy.Rational(value)
        case Symbol(name=name):
            return variables.setdefault(name, sympy.Symbol(name, real=True))
        case BinaryOperation(left=left, operator=operator, right=right):
            left = _to_sympy(left, variables)
            right = _to_sympy(right, variables)
            match operator:
                case "+":
                    return left + right
                case "-":
                    return left - right
                case "*":
                    return left * right
                case "/":
                    if right == 0:
                        raise ValueError("Division by zero in an equation.")
                    return left / right
                case "^":
                    return left ** right
                case _:
                    raise ValueError(f"Unsupported operator: {operator!r}")
        case FunctionCall(name=name, arguments=arguments):
            # Calculus can eliminate local variables, so retain only those
            # still present in the result, e.g. DIFF(X^2 | X=10) needs no X.
            local_variables: dict[str, sympy.Symbol] = {}
            converted = [_to_sympy(argument, local_variables) for argument in arguments]
            result = apply_function(name, converted)
            for symbol in sorted(result.free_symbols, key=str):
                variables.setdefault(symbol.name, symbol)
            return result
        case _:
            raise ValueError(f"Unknown expression node: {expression!r}")


def _solve_equations(equations: Sequence[Equation]) -> dict[str, sympy.Expr]:
    """Delegate symbolic solving to SymPy and retain exact numeric results."""
    variables: dict[str, sympy.Symbol] = {}
    constraints: list[sympy.Expr] = []
    for equation in equations:
        constraint = _to_sympy(equation.left, variables) - _to_sympy(
            equation.right, variables
        )
        # Discard identities while retaining variables mentioned in them.
        if sympy.simplify(constraint) != 0:
            constraints.append(constraint)

    solution = {}
    if constraints:
        solutions = sympy.solve(constraints, list(variables.values()), dict=True)
        if not solutions:
            raise ValueError("Equations have no solution.")
        if len(solutions) != 1:
            raise ValueError("Equations have multiple solutions.")
        solution = solutions[0]

    unresolved = [
        name for name, symbol in variables.items()
        if symbol not in solution or solution[symbol].free_symbols
    ]
    if unresolved:
        raise ValueError(f"Variables are not fully determined: {', '.join(sorted(unresolved))}")
    if any(value.is_finite is False for value in solution.values()):
        raise ValueError("Equations have no solution with finite variable values.")
    return {name: solution[symbol] for name, symbol in variables.items()}
