# Functions

Put each mathematical function in its own module here and add its name to
`FUNCTIONS` in `__init__.py`. A handler accepts a list of SymPy expressions,
validates its arguments, and returns a SymPy expression. Function names in
this registry are case-insensitive; variable names remain case-sensitive.

The parser records calls as `FunctionCall` nodes. The solver recursively
converts their arguments and dispatches them through the registry.

`SOLVE` is handled by the converter: its mathematical meaning is its argument,
so `B = SOLVE(B)` adds no constraint.
It is not required by the public Python API: `typecalc.solve` accepts equation
strings and returns every solved variable as a finite real float. For example:

```python
from typecalc import solve

print(solve(["A = DIFF(X^2 | X=10)", "A + B = 10"]))
# {'A': 20.0, 'B': -10.0}
```

The examples below use one equation per line. Pass each line as a string in
the list supplied to `solve`, or save the lines in a file for the CLI.

## DIFF

`diff.py` implements first derivatives using `sympy.diff`.

```text
X = 10
A = DIFF(X^2, X)
```

This finds `A = 20`. To use a local evaluation point without needing a separate
equation for X:

```text
A + B = 10
A = DIFF(X^2 | X=10)
B = SOLVE(B)
```

This finds `A = 20` and `B = -10`. The parser represents the point form as
`FunctionCall("DIFF", [expression, variable, point])`. The point is substituted
after differentiation and does not assign a global value to X.

For higher derivatives, nest calls:

```text
A = DIFF(DIFF(X^3, X) | X=2)
```

This finds `A = 12`. Multiplication must be explicit, for example `C*X^2`.
The third positional argument is an evaluation point, not a derivative order.

The solver still requires uniquely determined variable values. If a derivative
retains free variables, provide their values through equations or an evaluation
point. Symbolic-only results are not supported. The public `solve`
function returns floats, so fractions and roots can be approximate.

## INTEGRATE

`INTEGRATE(expression, variable, lower, upper)` uses `sympy.integrate` for
definite integration. All four arguments are required, and the variable must
be a symbol.

```text
A = INTEGRATE(X^2, X, 0, 3)
```

This gives `A = 9` without needing a global value for `X`. Integration happens
before substituting solved variable values. The integration variable is local
to the integrand, while coefficients and bounds can use global variables:

```text
A = INTEGRATE(C*X, X, 0, B)
C = 2
B = 3
```

This gives `A = 9`. Reversed bounds negate the result; equal bounds give zero.
Functions can be nested, including `DIFF` and `INTEGRATE` in either order.

## RAND

`RAND()` takes no arguments and samples a uniform pseudorandom value in
`[0, 1)`. Each call in the expression tree is sampled once during conversion
to SymPy, so the sample stays fixed while solving. The sample is represented
as an exact rational to prevent SymPy from rounding a value just below `1`
up to `1`.

```text
R = RAND()
A = 10*R
B = 20*R
```

All references to `R` share its sampled value, so `B = 2*A`. Separate `RAND()`
occurrences draw separate samples, and each solve draws fresh samples.

## SIN, COS, TAN

`SIN(angle)`, `COS(angle)`, and `TAN(angle)` take exactly one argument, in
radians. They return symbolic SymPy expressions, allowing solved variables
and nesting inside calculus functions. For example,
`DIFF(SIN(X) | X=0)` gives `1`.

## LN, LOG, EXP

- `LN(value)` takes one argument and calculates its natural logarithm.
- `LOG(value, base)` takes two arguments and uses the specified base.
- `EXP(value)` takes one argument and calculates e raised to that power.

Logarithms require positive values; bases must also be positive and different
from `1`. These functions preserve symbolic arguments for solving and calculus.
For example, `LOG(8, 2)` and `LN(EXP(3))` both give `3`.

## ABS

`ABS(value)` takes one argument and uses `sympy.Abs` to return its
nonnegative magnitude. `ABS(-5)` gives `5`. Solver variables are real so
symbolic absolute values can be solved, differentiated, and integrated:
`DIFF(ABS(X) | X=-2)` gives `-1`, and
`INTEGRATE(ABS(X), X, -1, 1)` gives `1`.

## PI, RAD, DEG

- `PI()` takes no arguments and returns exact `sympy.pi`.
- `RAD(degrees)` takes one argument and multiplies by `pi/180`.
- `DEG(radians)` takes one argument and multiplies by `180/pi`.

Conversions preserve exact expressions, so `SIN(RAD(30))` gives `1/2`
internally and `DEG(PI())` gives `180`. `PI` without parentheses remains
an ordinary variable name.

## ASIN, ACOS, ATAN, ATAN2

`ASIN(value)`, `ACOS(value)`, and `ATAN(value)` take one argument and use
their corresponding SymPy functions. They return principal angles in
radians, with ranges `[-pi/2, pi/2]`, `[0, pi]`, and `(-pi/2, pi/2)`,
respectively. `ASIN` and `ACOS` require inputs in `[-1, 1]` for real results.

`ATAN2(y, x)` takes two arguments, in y-then-x order, and returns the angle
in `(-pi, pi]` with the correct quadrant. Both arguments cannot be zero.
For example, `DEG(ATAN2(1, -1))` gives `135`.

## ROUND

`ROUND(value, places)` takes two arguments. `places` must be an integer:
positive values round fractional digits, zero rounds to an integer, and
negative values round to tens, hundreds, etc. Halfway values round to the
even digit. Examples: `ROUND(2.5, 0)` gives `2`, `ROUND(3.5, 0)` gives `4`,
and `ROUND(125, -1)` gives `120`.

The internal `_Round` SymPy function defers evaluation until both arguments
have numeric values, including when they come from other equations. It
returns exact expressions, so `ROUND(2.675, 2)` gives exactly `67/25`
internally and `2.68` through the public API. Rounding changes numeric
values, not output formatting or trailing zeros.
