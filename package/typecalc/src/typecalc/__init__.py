"""Equation parsing, mathematical functions, and solving.

Use solve with a sequence of equation strings to get JSON-ready variable
values: finite real floats, lists of floats (vectors), or nested lists of
floats (matrices).
"""

from .solver import solve

__all__ = ["solve"]
