"""Equation parsing for the engine, independent of document formats."""

from __future__ import annotations

from collections.abc import Sequence

from ..ast.equation import Equation
from .expression_parser import parse_equation, parse_expression

__all__ = ["parse_equation", "parse_equations", "parse_expression"]


def parse_equations(equations: Sequence[str]) -> list[Equation]:
    """Parse equation strings into engine Equation objects.

    Blank strings are skipped. Raises ValueError naming the 1-based line
    for any equation that fails to parse.
    """
    if isinstance(equations, (str, bytes)):
        raise TypeError("Expected a sequence of equation strings, not a single string.")

    parsed: list[Equation] = []

    for number, source in enumerate(equations, start=1):
        if not isinstance(source, str):
            raise TypeError(f"Line {number}: equation must be a string.")
        if not source.strip():
            continue

        try:
            parsed.append(parse_equation(source))
        except ValueError as error:
            raise ValueError(f"Line {number}: {error}") from error

    return parsed
