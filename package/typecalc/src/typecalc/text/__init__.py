"""Document conversion built on the engine's equation parser and solver."""

from .document import Block, Document, EquationBlock, TextBlock
from .document_parser import parse_document
from .solving import evaluate_document, solve_document

__all__ = [
    "Block",
    "Document",
    "EquationBlock",
    "TextBlock",
    "evaluate_document",
    "parse_document",
    "solve_document",
]
