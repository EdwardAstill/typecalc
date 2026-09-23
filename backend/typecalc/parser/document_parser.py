# Block-level document parser.
#
# A document is a sequence of blocks separated by blank lines. Each block
# starts with a header line ("EQUATIONS" or "TEXT"); the remaining lines are
# the block's content.

import re

from ..ast.document import Block, Document, EquationBlock, TextBlock
from .expression_parser import parse_equation


def parse_document(source: str) -> Document:
    """
    Parse a whole document into a Document of blocks.

    Blank lines separate blocks; the first line of a block names its type.
    Raises ValueError on a block whose header is not EQUATIONS or TEXT.
    """
    source = source.strip()

    blocks: list[Block] = []

    # Blocks are chunks of text separated by blank lines, e.g.:
    #   "EQUATIONS\nA + B = 10"  <blank>  "TEXT\nhello"
    block_strings = re.split(
        r"\n\s*\n",
        source
    )

    for block_string in block_strings:
        lines = block_string.splitlines()

        # Skip empty chunks produced by leading/trailing blank lines.
        if not lines:
            continue

        # First line is the block header; the rest is content.
        block_type = lines[0].strip()

        if block_type == "EQUATIONS":
            # Every non-empty line after the header is one equation.
            equations = [
                parse_equation(line)
                for line in lines[1:]
                if line.strip()
            ]

            blocks.append(
                EquationBlock(equations)
            )

        elif block_type == "TEXT":
            # Everything after the header is kept verbatim,
            # preserving internal newlines.
            text = "\n".join(lines[1:])

            blocks.append(
                TextBlock(text)
            )

        else:
            raise ValueError(
                f"Unknown block type: {block_type}"
            )

    return Document(blocks)
