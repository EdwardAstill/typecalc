"""Solve engine equations for their variable values with SymPy."""

from __future__ import annotations

from collections.abc import Sequence

import sympy

from ..ast.equation import Equation
from ..ast.expressions import BinaryOperation, Expression, FunctionCall, Number, Symbol
from ..functions import apply_function


def _to_sympy(
    expression: Expression, variables: dict[str, sympy.Symbol]
) -> sympy.Expr:
    """Convert an expression, recording symbols before any simplification."""
    match expression:
        case Number(value=value):
            return sympy.Rational(str(value))

        case Symbol(name=name):
            return variables.setdefault(name, sympy.Symbol(name))
        

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
