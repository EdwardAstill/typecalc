"""Tokenize and parse equation strings into expression trees."""

from __future__ import annotations

from collections.abc import Sequence
import re

from .ast import BinaryOperation, Equation, Expression, FunctionCall, Number, Symbol

__all__ = ["parse_equation", "parse_equations", "parse_expression"]


# One "token" = optional leading whitespace, then a number, a name, or a single
# operator/punctuation character.
TOKEN_PATTERN = re.compile(
    r"""
    \s*
    (
        \d+(?:\.\d+)?     # number: "10", "3.14"
        |[A-Za-z_]\w*     # name: variable or function, e.g. "A", "SIN"
        |[+\-*/^(),=|]    # operators, parentheses, comma, equals, condition bar
    )
    """,
    re.VERBOSE,
)


def tokenize(source: str) -> list[str]:
    """Split source text into token strings, e.g. "A + B*2" -> ["A", "+", "B", "*", "2"]."""
    tokens = TOKEN_PATTERN.findall(source)

    # findall silently skips anything the pattern doesn't match, so a typo like
    # "A $ B" would vanish. Strip out everything matched; anything left over is
    # an unknown character -> reject instead of parsing a wrong expression.
    leftover = TOKEN_PATTERN.sub("", source).strip()
    if leftover:
        raise ValueError(f"Unexpected character(s): {leftover!r}")

    return tokens


# Recursive-descent parser that turns a token list into an Expression tree.
#
# Precedence is encoded in the call chain (lowest binds loosest, so it is
# outermost): parse_addition -> parse_multiplication -> parse_unary ->
# parse_power -> parse_primary. Each level consumes its operators and delegates to
# the next-higher-precedence level for its operands, which is what makes
# "A + B * 2" parse as  A + (B * 2)  instead of (A + B) * 2.
NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")
NAME_PATTERN = re.compile(r"[A-Za-z_]\w*")


class ExpressionParser:
    """
    A cursor over a token list.

    `position` is the index of the next token to read; `current()` peeks at it,
    `consume()` takes it and advances. Parse methods only ever look at
    tokens at or after `position`, never rewind.
    """

    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.position = 0

    def current(self) -> str | None:
        """Peek at the next token without consuming it; None at end of input."""
        if self.position >= len(self.tokens):
            return None

        return self.tokens[self.position]

    def consume(self) -> str:
        """Take the next token and advance; error at end of input."""
        token = self.current()

        if token is None:
            raise ValueError("Unexpected end of expression")

        self.position += 1
        return token

    def parse(self) -> Expression:
        """Parse a complete expression and require that all tokens were used."""
        expression = self.parse_addition()

        if self.current() is not None:
            raise ValueError(
                f"Unexpected token: {self.current()}"
            )

        return expression

    def parse_addition(self) -> Expression:
        """Lowest precedence: left-associative + and -."""
        left = self.parse_multiplication()

        while self.current() in ("+", "-"):
            operator = self.consume()
            right = self.parse_multiplication()

            left = BinaryOperation(
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_multiplication(self) -> Expression:
        """Middle precedence: left-associative * and /."""
        left = self.parse_unary()

        while self.current() in ("*", "/"):
            operator = self.consume()
            right = self.parse_unary()

            left = BinaryOperation(
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_unary(self) -> Expression:
        """Unary signs: -X^2 means -(X^2), and powers can have signed exponents."""
        if self.current() in ("+", "-"):
            operator = self.consume()
            expression = self.parse_unary()
            if operator == "-":
                return BinaryOperation(Number("0"), "-", expression)
            return expression

        return self.parse_power()

    def parse_power(self) -> Expression:
        """Highest binary precedence: ^ is right-associative, so 2^3^2 = 2^(3^2)."""
        left = self.parse_primary()

        if self.current() == "^":
            operator = self.consume()
            right = self.parse_unary()

            return BinaryOperation(
                left=left,
                operator=operator,
                right=right
            )

        return left

    def parse_primary(self) -> Expression:
        """Atoms: numbers, parenthesized sub-expressions, symbols, function calls."""
        token = self.consume()

        # Leaf: a numeric literal like "3" or "3.14"
        if NUMBER_PATTERN.fullmatch(token):
            return Number(token)

        # "(" starts a grouped sub-expression; recurse back to the lowest
        # level so the group is parsed as its own full expression.
        if token == "(":
            expression = self.parse_addition()

            if self.consume() != ")":
                raise ValueError("Expected ')'")

            return expression

        if NAME_PATTERN.fullmatch(token):
            if self.current() == "(":
                return self.parse_function_call(token)
            return Symbol(token)

        raise ValueError(f"Unexpected token: {token}")

    def parse_function_call(self, name: str) -> FunctionCall:
        """Parse ordinary arguments and the DIFF evaluation-point shorthand."""
        self.consume()  # (
        arguments: list[Expression] = []
        if self.current() != ")":
            while True:
                arguments.append(self.parse_addition())
                if self.current() == "|":
                    if name.upper() != "DIFF" or len(arguments) != 1:
                        raise ValueError("Expected DIFF(expression | variable=point)")
                    self.consume()
                    variable = self.consume()
                    if not NAME_PATTERN.fullmatch(variable):
                        raise ValueError("DIFF variable must be a symbol.")
                    if self.consume() != "=":
                        raise ValueError("Expected '=' in DIFF evaluation point.")
                    arguments.extend([Symbol(variable), self.parse_addition()])
                    break
                if self.current() != ",":
                    break
                self.consume()
        if self.consume() != ")":
            raise ValueError("Expected ')'")
        return FunctionCall(name, arguments)


def parse_expression(source: str) -> Expression:
    """Tokenize source and parse it into a single Expression tree."""
    return ExpressionParser(tokenize(source)).parse()


def parse_equation(source: str) -> Equation:
    """Parse one outer equality, allowing evaluation points inside calls."""
    parser = ExpressionParser(tokenize(source))
    left = parser.parse_addition()

    if parser.current() != "=":
        raise ValueError("Equation must contain exactly one top-level '='")
    parser.consume()
    right = parser.parse_addition()

    if parser.current() == "=":
        raise ValueError("Equation must contain exactly one top-level '='")
    if parser.current() is not None:
        raise ValueError(f"Unexpected token: {parser.current()}")

    return Equation(left=left, right=right)


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
