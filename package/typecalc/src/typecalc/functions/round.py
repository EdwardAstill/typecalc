"""Round real values to decimal places, with ties going to the even digit."""

import sympy


class _Round(sympy.Function):
    """Defer rounding until equation variables have numeric values."""

    nargs = 2

    @classmethod
    def eval(cls, value: sympy.Expr, places: sympy.Expr) -> sympy.Expr | None:
        if places.is_integer is False:
            raise ValueError("ROUND places must be an integer.")
        if value.is_real is False or value.is_finite is False:
            raise ValueError("ROUND requires a finite real value.")
        if not value.is_number or not places.is_number:
            return None
        if places.is_integer is not True:
            raise ValueError("ROUND places must be an integer.")

        scale = 10**places
        scaled = value * scale
        lower = sympy.floor(scaled)
        # Keep exact decimal inputs exact, including halfway cases like 2.675.
        if scaled - lower == sympy.Rational(1, 2):
            return (lower + sympy.Mod(lower, 2)) / scale
        return sympy.floor(scaled + sympy.Rational(1, 2)) / scale


def round(arguments: list[sympy.Expr]) -> sympy.Expr:
    """ROUND(value, places); negative places round to tens, hundreds, etc."""
    if len(arguments) != 2:
        raise ValueError("ROUND requires a value and an integer number of places.")

    return _Round(*arguments)
