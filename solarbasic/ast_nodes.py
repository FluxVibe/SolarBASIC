"""AST node definitions, result types, and shared utilities for SolarBASIC."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Union


# ---------------------------------------------------------------------------
# Line-storage helpers
# ---------------------------------------------------------------------------

class StoreAction(Enum):
    """Describe how a line update modified the program listing."""

    ADDED = auto()
    UPDATED = auto()
    DELETED = auto()
    UNCHANGED = auto()


@dataclass
class StoreResult:
    """Return information about a program-line mutation."""

    action: StoreAction
    line_number: int


class LineStorage:
    """Keep track of numbered program lines for SolarBASIC."""

    def __init__(self) -> None:
        self._lines: Dict[int, str] = {}

    def set_line(self, line_number: int, content: str) -> StoreResult:
        """Store or delete a line depending on whether content exists."""

        if content:
            action = StoreAction.UPDATED if line_number in self._lines else StoreAction.ADDED
            self._lines[line_number] = content
            return StoreResult(action=action, line_number=line_number)

        if line_number in self._lines:
            del self._lines[line_number]
            return StoreResult(action=StoreAction.DELETED, line_number=line_number)

        return StoreResult(action=StoreAction.UNCHANGED, line_number=line_number)

    def snapshot(self) -> Dict[int, str]:
        """Return a shallow copy of the stored program lines."""

        return dict(self._lines)

    def clear(self) -> None:
        """Remove every stored line from the buffer."""

        self._lines.clear()


def split_line_number(raw_input: str) -> Optional[Tuple[int, str]]:
    """Split "10 PRINT" into (10, "PRINT"), ignoring leading spaces."""

    stripped = raw_input.lstrip()
    if not stripped or not stripped[0].isdigit():
        return None

    idx = 0
    while idx < len(stripped) and stripped[idx].isdigit():
        idx += 1

    line_number = int(stripped[:idx])
    remainder = stripped[idx:].lstrip()
    return line_number, remainder


# ---------------------------------------------------------------------------
# Error and signal types
# ---------------------------------------------------------------------------

class ParseError(Exception):
    """Raised when user input cannot be parsed into a statement."""


class EvaluationError(Exception):
    """Raised when an expression cannot be evaluated."""


class ExecutionSignal(Enum):
    """Communicate when a statement triggers a REPL exit."""

    CONTINUE = auto()
    EXIT = auto()


@dataclass
class ExecutionResult:
    """Bundle the signal plus optional control-flow side information."""

    signal: ExecutionSignal = ExecutionSignal.CONTINUE
    goto_target: Optional[int] = None
    gosub_target: Optional[int] = None
    gosub_return: bool = False
    return_value: Optional[int] = None


# ---------------------------------------------------------------------------
# LED matrix
# ---------------------------------------------------------------------------

class LedMatrix:
    """Keep a 5x5 LED grid state for friendlier LED output."""

    WIDTH = 5
    HEIGHT = 5

    def __init__(self) -> None:
        self._grid = [[False for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]

    def set_pixel(self, x: int, y: int, on: bool) -> None:
        if not 0 <= x < self.WIDTH or not 0 <= y < self.HEIGHT:
            raise ValueError(
                f"Coordinates must be between 0 and {self.WIDTH - 1} for X and 0 and {self.HEIGHT - 1} for Y."
            )
        self._grid[y][x] = on

    def clear(self) -> None:
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                self._grid[y][x] = False

    def render_lines(self) -> List[str]:
        """Return the LED grid as rows of '#' (on) and '.' (off)."""

        return ["".join("#" if cell else "." for cell in row) for row in self._grid]


# ---------------------------------------------------------------------------
# AST base classes
# ---------------------------------------------------------------------------

@dataclass
class Statement:
    """Base type for SolarBASIC statements."""


@dataclass
class Expression:
    """Base type for SolarBASIC expressions."""


# ---------------------------------------------------------------------------
# Expression nodes
# ---------------------------------------------------------------------------

@dataclass
class NumberLiteral(Expression):
    value: int


@dataclass
class IdentifierExpression(Expression):
    name: str


@dataclass
class UnaryExpression(Expression):
    operator: str
    operand: Expression


@dataclass
class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression


@dataclass
class FunctionCallExpression(Expression):
    name: str
    arguments: List[Expression]


# ---------------------------------------------------------------------------
# Statement nodes
# ---------------------------------------------------------------------------

@dataclass
class AssignmentStatement(Statement):
    name: str
    expression: Expression
    force_global: bool = False


@dataclass
class PrintStatement(Statement):
    argument: Optional[Union[str, Expression]]


@dataclass
class LedStatement(Statement):
    x: int
    y: int
    on: bool


@dataclass
class ListStatement(Statement):
    pass


@dataclass
class ListFunctionsStatement(Statement):
    pass


@dataclass
class NewStatement(Statement):
    pass


@dataclass
class RunStatement(Statement):
    pass


@dataclass
class ExitStatement(Statement):
    keyword: str


@dataclass
class IfStatement(Statement):
    condition: Expression
    consequence: Statement


@dataclass
class GotoStatement(Statement):
    target_line: int


@dataclass
class GosubStatement(Statement):
    target_line: int


@dataclass
class WhileStatement(Statement):
    condition: Expression


@dataclass
class WendStatement(Statement):
    pass


@dataclass
class FuncStatement(Statement):
    name: str
    parameters: List[str]


@dataclass
class EndFuncStatement(Statement):
    pass


@dataclass
class ReturnStatement(Statement):
    value: Optional[Expression]


@dataclass
class HelpStatement(Statement):
    pass


@dataclass
class AboutStatement(Statement):
    pass


# ---------------------------------------------------------------------------
# Function definition (runtime metadata)
# ---------------------------------------------------------------------------

@dataclass
class FunctionDefinition:
    """Store metadata for a SolarBASIC function block."""

    name: str
    parameters: List[str]
    body: List[Tuple[int, Optional[Statement]]]
    while_to_wend: Dict[int, int]
    wend_to_while: Dict[int, int]
