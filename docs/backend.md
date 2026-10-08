# Backend

## Workspace layout

The repository is a uv workspace. The engine is a library
(`package/typecalc`); frontends are separate apps that import it
(`cli` today). The library depends only on SymPy, and the CLI depends only
on the library. The experimental TUI remains under `tui`, outside the
active workspace.

The CLI's `typecalc = { workspace = true }` source uses the local engine
as an editable dependency. See the [installation guide](../README.md)
for GitHub and local installation commands.

The `typecalc` command in `cli/src/typecalc_cli/cli.py` reads a UTF-8 file or
literal `--text` input, passes its lines to `solve`, and prints sorted variable values. Errors go to
stderr with a nonzero exit code. It imports the engine directly.

## Two layers

The typecalc library has two layers with a one-way dependency:

- `typecalc` — the **engine**: equation syntax, AST nodes, mathematical
  functions, and solving. Its public `solve` accepts a sequence
  of equation strings and returns JSON-ready variable values.
- `typecalc.text` — the **document converter**: handles `EQUATIONS`/`TEXT`
  blocks, prose, and document order. It uses the engine; the engine does
  not import it.

## Engine

### Public interface

```python
from typecalc import solve

values = solve(["A + B = 10", "A = 6"])
print(values)  # {'A': 6.0, 'B': 4.0}
```

No block headers or `SOLVE` markers are needed. Blank strings are ignored.
The input is unchanged, and equation order does not affect deterministic
solutions. Each occurrence of `RAND()` draws a fresh sample per solve and
keeps it fixed for that solve.

`solve` returns `dict[str, float]`, not encoded JSON. It rejects complex
or out-of-range results with `ValueError`, so successful results support
`json.dumps(values, allow_nan=False)`. Fractions and roots may be approximate.
Invalid input types raise `TypeError`.

### Equation parsing

The engine owns `parser/tokenizer.py` and `parser/expression_parser.py`.
`typecalc.parser` exposes `parse_expression`, `parse_equation`, and
`parse_equations` for AST consumers. The public solver uses this same
parser, adding the original 1-based input line to parse errors.

### AST

Expressions form a recursive tree:

- `BinaryOperation`
- `Symbol`
- `Number`
- `FunctionCall`

`Expression` is the union of these types; operations contain two child
expressions, function calls contain a list of arguments, and numbers and
symbols are the leaves.

An `Equation` (`ast/equation.py`) holds a left and a right expression — one
`lhs = rhs` statement.

### Solving

The public `solve` parses the strings and calls the internal
`_solve_equations(equations)` in `solver/sympy_variable_solver.py`. This
AST-based solver retains exact SymPy values; conversion to finite floats
happens only at the public API boundary.

A unique solution is required: unresolved variables, inconsistent equations,
and multiple solutions raise `ValueError`. SymPy's `NotImplementedError`
propagates when it cannot solve a system.

Mathematical functions live in `typecalc/functions/`. See the
[function notes](../package/typecalc/src/typecalc/functions/README.md) for function syntax
and how to add another function.

## Text layer

### Block format

A document is a series of blocks separated by blank lines; the first line of
each block names its type (`EQUATIONS` or `TEXT`):

1. `parse_document` removes leading and trailing whitespace, then splits the
   source into blocks at blank lines. Consecutive blank lines act as one
   separator.
2. The first line of each block identifies its type.
3. In an equation block, each remaining non-empty line is parsed as an
   equation (`parse_equation`). In a text block, the remaining lines are
   kept as text.

`Document`, `EquationBlock`, and `TextBlock` live in `text/document.py`;
the solver ignores text blocks.

`document_equations(document)` flattens the blocks into engine equations;
`solve_document` reuses the internal AST solver without
reparsing or prematurely converting its exact SymPy results to floats.
It returns `dict[str, sympy.Expr]` and leaves the document unchanged.
An equation has one outer `=`. Calls can contain their own evaluation point,
such as `DIFF(X^2 | X=10)`.

## Rendering

Rendering equations and solved values as LaTeX or plots is planned.
