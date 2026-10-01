# Backend

## Workspace layout

The repository is a uv workspace. The engine is a library
(`packages/typecalc`); frontends are separate apps that import it
(`apps/tui` today). Install boundaries: the library depends only on sympy,
and nobody installing it pulls Textual.

## Two layers

The typecalc library has two layers with a one-way dependency:

- `typecalc` — the **engine**: equation syntax, AST nodes, mathematical
  functions, solving, and evaluation. Its public `solve` accepts a sequence
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
The input is unchanged, equation order does not affect the solution, and
each call is independent.

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

### Solving and evaluation

The public `solve` parses the strings and calls the internal
`_solve_equations(equations)` in `solver/sympy_variable_solver.py`. This
AST-based solver retains exact SymPy values; conversion to finite floats
happens only at the public API boundary.

A unique solution is required: unresolved variables, inconsistent equations,
and multiple solutions raise `ValueError`. SymPy's `NotImplementedError`
propagates when it cannot solve a system.

`evaluate_equations(equations, values)` returns new equations with function
calls replaced by numeric results; solving is the caller's job.

Mathematical functions live in `typecalc/functions/`. See the
[function notes](../packages/typecalc/src/typecalc/functions/README.md) for `DIFF` syntax
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
the solver ignores text blocks and the evaluator preserves them.

`document_equations(document)` flattens the blocks into engine equations;
`solve_document` and `evaluate_document` reuse the internal AST solver without
reparsing or prematurely converting its exact SymPy results to floats.
`solve_document` returns `dict[str, sympy.Expr]`; `evaluate_document` replaces
function calls with float-valued `Number` nodes and preserves the document.
An equation has one outer `=`. Calls can contain their own evaluation point,
such as `DIFF(X^2 | X=10)`.

## Rendering

Rendering the evaluated AST as LaTeX or plots is planned.
