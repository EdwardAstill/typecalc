"""Document-level solving built on the engine."""

from __future__ import annotations

import sympy

from ..ast.equation import Equation
from ..solver.sympy_variable_solver import _solve_equations
from .document import Document, EquationBlock


def document_equations(document: Document) -> list[Equation]:
    """Return every equation in the document, in block order."""
    return [
        equation
        for block in document.blocks
        if isinstance(block, EquationBlock)
        for equation in block.equations
    ]


def solve_document(document: Document) -> dict[str, sympy.Expr]:
    """Return the document's uniquely determined variable values."""
    return _solve_equations(document_equations(document))
