"""Document containers for the block text format.

A Document is the parse result for text with ``EQUATIONS``/``TEXT`` blocks.
The engine only ever sees the Equations extracted from it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..ast.equation import Equation


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
class Document:
    """The parse result: a flat list of blocks in source order."""

    blocks: list[Block]
