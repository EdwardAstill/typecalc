"""Convert a vector to a one-column matrix."""

import sympy

from ..arrays import SymbolicValue, shape


def col(value: SymbolicValue) -> sympy.ImmutableDenseNDimArray:
    if len(shape(value)) != 1:
        raise ValueError("COL requires a vector.")
    return value.reshape(len(value), 1)
