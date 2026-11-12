# Operations reference

Use typecalc to calculate values or solve simultaneous equations, including
unknowns on either side of `=`. Equations are constraints, not sequential
assignments: `V = I*R` and `V = 12` and `R = 3` solve to `I = 4`.
The solver must return one fully determined, finite real solution; it is
not a general symbolic-output calculator. See [solvability requirements](reference.md#solvability-requirements)
for solver limits.

## Arithmetic and syntax

Each example expression below can be used as an equation such as `A = 2 + 3`.

| Operation | Syntax / example | Result |
| --- | --- | --- |
| Addition | `2 + 3` | `5` |
| Subtraction | `7 - 4` | `3` |
| Multiplication | `3 * 4` | `12` |
| Division | `7 / 2` | `3.5` |
| Power | `2^3` | `8` |
| Negative exponent | `2^-3` | `0.125` |
| Root via fractional power | `9^(1/2)` | `3` |
| Unary signs | `-5 + +2` | `-3` |
| Parentheses | `(2 + 3) * 4` | `20` |

Precedence, highest first: parentheses/function calls, powers, unary signs,
multiplication/division/`@`, addition/subtraction. Powers associate right:
`2^3^2` is `2^(3^2)` (`512`). Other binary operators associate left:
`8/4/2` is `(8/4)/2` (`1`). `-2^2` is `-4`; `(-2)^2` is `4`.

- Numbers: integers and decimals such as `12`, `0.5`, and `-3.14`.
  Write `0.5`, not `.5`, and `5.0`, not `5.`. Scientific notation is not
  supported; use `1.2*10^3` instead of `1.2e3`.
- Names start with an ASCII letter or `_`, followed by word characters
  (letters, digits, underscores); examples: `mass`, `R_1`, `_offset`.
  Variables are case-sensitive. `PI` and `e` are ordinary variables;
  use `PI()` and `E()` for the constants. `EXP(1)` also gives e.
- One equation per line, with one outer `=`. Blank lines are allowed;
  comments, headings, units, and bare expressions are not.
- Multiplication requires `*`: `2*X`, not `2X` or `2(X+1)`.
  `XY` is one variable, not `X*Y`.
- No `%` (modulo/percent), `//`, `**`, factorial `!`, inequalities,
  comparisons, or Boolean operators.
  Write a percentage explicitly, for example `price*15/100`.
- Arrays are nonempty vectors `[1, 2]` or rectangular matrices
  `[[1, 2], [3, 4]]`, with scalar expressions as components.
  `[1, 2]`, `[[1, 2]]`, and `[[1], [2]]` have distinct shapes:
  `(2,)`, `(1, 2)`, and `(2, 1)`. Ragged, empty, mixed-rank, and
  higher-rank arrays are unsupported.
- Array `+` and `-` require identical shapes; unary `+` and `-` work.
  `*` scales an array by a scalar or multiplies equal-shaped arrays
  elementwise. `/` requires a scalar denominator; `^` is scalar-only.
  There is no broadcasting, indexing, determinant, inverse, or cross-product.
- `@` requires two arrays and matching contracted dimensions. Like NumPy's
  rank-1/rank-2 products, vector @ vector returns a scalar; matrix @ vector
  and vector @ matrix return vectors; matrix @ matrix returns a matrix.
  This is a small array language, not full NumPy compatibility.

These lines can be saved as an equation file and run with `typecalc file.txt`:

```text
v = [1, 2]
M = [[1, 2], [3, 4]]
scaled = 2*v
elementwise = v*v
dot_product = v@v
matrix_vector = M@v
vector_matrix = v@M
matrix_product = M@M
row_vector = ROW(v)
column_vector = COL(v)
transposed = TRANSPOSE(M)
length = NORM(v)
dot_function = DOT(v, v)
```

Here `scaled = [2, 4]`, `elementwise = [1, 4]`, `dot_product = 5`,
`matrix_vector = [5, 11]`, `vector_matrix = [7, 10]`, and
`matrix_product = [[7, 10], [15, 22]]`. `row_vector = [[1, 2]]`,
`column_vector = [[1], [2]]`, `transposed = [[1, 3], [2, 4]]`,
`length = 5^(1/2)`, and `dot_function = 5`; output components are floats.

For a linear solve, give unknown components scalar names:

```text
M@v = [5, 6]
v = [x, y]
M = [[2, 1], [1, 1]]
```

This gives `x = -1`, `y = 7`, and `v = [-1, 7]` (and returns `M` too).
Array equalities compare corresponding components and require identical
shapes. Named array shapes come from an equation with that variable alone
on one side and an array-valued expression on the other. Definitions may
appear later and depend on other declared arrays; order does not matter.
Dimensions are not inferred through arbitrary equations: `M@v = [5, 6]`
alone does not declare `v`'s shape. Use `v = [x, y]` or an explicit
component literal in the product. A cycle without a known array shape
does not declare dimensions.

## All supported functions

Function names are case-insensitive. Arguments can be expressions and calls
can nest. Scalar functions reject array arguments: write
`[SIN(0), COS(0)]`, not `SIN([0, 0])`.
This is the complete function list, not the full SymPy API.

| Function | Meaning | Example expression | Result |
| --- | --- | --- | --- |
| `ABS(value)` | Absolute value | `ABS(-5)` | `5` |
| `SIN(angle)` | Sine, radians | `SIN(PI()/2)` | `1` |
| `COS(angle)` | Cosine, radians | `COS(0)` | `1` |
| `TAN(angle)` | Tangent, radians | `TAN(PI()/4)` | `1` |
| `ASIN(value)` | Inverse sine, radians | `ASIN(0)` | `0` |
| `ACOS(value)` | Inverse cosine, radians | `ACOS(1)` | `0` |
| `ATAN(value)` | Inverse tangent, radians | `DEG(ATAN(1))` | `45` |
| `ATAN2(y, x)` | Quadrant-aware angle, radians | `DEG(ATAN2(1, -1))` | `135` |
| `PI()` | Pi | `PI()` | approximately `3.141592653589793` |
| `E()` | Euler's number e | `E()` | approximately `2.718281828459045` |
| `RAD(degrees)` | Degrees to radians | `RAD(180)` | approximately `3.141592653589793` |
| `DEG(radians)` | Radians to degrees | `DEG(PI())` | `180` |
| `LN(value)` | Natural logarithm | `LN(EXP(3))` | `3` |
| `LOG(value, base)` | Logarithm to an explicit base | `LOG(8, 2)` | `3` |
| `EXP(value)` | e raised to a power | `EXP(0)` | `1` |
| `ROUND(value, places)` | Decimal rounding, ties to even | `ROUND(2.675, 2)` | `2.68` |
| `RAND()` | Fresh uniform sample per occurrence per solve | `RAND()` | `0 <= value < 1` |
| `DIFF(expression, variable)` | First derivative; supply remaining variables | `DIFF(X^2, X, 3)` | `6` |
| `INTEGRATE(expression, variable, lower, upper)` | Definite integral | `INTEGRATE(X^2, X, 0, 3)` | `9` |
| `DOT(v, w)` | Dot product of equal-length vectors | `DOT([1, 2], [3, 4])` | `11` |
| `NORM(v)` | Euclidean vector norm | `NORM([3, 4])` | `5` |
| `TRANSPOSE(array)` | Transpose a matrix; leave a vector 1D | `TRANSPOSE([[1, 2]])` | `[[1], [2]]` |
| `ROW(v)` | Convert a vector to a 2D row | `ROW([1, 2])` | `[[1, 2]]` |
| `COL(v)` | Convert a vector to a 2D column | `COL([1, 2])` | `[[1], [2]]` |

`DIFF` also accepts a third argument as an evaluation point, or the shorthand
`DIFF(X^2 | X=3)`. Neither form assigns a global value to `X`.
There is no `SQRT` function; use a fractional power for a positive square root.
For domains, variable scope, rounding, and randomness, see the
[detailed function reference](reference.md#functions).

