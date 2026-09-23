# Functions

Put each mathematical function in its own module here and add its name to
`FUNCTIONS` in `__init__.py`. A handler accepts a list of SymPy expressions,
validates its arguments, and returns a SymPy expression. Function names in
this registry are case-insensitive; variable names remain case-sensitive.

The parser records calls as `FunctionCall` nodes. The solver recursively
converts their arguments and dispatches them through the registry. The
document evaluator uses that same conversion and replaces calls with numeric
`Number` nodes after substituting the solved variable values.

`SOLVE` remains an evaluation marker handled by the converter: its mathematical
meaning is its argument, so `B = SOLVE(B)` adds no constraint.

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
point. Symbolic-only document results are not supported yet. Evaluated AST
results use floats, so fractions and roots can be approximate.
