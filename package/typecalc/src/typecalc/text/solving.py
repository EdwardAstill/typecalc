"""Document-level solving and evaluation built on the engine."""

from __future__ import annotations

import sympy

from ..ast.equation import Equation
from ..solver.evaluator import evaluate_equations
from ..solver.sympy_variable_solver import _solve_equations
from .document import Block, Document, EquationBlock, TextBlock


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


def evaluate_document(document: Document) -> Document:
    """Return a new document AST with function calls replaced by values.

    Solve the variables once, then evaluate calls on either side of each
    equation. Surrounding expressions, block order, and text are preserved;
    the input AST is unchanged.
    """
    equations = document_equations(document)
    evaluated = evaluate_equations(equations, _solve_equations(equations))
    blocks: list[Block] = []
    index = 0

    for block in document.blocks:
        match block:
            case TextBlock(text=text):
                blocks.append(TextBlock(text))

            case EquationBlock(equations=block_equations):
                blocks.append(
                    EquationBlock(evaluated[index : index + len(block_equations)])
                )
                index += len(block_equations)

            case _:
                raise ValueError(f"Unknown document block: {block!r}")

    return Document(blocks)
