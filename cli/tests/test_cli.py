"""Exercise file inputs, terminal output, and CLI failures."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from typecalc_cli.cli import main


class CommandLineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "equations with spaces.txt"

    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def solve_file(self, content):
        self.path.write_text(content, encoding="utf-8")
        return self.run_cli([str(self.path)])

    def test_prints_sorted_values_and_accepts_blank_lines_and_spaces_in_the_path(self):
        code, out, err = self.solve_file("B + A = 10\n\n  \nA = 6\n")
        self.assertEqual(code, 0)
        self.assertEqual(out, "A = 6.0\nB = 4.0\n")
        self.assertEqual(err, "")

    def test_parse_errors_preserve_original_file_line_numbers(self):
        code, out, err = self.solve_file("A = 6\n\nB =\n")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("typecalc: Line 3:", err)

    def test_solver_errors_exit_nonzero_without_partial_output(self):
        code, out, err = self.solve_file("A + B = 10\n")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("not fully determined", err)

    def test_missing_file_reports_an_error(self):
        code, out, err = self.run_cli([str(self.path)])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(str(self.path), err)

    def test_invalid_utf8_reports_an_error(self):
        self.path.write_bytes(b"A = 6\n\xff")
        code, out, err = self.run_cli([str(self.path)])
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("decode", err)

    def test_blank_file_succeeds_without_output(self):
        code, out, err = self.solve_file("\n  \n")
        self.assertEqual((code, out, err), (0, "", ""))

    def test_literal_multiline_text_succeeds_without_reading_a_file(self):
        with patch("typecalc_cli.cli.Path.read_text") as read:
            result = self.run_cli(["--text", "B + A = 10\n\nA = 6"])
        read.assert_not_called()
        self.assertEqual(result, (0, "A = 6.0\nB = 4.0\n", ""))

    def test_empty_literal_text_succeeds_without_output(self):
        self.assertEqual(self.run_cli(["--text", ""]), (0, "", ""))

    def test_literal_text_errors_preserve_line_numbers(self):
        code, out, err = self.run_cli(["--text", "A = 6\n\nB ="])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("typecalc: Line 3:", err)

    def test_literal_text_can_start_with_a_minus_sign(self):
        self.assertEqual(self.run_cli(["--text=-A = 6"]), (0, "A = -6.0\n", ""))

    def test_file_and_text_cannot_be_combined(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
            main([str(self.path), "--text", "A = 6"])
        self.assertEqual(raised.exception.code, 2)

    def test_file_argument_is_required(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
            main([])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("usage: typecalc", err.getvalue())
        self.assertIn("file", err.getvalue())

    def test_unsupported_system_reports_an_error(self):
        with patch(
            "typecalc_cli.cli.solve",
            side_effect=NotImplementedError("Unsupported system"),
        ):
            code, out, err = self.solve_file("A = 6\n")
        self.assertEqual((code, out, err), (1, "", "typecalc: Unsupported system\n"))


if __name__ == "__main__":
    unittest.main()
