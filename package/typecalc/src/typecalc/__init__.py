"""Equation parsing, mathematical functions, and solving.

Use solve with a sequence of equation strings to get JSON-ready variable
values. Document formats and prose belong to typecalc.text.
"""

from .ast.equation import Equation
from .ast.expressions import BinaryOperation, Expression, FunctionCall, Number, Symbol
from .solver import solve

__all__ = [
    "BinaryOperation",
    "Equation",
    "Expression",
    "FunctionCall",
    "Number",
    "Symbol",
    "solve",
]
