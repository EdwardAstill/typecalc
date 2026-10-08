"""Solve equation strings for finite real values using SymPy."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite

import sympy

from .ast import BinaryOperation, Equation, Expression, FunctionCall, Number, Symbol
from .functions import apply_function
from .parser import parse_equations


def solve(equations: Sequence[str]) -> dict[str, float]:
    """Solve equation strings and return every variable as a finite real float.

    Blank strings are ignored; parse errors identify the 1-based input line.
    Each call is independent and leaves the input unchanged. Every nonblank
    row must be an equation. SOLVE markers are optional.

    Raise ValueError for malformed equations, inconsistent or ambiguous
    systems, unresolved variables, or values outside the finite real float
    range. Incorrect input types raise TypeError. SymPy's NotImplementedError
    propagates when it cannot solve a system. Fractions and roots may be
    approximate; successful results can be serialized with json.dumps.
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
    """Convert an expression, recording symbols before any simplification."""
    match expression:
        case Number(value=value):
            return sympy.Rational(str(value))

        case Symbol(name=name):
            # The public solver returns real values; ABS also needs this
            # assumption to solve and differentiate symbolic arguments.
            return variables.setdefault(name, sympy.Symbol(name, real=True))


        case BinaryOperation(left=left, operator=operator, right=right):

            #if it is a binary operation do recursion
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

        case FunctionCall(name="SOLVE", arguments=[argument]):
            # SOLVE denotes the same expression as its argument.
            return _to_sympy(argument, variables)

        case FunctionCall(name="SOLVE"):
            raise ValueError("SOLVE requires exactly one argument.")

        case FunctionCall(name=name, arguments=arguments):
            # Function-local symbols may disappear after evaluation, such as
            # X in DIFF(X^2 | X=10). Only remaining symbols need global values.
            local_variables: dict[str, sympy.Symbol] = {}
            converted = [_to_sympy(argument, local_variables) for argument in arguments]
            result = apply_function(name, converted)
            for symbol in sorted(result.free_symbols, key=str):
                variables.setdefault(symbol.name, symbol)
            return result

        case _:
            raise ValueError(f"Unknown expression node: {expression!r}")


def _solve_equations(equations: Sequence[Equation]) -> dict[str, sympy.Expr]:
    """Return the equations' uniquely determined variable values.

    SOLVE(expression) contributes the same constraint as expression, so
    B = SOLVE(B) becomes the identity B = B.

    Values remain SymPy numbers, preserving fractions and exact roots.
    Raise ValueError for inconsistent equations, unresolved variables, or
    multiple solutions. SymPy's NotImplementedError is allowed through when
    it cannot solve a system; that does not mean the system has no solution.
    """
    variables: dict[str, sympy.Symbol] = {}
    constraints: list[sympy.Expr] = []

    for equation in equations:
        left = _to_sympy(equation.left, variables)
        right = _to_sympy(equation.right, variables)
        constraint = left - right

        # Identities add no information. Keep the original expression
        # for SymPy's solve checks when it is a real constraint.
        if sympy.simplify(constraint) != 0:
            constraints.append(constraint)

    if constraints:
        solutions = sympy.solve(constraints, list(variables.values()), dict=True)

        if not solutions:
            raise ValueError("Equations have no solution.")

        if len(solutions) != 1:
            raise ValueError("Equations have multiple solutions.")

        solution = solutions[0]
    else:
        # No constraints: any mentioned variables are still unresolved.
        solution = {}

    unresolved = [
        name
        for name, symbol in variables.items()
        if symbol not in solution or solution[symbol].free_symbols
    ]
    if unresolved:
        raise ValueError(
            f"Variables are not fully determined: {', '.join(sorted(unresolved))}"
        )

    if any(value.is_finite is False for value in solution.values()):
        raise ValueError("Equations have no solution with finite variable values.")

    return {name: solution[symbol] for name, symbol in variables.items()}
