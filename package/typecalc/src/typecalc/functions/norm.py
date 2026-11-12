"""Calculate a vector's Euclidean norm."""

import sympy

from ..arrays import SymbolicValue, shape


def norm(value: SymbolicValue) -> sympy.Expr:
    if len(shape(value)) != 1:
        raise ValueError("NORM requires a vector.")
    return sympy.sqrt(sum(sympy.Abs(component) ** 2 for component in value))
