"""CommandExecutor: executes SolarBASIC statements and manages runtime state."""
from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence

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
    PrintStatement,
    ReturnStatement,
    RunStatement,
    Statement,
    UnaryExpression,
    WendStatement,
    WhileStatement,
)
from .parser import CommandParser
from .version import AUTHOR as SOLARBASIC_AUTHOR, TAGLINE, VERSION_LABEL as SOLARBASIC_VERSION

DEFAULT_STEP_LIMIT = 10_000


class CommandExecutor:
    """Execute SolarBASIC statements through the v1.0.0 feature set."""

    def __init__(
        self,
        line_storage: LineStorage,
        parser: CommandParser,
        *,
        debug: bool = False,
        step_limit: int = DEFAULT_STEP_LIMIT,
    ) -> None:
        self._line_storage = line_storage
        self._parser = parser
        self._functions: Dict[str, FunctionDefinition] = {}
        self._global_env: Dict[str, int] = {}
        self._env_stack: List[Dict[str, int]] = []
        self._led_matrix = LedMatrix()
        self._debug = debug
        self._step_limit = step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT
        self._builtin_functions = {
            "RND": self._builtin_rnd,
            "ABS": self._builtin_abs,
            "SGN": self._builtin_sgn,
        }

    def register_functions(self, functions: Dict[str, FunctionDefinition]) -> None:
        """Replace the known function table (invoked before RUN executes)."""

        self._functions = functions

    def execute(self, statement: Statement) -> ExecutionResult:
        return self._execute(statement, inside_function=False)

    def execute_in_function(self, statement: Statement) -> ExecutionResult:
        return self._execute(statement, inside_function=True)

    def _execute(self, statement: Statement, inside_function: bool) -> ExecutionResult:
        if isinstance(statement, PrintStatement):
            self._execute_print(statement)
        elif isinstance(statement, AssignmentStatement):
            self._execute_assignment(statement, inside_function)
        elif isinstance(statement, LedStatement):
            self._execute_led(statement)
        elif isinstance(statement, IfStatement):
            return self._execute_if(statement, inside_function)
        elif isinstance(statement, GotoStatement):
            return ExecutionResult(goto_target=statement.target_line)
        elif isinstance(statement, GosubStatement):
            if inside_function:
                print("GOSUB is not supported inside functions.")
                return ExecutionResult(signal=ExecutionSignal.CONTINUE)
            return ExecutionResult(gosub_target=statement.target_line)
        elif isinstance(statement, ListStatement):
            self._execute_list()
        elif isinstance(statement, ListFunctionsStatement):
            self._execute_list_functions()
        elif isinstance(statement, NewStatement):
            self._execute_new()
        elif isinstance(statement, RunStatement):
            return self._execute_run()
        elif isinstance(statement, HelpStatement):
            self._execute_help()
        elif isinstance(statement, AboutStatement):
            self._execute_about()
        elif isinstance(statement, ExitStatement):
            return ExecutionResult(signal=ExecutionSignal.EXIT)
        elif isinstance(statement, (WhileStatement, WendStatement)):
            self._reject_block_statement()
        elif isinstance(statement, (FuncStatement, EndFuncStatement)):
            self._reject_function_statement()
        elif isinstance(statement, ReturnStatement):
            return self._execute_return(statement, inside_function)
        else:
            raise ValueError(f"Unsupported statement type: {statement!r}")

        return ExecutionResult(signal=ExecutionSignal.CONTINUE)

    def _execute_print(self, statement: PrintStatement) -> None:
        argument = statement.argument
        if argument is None:
            print()
            return

        if isinstance(argument, str):
            print(argument)
            return

        try:
            value = self._evaluate_expression(argument)
        except ZeroDivisionError:
            print("Runtime error: division by zero in PRINT expression.")
            return
        except EvaluationError as exc:
            print(f"Runtime error in PRINT expression: {exc}")
            return

        print(value)

    def _execute_assignment(self, statement: AssignmentStatement, inside_function: bool) -> None:
        try:
            value = self._evaluate_expression(statement.expression)
        except ZeroDivisionError:
            print(f"Runtime error: division by zero in assignment to {statement.name}.")
            return
        except EvaluationError as exc:
            print(f"Runtime error in assignment to {statement.name}: {exc}")
            return

        self._assign(
            statement.name, value, inside_function=inside_function, force_global=statement.force_global
        )

    def _assign(self, name: str, value: int, *, inside_function: bool, force_global: bool) -> None:
        if force_global:
            self._global_env[name] = value
            return

        if inside_function:
            if not self._env_stack:
                self._env_stack.append({})
            self._env_stack[-1][name] = value
            return

        self._global_env[name] = value

    def evaluate_expression(self, expression: Expression) -> int:
        """Public hook so other components (ProgramRunner) can reuse evaluation."""

        return self._evaluate_expression(expression)

    def _evaluate_expression(self, expression: Expression) -> int:
        if isinstance(expression, NumberLiteral):
            return expression.value

        if isinstance(expression, IdentifierExpression):
            return self._lookup_identifier(expression.name)

        if isinstance(expression, UnaryExpression):
            value = self._evaluate_expression(expression.operand)
            if expression.operator == "-":
                return -value
            raise ValueError(f"Unsupported unary operator {expression.operator!r}")

        if isinstance(expression, BinaryExpression):
            left = self._evaluate_expression(expression.left)
            right = self._evaluate_expression(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
            if expression.operator == "/":
                if right == 0:
                    raise ZeroDivisionError
                return left // right
            if expression.operator == "=":
                return 1 if left == right else 0
            if expression.operator == "<>":
                return 1 if left != right else 0
            if expression.operator == "<":
                return 1 if left < right else 0
            if expression.operator == ">":
                return 1 if left > right else 0
            if expression.operator == "<=":
                return 1 if left <= right else 0
            if expression.operator == ">=":
                return 1 if left >= right else 0
            raise ValueError(f"Unsupported binary operator {expression.operator!r}")

        if isinstance(expression, FunctionCallExpression):
            return self._invoke_function(expression)

        raise ValueError(f"Unknown expression node: {expression!r}")

    def _lookup_identifier(self, name: str) -> int:
        for env in reversed(self._env_stack):
            if name in env:
                return env[name]
        if name in self._global_env:
            return self._global_env[name]
        raise EvaluationError(f"Undefined variable {name}")

    def _invoke_function(self, expression: FunctionCallExpression) -> int:
        builtin = self._builtin_functions.get(expression.name)
        if builtin is not None:
            return builtin(expression.arguments)

        function = self._functions.get(expression.name)
        if function is None:
            raise EvaluationError(f"Unknown function '{expression.name}'.")

        if len(expression.arguments) != len(function.parameters):
            raise EvaluationError(
                f"Function '{expression.name}' expects {len(function.parameters)} argument(s) but got {len(expression.arguments)}."
            )

        arg_values: List[int] = []
        for arg in expression.arguments:
            arg_values.append(self._evaluate_expression(arg))

        new_env = {param: value for param, value in zip(function.parameters, arg_values)}
        self._env_stack.append(new_env)
        try:
            return self._run_function_body(function)
        finally:
            self._env_stack.pop()

    def _builtin_rnd(self, arguments: Sequence[Expression]) -> int:
        if len(arguments) != 1:
            raise EvaluationError("Builtin RND expects exactly 1 argument.")

        limit = self._evaluate_expression(arguments[0])
        if limit <= 0:
            return 0
        return random.randrange(limit)

    def _builtin_abs(self, arguments: Sequence[Expression]) -> int:
        if len(arguments) != 1:
            raise EvaluationError("Builtin ABS expects exactly 1 argument.")

        value = self._evaluate_expression(arguments[0])
        return abs(value)

    def _builtin_sgn(self, arguments: Sequence[Expression]) -> int:
        if len(arguments) != 1:
            raise EvaluationError("Builtin SGN expects exactly 1 argument.")

        value = self._evaluate_expression(arguments[0])
        if value < 0:
            return -1
        if value > 0:
            return 1
        return 0

    def _run_function_body(self, function: FunctionDefinition) -> int:
        body = function.body
        idx = 0
        while idx < len(body):
            line_number, statement = body[idx]
            if statement is None:
                idx += 1
                continue

            if isinstance(statement, WhileStatement):
                skip_idx = function.while_to_wend.get(idx)
                if skip_idx is None:
                    print(
                        f"Internal error: WHILE at line {line_number} is missing loop metadata inside function {function.name}."
                    )
                    return 0
                try:
                    condition_value = self._evaluate_expression(statement.condition)
                except ZeroDivisionError:
                    print(
                        f"Runtime error: division by zero in WHILE condition on line {line_number} of function {function.name}."
                    )
                    return 0
                except EvaluationError as exc:
                    print(
                        f"Runtime error in WHILE condition on line {line_number} of function {function.name}: {exc}"
                    )
                    return 0

                if condition_value == 0:
                    idx = skip_idx + 1
                    continue

                idx += 1
                continue

            if isinstance(statement, WendStatement):
                start_idx = function.wend_to_while.get(idx)
                if start_idx is None:
                    print(
                        f"Internal error: WEND at line {line_number} is missing loop metadata inside function {function.name}."
                    )
                    return 0
                idx = start_idx
                continue

            result = self._execute(statement, inside_function=True)
            if result.signal is ExecutionSignal.EXIT:
                print("EXIT cannot be used inside functions that return values.")
                return 0
            if result.goto_target is not None:
                print("GOTO is not supported inside functions.")
                return 0
            if result.gosub_target is not None:
                print("GOSUB is not supported inside functions.")
                return 0
            if result.gosub_return:
                print("Line-level RETURN is not supported inside functions.")
                return 0
            if result.return_value is not None:
                return result.return_value

            idx += 1

        return 0

    def _execute_if(self, statement: IfStatement, inside_function: bool) -> ExecutionResult:
        try:
            condition_value = self._evaluate_expression(statement.condition)
        except EvaluationError as exc:
            print(f"Runtime error in IF condition: {exc}")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)
        except ZeroDivisionError:
            print("Runtime error: division by zero in IF condition.")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)

        if condition_value != 0:
            return self._execute(statement.consequence, inside_function)
        return ExecutionResult(signal=ExecutionSignal.CONTINUE)

    def _reject_block_statement(self) -> None:
        print("WHILE/WEND blocks are only available when RUN executes stored program lines.")

    def _reject_function_statement(self) -> None:
        print("FUNC/ENDFUNC blocks are only available when RUN executes stored program lines.")

    def _execute_led(self, statement: LedStatement) -> None:
        try:
            self._led_matrix.set_pixel(statement.x, statement.y, statement.on)
        except ValueError as exc:
            print(f"LED error: {exc}")
            return

        state = "ON" if statement.on else "OFF"
        print(f"[LED] ({statement.x}, {statement.y}) -> {state}")
        for row in self._led_matrix.render_lines():
            print(f"        {row}")

    def _execute_return(self, statement: ReturnStatement, inside_function: bool) -> ExecutionResult:
        if not inside_function:
            if statement.value is not None:
                print("Line-level RETURN does not take a value; use RETURN <expr> inside FUNC.")
                return ExecutionResult(signal=ExecutionSignal.CONTINUE)
            return ExecutionResult(signal=ExecutionSignal.CONTINUE, gosub_return=True)

        try:
            # Fix: use explicit `is not None` to correctly handle RETURN 0
            value = self._evaluate_expression(statement.value) if statement.value is not None else 0
        except EvaluationError as exc:
            print(f"Runtime error in RETURN value: {exc}")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)
        except ZeroDivisionError:
            print("Runtime error: division by zero in RETURN expression.")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)

        return ExecutionResult(signal=ExecutionSignal.CONTINUE, return_value=value)

    def _execute_list(self) -> None:
        snapshot = self._line_storage.snapshot()
        if not snapshot:
            print("No program lines stored.")
            return

        for line_number in sorted(snapshot):
            print(f"{line_number} {snapshot[line_number]}")

    def _execute_new(self) -> None:
        self._line_storage.clear()
        self._functions.clear()
        self._led_matrix.clear()
        self._global_env.clear()
        # Fix: also clear any leftover function call frames
        self._env_stack.clear()
        print("Program cleared.")

    def _execute_run(self) -> ExecutionResult:
        # Import here to avoid circular import at module load time
        from .runner import ProgramRunner

        runner = ProgramRunner(
            parser=self._parser,
            executor=self,
            step_limit=self._step_limit,
            debug=self._debug,
        )
        return runner.run(self._line_storage.snapshot())

    def _execute_list_functions(self) -> None:
        if not self._functions:
            print("No functions defined.")
            return

        for name in sorted(self._functions):
            params = ", ".join(self._functions[name].parameters)
            print(f"{name}({params})")

    def _execute_help(self) -> None:
        print(f"SolarBASIC {SOLARBASIC_VERSION} — {TAGLINE}")
        print("Commands:")
        print("  PRINT <expr|string>          — output text or expression results")
        print("  X = <expr>                   — assign (inside FUNC stays local by default)")
        print("  LET X = <expr>               — force a global assignment even inside FUNC")
        print("  Built-ins: RND, ABS, SGN     — numeric helpers (RND<=0 returns 0)")
        print("  GOSUB <line> / RETURN        — line subroutines (program mode only)")
        print("  LED x y ON|OFF               — toggle the simulated 5x5 LED matrix")
        print("  LIST [FUNCS]/LISTF           — list stored lines or function headers")
        print("  NEW / RUN / EXIT             — manage the stored program")
        print("  IF / GOTO / WHILE / FUNC     — structured flow control")
        print("  HELP / ABOUT                 — show this summary or project info")

    def _execute_about(self) -> None:
        features = [
            "PRINT",
            "ASSIGN",
            "IF",
            "GOTO",
            "GOSUB",
            "WHILE",
            "FUNC",
            "RETURN",
            "RND/ABS/SGN",
            "LED",
        ]
        print(f"SolarBASIC {SOLARBASIC_VERSION} — {TAGLINE}")
        print(f"Author: {SOLARBASIC_AUTHOR}")
        print("Stage: 14 (v1.0.0 release)")
        print(f"Features: {', '.join(features)}")
