from __future__ import annotations

from dataclasses import dataclass

from .expressions import Expression


@dataclass
class Equation:
    """An ``lhs = rhs`` statement; each side is an Expression tree."""

    left: Expression
    right: Expression
