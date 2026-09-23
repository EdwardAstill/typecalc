quite differtn to the cell method i think that i just want text

you just write the equations


A + B = 10
A = DIFF(AX^2|X=10) = V(A)

B = V(B)
The latex for this would be

\[
A + B = 10

A = \left.\frac{d}{dx}(x^2)\right|_{x=10} = 20

B = -10
\]

how would this all work for each lettter is there a certain amount of information liek do we build an ast or what

if you had a graph where notessa re variable sand the relationships are equations then you just need as many non equivalent edges as nodes

i think taht just 

doing ... should mean diplay remaining varibles
TEXT(THis should display as text)



DIFF(Function|condition)

Diffs take in function, variable with respect to, there are no double derivatives yetm just do diff around diff


B = SOLVE(B)

This would show the value of B unless you are in the typing mode
this is possible because it is constrained

PLOT(LINE(3)) plot should take in functions
Matrices

A = MATRIX( , S(2,2)) - last arguments is size this allows for more than order 2


latex alignment?


To have equations display next to each other with a space use a new line
To have them stacked put in a space


Then you can go to display mode
and it would render it (display mode can maybe be on the right)
you would put equations 

spreadheet is sometimes useful?
spreadsheet mode??

for now i can use sympy

in the future i would like to implement Buchberger's algorithm to solve it by myself

i think for now i want to take in text and give it to a parser that builds and ast

from the ast then it goes to the solver

the solver gives the results

then a displayer combines the original text with the results to give latex/plots etc

