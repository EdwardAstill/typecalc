"""One- and two-dimensional values with explicit, non-broadcasting operations."""

from math import prod

import sympy

from .ast import ArrayLiteral, BinaryOperation, Equation, Expression, FunctionCall, Number, Symbol


type Shape = tuple[int, ...]
type SymbolicValue = sympy.Expr | sympy.ImmutableDenseNDimArray


def shape(value: SymbolicValue) -> Shape:
    return value.shape if isinstance(value, sympy.NDimArray) else ()


def elements(value: SymbolicValue) -> list[sympy.Expr]:
    return list(value.reshape(prod(value.shape))) if shape(value) else [value]


def literal_shape(expression: ArrayLiteral) -> Shape:
    if not expression.elements:
        raise ValueError("Arrays cannot be empty.")
    children = [literal_shape(item) if isinstance(item, ArrayLiteral) else ()
                for item in expression.elements]
    if any(child != children[0] for child in children) or len(children[0]) > 1:
        raise ValueError("Arrays must be vectors or rectangular matrices.")
    return (len(children), *children[0])


def operation_shape(operator: str, left: Shape, right: Shape) -> Shape:
    if operator in ("+", "-"):
        if left != right:
            raise ValueError(f"{operator} requires identical shapes, got {left} and {right}.")
        return left
    if operator == "*":
        if left and right and left != right:
            raise ValueError(f"Elementwise multiplication requires identical shapes, got {left} and {right}.")
        return left or right
    if operator == "/":
        if right:
            raise ValueError("Division requires a scalar denominator.")
        return left
    if operator == "^":
        if left or right:
            raise ValueError("Powers require scalar operands.")
        return ()
    if operator == "@":
        if not left or not right:
            raise ValueError("@ requires vectors or matrices; define unknown components explicitly, e.g. v = [x, y].")
        if left[-1] != right[0]:
            raise ValueError(f"Incompatible shapes for @: {left} and {right}.")
        return left[:-1] + right[1:]
    raise ValueError(f"Unsupported operator: {operator!r}")


def binary_operation(operator: str, left: SymbolicValue, right: SymbolicValue) -> SymbolicValue:
    result_shape = operation_shape(operator, shape(left), shape(right))
    match operator:
        case "+":
            return left + right
        case "-":
            return left - right
        case "*":
            if shape(left) and shape(right):
                return sympy.Array([a * b for a, b in zip(elements(left), elements(right))], result_shape)
            return left * right
        case "/":
            if right == 0:
                raise ValueError("Division by zero in an equation.")
            return left / right
        case "^":
            return left ** right
        case "@":
            a = sympy.Matrix(left.tolist())
            b = sympy.Matrix(right.tolist())
            if len(shape(left)) == 1:
                a = a.T
            result = a * b
            if not result_shape:
                return result[0]
            return sympy.Array(list(result), result_shape)


def _expression_shape(expression: Expression, known: dict[str, Shape]) -> Shape | None:
    match expression:
        case Number():
            return ()
        case Symbol(name=name):
            return known.get(name)
        case ArrayLiteral():
            return literal_shape(expression)
        case BinaryOperation(left=left, operator=operator, right=right):
            a, b = _expression_shape(left, known), _expression_shape(right, known)
            if a is not None and b is not None:
                return operation_shape(operator, a, b)
            if operator in ("+", "-"):
                return a if a is not None else b
            if operator == "*":
                return a or b or None
            if operator == "/":
                return a
            if operator == "^":
                return ()
            return None
        case FunctionCall(name=name, arguments=arguments):
            name = name.upper()
            if name not in ("ROW", "COL", "TRANSPOSE"):
                return ()
            if len(arguments) != 1:
                return None  # Argument counts are checked by the function registry.
            source = _expression_shape(arguments[0], known)
            if source is None:
                return None
            if name == "TRANSPOSE" and source:
                return source[::-1]
            if name in ("ROW", "COL") and len(source) == 1:
                return (1, source[0]) if name == "ROW" else (source[0], 1)
            raise ValueError(f"Invalid shape for {name}: {source}.")
    raise ValueError(f"Unknown expression node: {expression!r}")


def array_symbols(equations: list[Equation]) -> dict[str, sympy.ImmutableDenseNDimArray]:
    # shortcut: infer named shapes only from whole-side equations; extend for implicit array unknowns.
    known: dict[str, Shape] = {}
    changed = True
    while changed:
        changed = False
        for equation in equations:
            for target, source in ((equation.left, equation.right), (equation.right, equation.left)):
                if not isinstance(target, Symbol):
                    continue
                inferred = _expression_shape(source, known)
                if inferred is None:
                    continue
                if target.name in known:
                    if known[target.name] != inferred:
                        raise ValueError(f"Conflicting shapes for {target.name}: {known[target.name]} and {inferred}.")
                else:
                    known[target.name] = inferred
                    changed = True
    return {
        name: sympy.Array([sympy.Dummy(f"{name}_{i}", real=True) for i in range(prod(dimensions))], dimensions)
        for name, dimensions in known.items() if dimensions
    }

