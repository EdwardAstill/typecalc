"""Calculate the dot product of two vectors."""

import sympy

from ..arrays import SymbolicValue, binary_operation, shape


def dot(left: SymbolicValue, right: SymbolicValue) -> sympy.Expr:
    if len(shape(left)) != 1 or len(shape(right)) != 1:
        raise ValueError("DOT requires two vectors.")
    return binary_operation("@", left, right)
