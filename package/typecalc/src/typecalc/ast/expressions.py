"""Expression trees for equation sides.

Operations and function calls contain child expressions. Numbers and symbols
are leaves. The Expression union names all supported node types.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Number:
    """A literal numeric value, e.g. ``10`` or ``3.14``."""

    value: float


@dataclass
class Symbol:
    """A named variable, e.g. ``A`` in ``A + B = 10``."""

    name: str


@dataclass
class BinaryOperation:
    """
    An operation with two operands, e.g. ``A + B``.

    Nested operations encode precedence naturally: "A + B * 2" becomes
    BinaryOperation(+, A, BinaryOperation(*, B, 2)) because * binds tighter.
    """

    left: Expression
    operator: str  # one of "+", "-", "*", "/", "^"
    right: Expression


@dataclass
class FunctionCall:
    """A call to a named function with arguments, e.g. ``SOLVE(B)``."""

    name: str
    arguments: list[Expression]


type Expression = Number | Symbol | BinaryOperation | FunctionCall
