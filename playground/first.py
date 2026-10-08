from pathlib import Path

from typecalc import solve

equations_path = Path(__file__).with_name("calcs.txt")
equations = equations_path.read_text(encoding="utf-8").splitlines()
print(solve(equations))
