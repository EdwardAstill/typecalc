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

The `EQUATIONS` headers in the examples below belong to the optional document
format, not the input to `solve`.

## DIFF

`diff.py` implements first derivatives using `sympy.diff`.

```text
EQUATIONS
X = 10
A = DIFF(X^2, X)
```

This finds `A = 20`. To use a local evaluation point without needing a separate
equation for X:

```text
EQUATIONS
A + B = 10
A = DIFF(X^2 | X=10)
B = SOLVE(B)
```

This finds `A = 20` and `B = -10`. The parser represents the point form as
`FunctionCall("DIFF", [expression, variable, point])`. The point is substituted
after differentiation and does not assign a document-wide value to X.

For higher derivatives, nest calls:

```text
EQUATIONS
A = DIFF(DIFF(X^3, X) | X=2)
```

This finds `A = 12`. Multiplication must be explicit, for example `C*X^2`.
The third positional argument is an evaluation point, not a derivative order.

The solver still requires uniquely determined variable values. If a derivative
retains free variables, provide their values through equations or an evaluation
point. Symbolic-only document results are not supported yet. The public `solve`
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
