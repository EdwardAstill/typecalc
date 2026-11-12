"""Transpose a matrix while preserving one-dimensional vectors."""

from ..arrays import SymbolicValue, shape


def transpose(value: SymbolicValue) -> SymbolicValue:
    if not shape(value):
        raise ValueError("TRANSPOSE requires a vector or matrix.")
    if len(shape(value)) == 1:
        return value
    return value.transpose()
