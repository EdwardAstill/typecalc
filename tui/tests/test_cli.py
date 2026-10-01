"""Tests for the file-based command-line interface."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from typecalc_tui.cli import main


class CommandLineTests(unittest.TestCase):
    def solve_file(self, content: str) -> tuple[int, str, str]:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        ) as handle:
            handle.write(content)
            path = handle.name

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([path])

        Path(path).unlink()
        return code, out.getvalue(), err.getvalue()

    def test_prints_sorted_values_and_succeeds(self):
        code, out, err = self.solve_file("B = SOLVE(B)\n\nA + B = 10\nA = 6\n")

        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(out.splitlines(), ["A = 6.0", "B = 4.0"])

    def test_solver_errors_exit_nonzero_with_a_message(self):
        code, out, err = self.solve_file("A + B = 10\n")

        self.assertEqual(code, 1)
        self.assertIn("not fully determined", err)
        self.assertEqual(out, "")

    def test_missing_file_exits_nonzero_with_a_message(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["/nonexistent/path/typecalc.txt"])

        self.assertEqual(code, 1)
        self.assertIn("typecalc:", err.getvalue())
        self.assertEqual(out.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
