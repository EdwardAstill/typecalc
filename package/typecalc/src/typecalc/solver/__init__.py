"""Public string-equation solver."""

from collections.abc import Sequence
from math import isfinite

from ..parser import parse_equations
from .sympy_variable_solver import _solve_equations


def solve(equations: Sequence[str]) -> dict[str, float]:
    """Solve equation strings and return every variable as a finite real float.

    Blank strings are ignored; parse errors identify the 1-based input line.
    Each call is independent and leaves the input unchanged. SOLVE markers
    and document headers are not required.

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
