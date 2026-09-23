# Backend

## AST

`Document` is the root of the AST. Its children are blocks, kept in source order.

There are currently two types of block:

- `EquationBlock`
- `TextBlock`

Plot blocks are planned. `Block` is a union of the supported block types.

### Equation blocks

An `EquationBlock` contains a list of equations. Each `Equation` has a left
expression and a right expression.

The expression types are:

- `BinaryOperation`
- `Symbol`
- `Number`
- `FunctionCall`

`Expression` is a union of these types. Expressions form a recursive tree:
a binary operation contains two expressions, and a function call contains
a list of argument expressions. Numbers and symbols are the leaves.

### Text blocks

A `TextBlock` holds text. The solver ignores it, and the evaluator preserves it.

## Parsing to an AST

1. `parse_document` removes leading and trailing whitespace, then splits the
   source into blocks at blank lines. Consecutive blank lines act as one separator.
2. The first line of each block identifies its type: `EQUATIONS` or `TEXT`.
3. In an equation block, each remaining non-empty line is parsed as an equation.
   Each side is tokenized and turned into an expression tree, respecting
   parentheses and operator precedence. In a text block, the remaining lines
   are kept as text.

An equation has one outer `=`. Function calls can contain their own evaluation
point, such as `DIFF(X^2 | X=10)`.

## Solving and evaluation

`solve_variables(document)` extracts the equations, converts them to SymPy,
and returns the uniquely determined variable values.

`evaluate_document(document)` uses those values to return a new AST with
function calls replaced by numeric results. Surrounding expressions, block
order, and text are preserved; the input AST is unchanged.

For solving, `SOLVE(B)` means B, so `B = SOLVE(B)` adds no constraint.
Evaluated results use floats for now.

Mathematical functions live in `backend/typecalc/functions/`.
See the [function notes](../backend/typecalc/functions/README.md) for
`DIFF` syntax and how to add another function.

## AST conversion

Rendering the evaluated AST as LaTeX or plots is planned.
