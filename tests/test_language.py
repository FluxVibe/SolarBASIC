"""Unit tests for key SolarBASIC language features."""
from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from solarbasic.interpreter import (
    CommandExecutor,
    CommandParser,
    ExecutionSignal,
    LineStorage,
    ProgramRunner,
)


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


if __name__ == "__main__":
    unittest.main()
