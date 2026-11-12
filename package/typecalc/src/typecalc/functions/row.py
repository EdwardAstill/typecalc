"""Convert a vector to a one-row matrix."""

import sympy

from ..arrays import SymbolicValue, shape


def row(value: SymbolicValue) -> sympy.ImmutableDenseNDimArray:
    if len(shape(value)) != 1:
        raise ValueError("ROW requires a vector.")
    return value.reshape(1, len(value))
