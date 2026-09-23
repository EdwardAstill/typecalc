from __future__ import annotations

from dataclasses import dataclass

from .expressions import Expression


@dataclass
class EquationBlock:
    """A section starting with an ``EQUATIONS`` header, holding one Equation per line."""

    equations: list[Equation]


@dataclass
class TextBlock:
    """A section starting with a ``TEXT`` header, holding its remaining lines verbatim."""

    text: str


type Block = EquationBlock | TextBlock


@dataclass
class Equation:
    """An ``lhs = rhs`` statement; each side is an Expression tree."""

    left: Expression
    right: Expression


@dataclass
class Document:
    """The parse result: a flat list of blocks in source order."""

    blocks: list[Block]
