import re

# One "token" = optional leading whitespace, then a number, a name, or a single
# operator/punctuation character.
TOKEN_PATTERN = re.compile(
    r"""
    \s*
    (
        \d+(?:\.\d+)?     # number: "10", "3.14"
        |[A-Za-z_]\w*     # name: variable or function, e.g. "A", "SOLVE"
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
