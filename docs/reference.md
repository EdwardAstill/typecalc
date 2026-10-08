# typecalc Reference

`typecalc` parses and solves lists of equation strings. Frontends such as
the CLI call this same API.

## Quick start

Pass one equation per string to `solve`:

```python
from typecalc import solve

values = solve(["A + B = 10", "A = 6"])
print(values)  # {'A': 6.0, 'B': 4.0}
```

Every solved variable is returned. The result is a Python dictionary,
not encoded JSON; serialize it only
when needed:

```python
import json
from typecalc import solve

print(json.dumps(solve(["A = 1/3"]), allow_nan=False))
# {"A": 0.3333333333333333}
```

### Input, output, and errors

- Pass a list or another sequence of equation strings, not one multiline
  string. Blank strings are ignored. Every other row must be an equation;
  block headers and prose are rejected.
- Each call leaves input rows unchanged. Reordering deterministic equations
  does not change the solution; `RAND()` draws new values on each solve.
- Numeric literals stay exact during solving. Returned values are finite real
  floats, so fractions and roots may be approximate. Complex or out-of-range
  results raise `ValueError`.
- Parse errors raise `ValueError` with the original 1-based input position,
  including blank rows in the count (`Line 3: ...`).
- No returned solution, unresolved values, or multiple returned solutions
  raise `ValueError`. An empty list returns `{}`.
- Incorrect input types raise `TypeError`. Unsupported systems may raise
  SymPy's `NotImplementedError`; this does not mean there is no solution.

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

## Equations

Each equation has one outer `=`. Operator precedence and parentheses work as
expected (`^` is exponentiation). Multiplication must be explicit: write
`C*X^2`, not `CX^2`.

Variable names are case-sensitive (`a` and `A` are different variables).
Function names are case-insensitive (`diff` and `DIFF` are the same function).

## Solving

The solver sends every equation to SymPy and accepts one returned solution
with finite real values for all retained global variables:

```text
A + B = 10
A = 6
```

This solves to `A = 6` and `B = 4`. The old `SOLVE(...)` expression wrapper
has been removed; write the expression directly and omit identity markers
such as `B = SOLVE(B)`.

## Functions

### DIFF

`DIFF` takes a function, a variable, and an optional evaluation point:

```text
X = 10
A = DIFF(X^2, X)
```

gives `A = 20`. With a local evaluation point (`|`), the point is substituted
after differentiating and does not assign a global value to `X`:

```text
A + B = 10
A = DIFF(X^2 | X=10)
```

gives `A = 20` and `B = -10`. The third positional argument is an evaluation
point, not a derivative order. For higher derivatives, nest calls:

```text
A = DIFF(DIFF(X^3, X) | X=2)
```

gives `A = 12`.

### INTEGRATE

`INTEGRATE(expression, variable, lower, upper)` calculates a definite integral:

```text
A = INTEGRATE(X^2, X, 0, 3)
```

This gives `A = 9`. The integration variable is local to the integrand and
does not need a separate value. A global `X = 10` would remain unchanged and
would not replace `X` inside this integral. Bounds and coefficients can use
variables solved by other equations:

```text
A = INTEGRATE(C*X, X, 0, B)
C = 2
B = 3
```

This gives `A = 9`. Reversing the bounds negates the integral; equal bounds
give zero. Both bounds are required. Calls can be nested, for example
`INTEGRATE(DIFF(X^3, X), X, 0, 2)` gives `8`.

### RAND

`RAND()` takes no arguments and samples a uniform pseudorandom number with
`0 <= value < 1`. Each occurrence is sampled once per solve, and its value
stays fixed throughout that solve. Assign it to a variable to reuse a sample:

```text
R = RAND()
A = 10*R
B = 20*R
```

Here `B = 2*A`. Separate `RAND()` calls draw separate samples, and solving
the same input again draws new samples.

### SIN, COS, TAN

`SIN(angle)`, `COS(angle)`, and `TAN(angle)` each take one angle in radians.
Arguments can be expressions or variables constrained by other equations:

```text
X = 0.5
S = SIN(X)
C = COS(X)
T = TAN(X)
```

These functions remain symbolic inside `DIFF` and `INTEGRATE`:
`DIFF(SIN(X) | X=0)` gives `1`.

### LN, LOG, EXP

- `LN(value)` is the natural logarithm: `LN(EXP(3))` gives `3`.
- `LOG(value, base)` uses an explicit base: `LOG(8, 2)` gives `3`.
- `EXP(value)` raises e to the given power: `EXP(1)` gives approximately
  `2.718281828459045`.

Logarithms require a positive value. A logarithm base must be positive and
different from `1`. Arguments may be expressions or solved variables.

### ABS

`ABS(value)` returns its nonnegative magnitude: `ABS(-5)` gives `5`.
It also supports variables constrained by other equations:

```text
X = -5
A = ABS(X)
```

This gives `A = 5`. Absolute values remain symbolic for calculus:
`INTEGRATE(ABS(X), X, -1, 1)` gives `1`.

### PI, RAD, DEG

- `PI()` takes no arguments and returns pi. It stays exact during solving,
  so `SIN(PI()/2)` gives exactly `1`.
- `RAD(degrees)` converts degrees to radians: `RAD(180)` gives pi.
- `DEG(radians)` converts radians to degrees: `DEG(PI())` gives `180`.

For angles in degrees, write `SIN(RAD(30))` to get `0.5`. Conversions accept
expressions and solved variables. `PI` without parentheses is still an
ordinary variable; the constant requires `PI()`.

### ASIN, ACOS, ATAN, ATAN2

Inverse trigonometric functions return their principal angles in radians:

| Function | Result range | Example |
| --- | --- | --- |
| `ASIN(value)` | `[-PI()/2, PI()/2]` | `DEG(ASIN(0.5))` gives `30` |
| `ACOS(value)` | `[0, PI()]` | `DEG(ACOS(0.5))` gives `60` |
| `ATAN(value)` | `(-PI()/2, PI()/2)` | `DEG(ATAN(1))` gives `45` |
| `ATAN2(y, x)` | `(-PI(), PI()]` | `DEG(ATAN2(1, -1))` gives `135` |

`ASIN` and `ACOS` require values between `-1` and `1`, inclusive, for real
results. `ATAN2` takes the **y component first**, accounts for the quadrant,
and is undefined when both components are zero.

### ROUND

`ROUND(value, places)` rounds to an integer number of decimal places. Both
arguments are required and may use expressions or solved variables.
Zero places rounds to an integer; negative places round to tens, hundreds,
and so on:

```text
A = ROUND(PI(), 2)
B = ROUND(1234, -2)
```

This gives `A = 3.14` and `B = 1200`. Halfway values round to the even digit:
`ROUND(2.5, 0)` gives `2`, `ROUND(3.5, 0)` gives `4`, and
`ROUND(2.675, 2)` gives `2.68`. This changes the numeric value; it does not
add trailing zeros to the output.

## Solvability requirements

- Every variable retained after symbolic simplification needs a numeric value.
  The differentiation variable in `DIFF(expression | X=point)` and the
  integration variable of `INTEGRATE`
  do not need global values; variables remaining in the point or bounds do.
- Symbolic-only results are not supported: a derivative retaining free
  variables is an error unless you supply their values.
- `solve` returns floats, so fractions and roots may be approximate.
  Results that cannot be stored as a finite real number raise an error.

### Limitations

SymPy may return only principal branches for periodic or transcendental
equations: `TAN(X) = 0` returns `X = 0`, although other solutions exist.
Simplification can also discard domain restrictions; `A = LOG(1, B)` with
`B = 1` currently returns `A = 0` despite the invalid logarithm base.

## Lower-level Python API

The package root exports only `solve`. For AST inspection, import node types
from `typecalc.ast`; `typecalc.parser` exposes `parse_equation`,
`parse_expression`, and `parse_equations`:

```python
from typecalc.parser import parse_equations

rows = ["A = 6", "B = A + 1"]
equations = parse_equations(rows)
print(equations[0].left.name)  # A
```

`solve` accepts strings, not AST nodes; AST-based symbolic solving is an
internal engine detail.

## Rendering and planned features

Rendering equations and solved values as LaTeX or plots is planned. See
[the backend guide](backend.md) for the engine layout and
[the function notes](../package/typecalc/src/typecalc/functions/README.md) for
function syntax and how to add another function.
