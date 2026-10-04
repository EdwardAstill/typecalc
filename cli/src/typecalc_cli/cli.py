"""Solve equations from a file or literal text and print variable values."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from typecalc import solve


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="typecalc", description="Solve a file or text containing one equation per line."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("file", nargs="?", type=Path, help="UTF-8 equation file to solve")
    source.add_argument("--text", help="literal equations to solve, separated by newlines")
    args = parser.parse_args(argv)

    try:
        content = args.text if args.text is not None else args.file.read_text(encoding="utf-8")
        equations = content.splitlines()
        values = solve(equations)
    except (OSError, ValueError, NotImplementedError) as error:
        print(f"typecalc: {error}", file=sys.stderr)
        return 1

    for name, value in sorted(values.items()):
        print(f"{name} = {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
