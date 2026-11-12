"""Solve equation strings for finite real values using SymPy."""

from collections.abc import Sequence
from math import isfinite

import sympy

from .arrays import SymbolicValue, array_symbols, binary_operation, elements, literal_shape, shape
from .ast import ArrayLiteral, BinaryOperation, Equation, Expression, FunctionCall, Number, Symbol
from .functions import apply_function
from .parser import parse_equations


type Value = float | list[float] | list[list[float]]


def solve(equations: Sequence[str]) -> dict[str, Value]:
    """Solve equations and return finite real floats, vectors, or matrices.

    Blank rows are ignored and input rows are unchanged. Invalid equations,
    unresolved variables, or multiple returned solutions raise ValueError.
    SymPy's symbolic solving limitations apply; unsupported systems can raise
    NotImplementedError. Exact values become floats only at this boundary.
    """
    values = _solve_equations(parse_equations(equations))
    return {name: _numeric_value(value, name) for name, value in values.items()}


def _numeric_value(value: SymbolicValue | list, name: str) -> Value:
    if isinstance(value, sympy.NDimArray):
        value = value.tolist()
    if isinstance(value, list):
        return [_numeric_value(item, name) for item in value]
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
    return number


def _to_sympy(
    expression: Expression,
    variables: dict[str, SymbolicValue],
    arrays: dict[str, sympy.ImmutableDenseNDimArray],
    bindings: dict[str, sympy.Dummy],
) -> SymbolicValue:
    """Convert with lexical scalar bindings, collecting only global symbols or symbol arrays."""
    match expression:
        case Number(value=value):
            return sympy.Rational(value)
        case Symbol(name=name):
            if name in bindings:
                return bindings[name]
            value = arrays[name] if name in arrays else sympy.Symbol(name, real=True)
            variables[name] = value
            return value
        case ArrayLiteral(elements=items):
            dimensions = literal_shape(expression)
            converted = [_to_sympy(item, variables, arrays, bindings) for item in items]
            if any(shape(item) != dimensions[1:] for item in converted):
                raise ValueError("Array literal entries must be scalars, or literal rows of scalars.")
            return sympy.Array([entry for item in converted for entry in elements(item)], dimensions)
        case BinaryOperation(left=left, operator=operator, right=right):
            return binary_operation(
                operator, _to_sympy(left, variables, arrays, bindings),
                _to_sympy(right, variables, arrays, bindings),
            )
        case FunctionCall(name=name, arguments=arguments):
            # Calculus can eliminate local variables, so retain only those
            # still present in the result, e.g. DIFF(X^2 | X=10) needs no X.
            local_variables: dict[str, SymbolicValue] = {}
            body_bindings = bindings
            if (
                (name.upper() == "DIFF" and len(arguments) == 3)
                or (name.upper() == "INTEGRATE" and len(arguments) == 4)
            ) and isinstance(arguments[1], Symbol):
                variable = arguments[1].name
                body_bindings = {**bindings, variable: sympy.Dummy(variable, real=True)}
            # Only the body and variable are bound; points and bounds use the enclosing scope.
            converted = [
                _to_sympy(argument, local_variables, arrays, body_bindings if index < 2 else bindings)
                for index, argument in enumerate(arguments)
            ]
            result = apply_function(name, converted)
            for variable, value in local_variables.items():
                if value.free_symbols & result.free_symbols:
                    variables[variable] = value
            return result
        case _:
            raise ValueError(f"Unknown expression node: {expression!r}")


def _solve_equations(equations: list[Equation]) -> dict[str, SymbolicValue]:
    """Expand array constraints and delegate exact scalar solving to SymPy."""
    arrays = array_symbols(equations)
    variables: dict[str, SymbolicValue] = {}
    constraints: list[sympy.Expr] = []
    for equation in equations:
        difference = binary_operation(
            "-", _to_sympy(equation.left, variables, arrays, {}),
            _to_sympy(equation.right, variables, arrays, {}),
        )
        for constraint in elements(difference):
            # Discard identities while retaining variables mentioned in them.
            if sympy.simplify(constraint) != 0:
                constraints.append(constraint)

    solution = {}
    if constraints:
        symbols = [symbol for value in variables.values() for symbol in elements(value)]
        solutions = sympy.solve(constraints, symbols, dict=True)
        if not solutions:
            raise ValueError("Equations have no solution.")
        if len(solutions) != 1:
            raise ValueError("Equations have multiple solutions.")
        solution = solutions[0]

    unresolved = [
        name for name, value in variables.items()
        if any(symbol not in solution or solution[symbol].free_symbols for symbol in elements(value))
    ]
    if unresolved:
        raise ValueError(f"Variables are not fully determined: {', '.join(sorted(unresolved))}")
    if any(value.is_finite is False for value in solution.values()):
        raise ValueError("Equations have no solution with finite variable values.")
    return {name: value.xreplace(solution) for name, value in variables.items()}
