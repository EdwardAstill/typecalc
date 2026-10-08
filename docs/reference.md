# typecalc Reference

The **engine** (`typecalc`) parses and solves equation strings. The
**document converter** (`typecalc.text`) handles documents containing
`EQUATIONS` and `TEXT` blocks. A TUI can call the engine directly.

## Quick start

Pass one equation per string to `solve`:

```python
from typecalc import solve

values = solve(["A + B = 10", "A = 6"])
print(values)  # {'A': 6.0, 'B': 4.0}
```

No document headers, AST construction, or `SOLVE(B)` marker is required.
Every solved variable is returned. The result is a Python dictionary, not
encoded JSON; serialize it only when needed:

```python
import json
from typecalc import solve

print(json.dumps(solve(["A = 1/3"]), allow_nan=False))
# {"A": 0.3333333333333333}
```

### Input, output, and errors

- Pass a list or another sequence of equation strings, not one multiline
  string. Blank strings are ignored.
- Each call is independent. Input rows are unchanged, and reordering them
  does not change the solution.
- Returned values are finite real floats; fractions and roots may be
  approximate. Complex or out-of-range results raise `ValueError`.
- Parse errors raise `ValueError` with the original 1-based input position,
  including blank rows in the count (`Line 3: ...`).
- Underdetermined, inconsistent, or multiple-solution systems raise
  `ValueError`. An empty list returns `{}`.
- Incorrect input types raise `TypeError`. If SymPy cannot solve a system,
  its `NotImplementedError` propagates; this does not mean there is no solution.

## Command line

See the [installation guide](../README.md) to install the library or CLI
from GitHub, or run them from a local clone.

`typecalc` is the executable from the `typecalc-cli` package. Pass a file path:

```sh
typecalc equations.txt
typecalc --text 'A = 6'
```

The CLI reads the UTF-8 file, or takes literal text with `--text`, and passes
its lines directly to `solve`. File and text inputs are mutually exclusive.
Use one equation per line; blank lines are allowed. Successful results print
to stdout as `name = value`, sorted by variable name, with exit code 0. An
empty file succeeds without output. File, decoding, parsing, and solver
errors print to stderr with exit code 1; missing arguments return exit code 2.
Parse errors name the original 1-based line within the supplied input.

The entry point is `cli/src/typecalc_cli/cli.py`. The experimental TUI and
its equation catalog remain under `tui`, outside the active workspace.

## Document structure

For equations mixed with prose, use `parse_document` from `typecalc.text`.
A document is a series of blocks separated by one or more blank lines. The
first line of each block names its type; these headers are not inputs to
the engine's `solve`.

```text
EQUATIONS
A + B = 10
A = 6
B = SOLVE(B)

TEXT
This is some text to display.
```

Currently supported block types:

- `EQUATIONS` — every remaining non-empty line is one equation.
- `TEXT` — remaining lines are kept as plain text. The solver ignores them.

Consecutive blank lines count as a single separator. Leading and trailing
whitespace of the document is ignored.

## Equations

Each equation has one outer `=`. Operator precedence and parentheses work as
expected (`^` is exponentiation). Multiplication must be explicit: write
`C*X^2`, not `CX^2`.

Variable names are case-sensitive (`a` and `A` are different variables).
Function names are case-insensitive (`diff` and `DIFF` are the same function).

## Solving

The solver collects every equation and finds values for all mentioned
variables. It requires a unique solution: underdetermined variables raise an
error listing them.

`SOLVE(X)` denotes the same expression as `X`. `B = SOLVE(B)` means `B = B`,
so only your other equations constrain `B`:

```text
EQUATIONS
A + B = 10
A = 6
B = SOLVE(B)
```

This solves to `A = 6` and `B = 4`.

## Functions

### DIFF

`DIFF` takes a function, a variable, and an optional evaluation point:

```text
EQUATIONS
X = 10
A = DIFF(X^2, X)
```

gives `A = 20`. With a local evaluation point (`|`), the point is substituted
after differentiating and does not assign a document-wide value to `X`:

```text
EQUATIONS
A + B = 10
A = DIFF(X^2 | X=10)
B = SOLVE(B)
```

gives `A = 20` and `B = -10`. The third positional argument is an evaluation
point, not a derivative order. For higher derivatives, nest calls:

```text
EQUATIONS
A = DIFF(DIFF(X^3, X) | X=2)
```

gives `A = 12`.

### SOLVE

`SOLVE` requires exactly one argument and denotes the same expression.
It is optional when calling the Python `solve` function, which already
returns every variable's value.

## Solvability requirements

- Every variable mentioned in an equation must end up uniquely determined,
  whether by an equation, another variable's value, or an evaluation point.
  Variables used only inside a `DIFF` evaluation point do not need global
  values.
- Symbolic-only results are not supported: a derivative retaining free
  variables is an error unless you supply their values.
- `solve` returns floats, so fractions and roots may be approximate.
  Results that cannot be stored as a finite real number raise an error.

## Lower-level Python API

Most callers only need `from typecalc import solve`. For AST inspection,
`typecalc.parser` exposes `parse_equation`, `parse_expression`,
and `parse_equations`:

```python
from typecalc.parser import parse_equations

rows = ["A = 6", "B = A + 1"]
equations = parse_equations(rows)
print(equations[0].left.name)  # A
```

`solve` accepts strings, not AST nodes; AST-based symbolic solving is an
internal engine detail.

Document-specific APIs live in `typecalc.text`: `parse_document`
and `solve_document`. `solve_document` retains exact
SymPy values for document processing, unlike `solve`'s JSON-ready floats.
The input document is unchanged.

## Full document example

```python
from typecalc.text import parse_document, solve_document

text = """EQUATIONS
A + B = 10
A = 6
B = SOLVE(B)

TEXT
The values are shown above."""

document = parse_document(text)
print(solve_document(document))    # {'A': 6, 'B': 4}
print(document.blocks[1].text)     # The values are shown above.
```

## Rendering and planned features

Rendering equations and solved values as LaTeX or plots is planned. See
[the backend guide](backend.md) for the layer layout and
[the function notes](../package/typecalc/src/typecalc/functions/README.md) for `DIFF`
syntax and how to add another function.
