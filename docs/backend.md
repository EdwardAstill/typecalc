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

## Engine

The `typecalc` library handles equation syntax, AST nodes, mathematical
functions, and solving. Its public `solve` accepts a sequence of equation
strings and returns JSON-ready variable values.

### Public interface

```python
from typecalc import solve

values = solve(["A + B = 10", "A = 6"])
print(values)  # {'A': 6.0, 'B': 4.0}
```

The package root exports only `solve`. Each nonblank string must be an
equation; blank strings are ignored. Block headers and prose are rejected.
The input is unchanged, and equation order does not affect deterministic
solutions. Each occurrence of `RAND()` draws a fresh sample per solve and
keeps it fixed for that solve.

`solve` returns `dict[str, float]`, not encoded JSON. It rejects complex
or out-of-range results with `ValueError`, so successful results support
`json.dumps(values, allow_nan=False)`. Fractions and roots may be approximate.
Invalid input types raise `TypeError`.

### Equation parsing

`parser.py` contains tokenization and expression/equation parsing.
`typecalc.parser` exposes `parse_expression`, `parse_equation`, and
`parse_equations` for AST consumers. The public solver uses this same
parser, adding the original 1-based input line to parse errors.

### AST

`ast.py` defines expressions that form a recursive tree:

- `BinaryOperation`
- `Symbol`
- `Number`
- `FunctionCall`

`Expression` is the union of these types; operations contain two child
expressions, function calls contain a list of arguments, and numbers and
symbols are the leaves. `Number.value` preserves the numeric token as a
string, which the solver converts directly to an exact SymPy rational.

An `Equation`, also in `ast.py`, holds a left and a right expression — one
`lhs = rhs` statement.

### Solving

The public `solve` parses the strings and calls the internal
`_solve_equations(equations)` in `solver.py`. This
AST-based solver retains exact SymPy values; conversion to finite floats
happens only at the public API boundary.

Variable symbols have the `real=True` assumption, matching the public API's
real outputs and allowing symbolic `ABS` calls to be solved and differentiated.

The solver delegates to `sympy.solve` and accepts one returned solution with
finite real values for every retained variable. No solution, unresolved values,
or multiple returned solutions raise `ValueError`; unsupported systems may
raise `NotImplementedError`. SymPy may omit branches or simplify away domain
restrictions; see the [limitations](reference.md#limitations).

Mathematical functions live in `typecalc/functions/`. See the
[function notes](../package/typecalc/src/typecalc/functions/README.md) for function syntax
and how to add another function.

## Rendering

Rendering equations and solved values as LaTeX or plots is planned.
