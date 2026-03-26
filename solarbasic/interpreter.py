"""SolarBASIC interpreter — public API re-exports for backward compatibility.

The implementation has been split into focused modules:
  ast_nodes.py  — AST node types, result types, and shared utilities
  parser.py     — ExpressionParser and CommandParser
  executor.py   — CommandExecutor (statement execution and runtime state)
  runner.py     — ProgramRunner (line-by-line program execution)
  repl.py       — SolarBasicRepl and run_script_file

Import from those modules directly for new code, or continue importing from
here for backward compatibility.
"""
from __future__ import annotations

from .ast_nodes import (
    AboutStatement,
    AssignmentStatement,
    BinaryExpression,
    EndFuncStatement,
    EvaluationError,
    ExecutionResult,
    ExecutionSignal,
    Expression,
    ExitStatement,
    FuncStatement,
    FunctionCallExpression,
    FunctionDefinition,
    GosubStatement,
    GotoStatement,
    HelpStatement,
    IdentifierExpression,
    IfStatement,
    LedMatrix,
    LedStatement,
    LineStorage,
    ListFunctionsStatement,
    ListStatement,
    NewStatement,
    NumberLiteral,
    ParseError,
    PrintStatement,
    ReturnStatement,
    RunStatement,
    Statement,
    StoreAction,
    StoreResult,
    UnaryExpression,
    WendStatement,
    WhileStatement,
    split_line_number,
)
from .executor import CommandExecutor, DEFAULT_STEP_LIMIT
from .parser import CommandParser, ExpressionParser
from .repl import SolarBasicRepl, run_script_file
from .runner import ProgramRunner

__all__ = [
    # ast_nodes
    "AboutStatement",
    "AssignmentStatement",
    "BinaryExpression",
    "EndFuncStatement",
    "EvaluationError",
    "ExecutionResult",
    "ExecutionSignal",
    "Expression",
    "ExitStatement",
    "FuncStatement",
    "FunctionCallExpression",
    "FunctionDefinition",
    "GosubStatement",
    "GotoStatement",
    "HelpStatement",
    "IdentifierExpression",
    "IfStatement",
    "LedMatrix",
    "LedStatement",
    "LineStorage",
    "ListFunctionsStatement",
    "ListStatement",
    "NewStatement",
    "NumberLiteral",
    "ParseError",
    "PrintStatement",
    "ReturnStatement",
    "RunStatement",
    "Statement",
    "StoreAction",
    "StoreResult",
    "UnaryExpression",
    "WendStatement",
    "WhileStatement",
    "split_line_number",
    # executor
    "CommandExecutor",
    "DEFAULT_STEP_LIMIT",
    # parser
    "CommandParser",
    "ExpressionParser",
    # repl
    "SolarBasicRepl",
    "run_script_file",
    # runner
    "ProgramRunner",
]
