
## AST
Document is the root of the AST
Blocks are the children of the document

There will be 3 types of blocks:
    - Equations
    - text
    - plot

### Equation blocks
Equation blocks are a list of equations
equations each have a left expression and a right expression

Nodes represented by classes of expression type can be nested within each other:
A binary operation can have contain another binary operation and a symbol which are both expressions.

The different classes of expressions are:
- Binary operation
- Symbol
- Number
- FunctionCall


### Text blocks
These are not evaluated





## Parsing to ast

1. Text cleaning
first the text is cleaned
blank lines at teh top and bottom are removed
double empty lines are reduced to single

2. Walk though the blocks
Block are identified by empty lines
The text at the top of the block defines it
Blocks are broken down further depending on their type
Equations are broken into expressions:


3. 
The ast breaks down:
a document into blocks
blocks into lines


## AST conversion
to latex ... coming soon

