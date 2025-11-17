"""Unit tests for key SolarBASIC language features."""
from __future__ import annotations

import io
import random
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

from solarbasic.interpreter import (
    CommandExecutor,
    CommandParser,
    ExecutionSignal,
    LineStorage,
    ProgramRunner,
)
from solarbasic.version import VERSION, VERSION_LABEL


class SolarBasicLanguageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = CommandParser()
        self.storage = LineStorage()
        self.executor = CommandExecutor(self.storage, self.parser)

    def _capture_output(self, command: str) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse(command))
        return buffer.getvalue().strip()

    def test_expression_precedence(self) -> None:
        self.assertEqual(self._capture_output("PRINT 1+2*3"), "7")
        self.assertEqual(self._capture_output("PRINT -(1+2)"), "-3")

    def test_if_then_branching(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse("IF 2 > 1 THEN PRINT 42"))
            self.executor.execute(self.parser.parse("IF 0 THEN PRINT 99"))
        self.assertEqual(buffer.getvalue().strip(), "42")

    def test_assignment_global(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse("LET N = 3"))
            self.executor.execute(self.parser.parse("PRINT N"))
        self.assertEqual(buffer.getvalue().strip(), "3")

    def test_assignment_reuse(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse("N = 1"))
            self.executor.execute(self.parser.parse("N = N + 2"))
            self.executor.execute(self.parser.parse("PRINT N"))
        self.assertEqual(buffer.getvalue().strip(), "3")

    def test_while_wend_structure(self) -> None:
        self.storage.set_line(10, "PRINT 1")
        self.storage.set_line(20, "WHILE 0")
        self.storage.set_line(30, "PRINT 2")
        self.storage.set_line(40, "WEND")
        self.storage.set_line(50, "PRINT 3")

        runner = ProgramRunner(self.parser, self.executor)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            runner.run(self.storage.snapshot())
        self.assertEqual(buffer.getvalue().strip().splitlines(), ["1", "3"])

    def test_function_return_value(self) -> None:
        self.storage.set_line(10, "FUNC ADD(A,B)")
        self.storage.set_line(20, "RETURN A+B")
        self.storage.set_line(30, "ENDFUNC")
        self.storage.set_line(40, "PRINT ADD(2,3)")

        runner = ProgramRunner(self.parser, self.executor)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = runner.run(self.storage.snapshot())
        self.assertEqual(buffer.getvalue().strip(), "5")
        self.assertEqual(result.signal, ExecutionSignal.CONTINUE)

    def test_assignment_local_scope(self) -> None:
        self.storage.set_line(10, "FUNC INC(N)")
        self.storage.set_line(20, "N = N + 1")
        self.storage.set_line(30, "RETURN N")
        self.storage.set_line(40, "ENDFUNC")
        self.storage.set_line(50, "PRINT INC(5)")

        runner = ProgramRunner(self.parser, self.executor)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip(), "6")
        self.assertNotIn("N", self.executor._global_env)

    def test_undefined_variable_errors(self) -> None:
        message = self._capture_output("PRINT X")
        self.assertIn("Undefined variable X", message)

    def test_assignment_prefers_local_scope(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse("LET N = 10"))

            self.storage.set_line(10, "FUNC BUMP()")
            self.storage.set_line(20, "N = N + 5")
            self.storage.set_line(30, "RETURN N")
            self.storage.set_line(40, "ENDFUNC")
            self.storage.set_line(50, "PRINT BUMP()")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip(), "15")
        self.assertEqual(self.executor._global_env.get("N"), 10)

    def test_let_always_sets_global(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "FUNC MAKE(N)")
            self.storage.set_line(20, "LET N = 99")
            self.storage.set_line(30, "RETURN N")
            self.storage.set_line(40, "ENDFUNC")
            self.storage.set_line(50, "PRINT MAKE(5)")
            self.storage.set_line(60, "PRINT N")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip().splitlines(), ["5", "99"])
        self.assertEqual(self.executor._global_env.get("N"), 99)

    def test_gosub_basic_flow(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "GOSUB 100")
            self.storage.set_line(20, "PRINT 1")
            self.storage.set_line(30, "EXIT")
            self.storage.set_line(100, "PRINT 2")
            self.storage.set_line(110, "RETURN")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip().splitlines(), ["2", "1"])

    def test_gosub_nested_flow(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "GOSUB 50")
            self.storage.set_line(20, "PRINT 0")
            self.storage.set_line(30, "EXIT")
            self.storage.set_line(50, "PRINT 1")
            self.storage.set_line(60, "GOSUB 80")
            self.storage.set_line(70, "RETURN")
            self.storage.set_line(80, "PRINT 2")
            self.storage.set_line(90, "RETURN")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip().splitlines(), ["1", "2", "0"])

    def test_return_without_gosub(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "RETURN")
            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertIn("RETURN without GOSUB", buffer.getvalue())

    def test_gosub_blocked_inside_function(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "FUNC BAD()")
            self.storage.set_line(20, "GOSUB 100")
            self.storage.set_line(30, "RETURN 0")
            self.storage.set_line(40, "ENDFUNC")
            self.storage.set_line(50, "PRINT BAD()")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertIn("GOSUB is not supported inside functions", buffer.getvalue())

    def test_builtin_abs_and_sgn(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.executor.execute(self.parser.parse("PRINT SGN(-5)"))
            self.executor.execute(self.parser.parse("PRINT SGN(0)"))
            self.executor.execute(self.parser.parse("PRINT SGN(5)"))
            self.executor.execute(self.parser.parse("PRINT ABS(-3)"))

        self.assertEqual(buffer.getvalue().strip().splitlines(), ["-1", "0", "1", "3"])

    def test_builtin_rnd_range(self) -> None:
        random.seed(0)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            for _ in range(5):
                self.executor.execute(self.parser.parse("PRINT RND(10)"))
            self.executor.execute(self.parser.parse("PRINT RND(0)"))
        values = [int(line) for line in buffer.getvalue().strip().splitlines()]
        for value in values:
            self.assertGreaterEqual(value, 0)
            self.assertLess(value, 10)
        self.assertEqual(values[-1], 0)

    def test_builtin_precedence_over_user_function(self) -> None:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.storage.set_line(10, "FUNC ABS(X)")
            self.storage.set_line(20, "RETURN 123")
            self.storage.set_line(30, "ENDFUNC")
            self.storage.set_line(40, "PRINT ABS(-4)")

            runner = ProgramRunner(self.parser, self.executor)
            runner.run(self.storage.snapshot())

        self.assertEqual(buffer.getvalue().strip(), "4")

    def test_cli_version_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "main.py", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), f"SolarBASIC {VERSION_LABEL}")


if __name__ == "__main__":
    unittest.main()
