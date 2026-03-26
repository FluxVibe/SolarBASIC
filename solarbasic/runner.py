"""ProgramRunner: executes stored SolarBASIC program lines with full control flow."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from .ast_nodes import (
    EndFuncStatement,
    EvaluationError,
    ExecutionResult,
    ExecutionSignal,
    FuncStatement,
    FunctionDefinition,
    Statement,
    WendStatement,
    WhileStatement,
)
from .executor import CommandExecutor, DEFAULT_STEP_LIMIT
from .parser import CommandParser
from .tokenizer import TokenizerError

# Re-export ParseError for callers that import it from here
from .ast_nodes import ParseError


class ProgramRunner:
    """Execute stored SolarBASIC program lines with GOTO support."""

    def __init__(
        self,
        parser: CommandParser,
        executor: CommandExecutor,
        *,
        step_limit: int = DEFAULT_STEP_LIMIT,
        debug: bool = False,
    ) -> None:
        self._parser = parser
        self._executor = executor
        self._step_limit = step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT
        self._debug = debug

    def run(self, program_lines: Dict[int, str]) -> ExecutionResult:
        if not program_lines:
            print("No program stored. Use line numbers to add code before RUN.")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)

        ordered = sorted(program_lines.items())
        compiled: List[Tuple[int, Optional[Statement]]] = []
        for line_number, source in ordered:
            normalized = source.strip()
            if not normalized:
                compiled.append((line_number, None))
                continue
            try:
                statement = self._parser.parse(normalized)
            except (ParseError, TokenizerError) as exc:
                print(f"RUN parse error on line {line_number}: {exc}")
                return ExecutionResult(signal=ExecutionSignal.CONTINUE)
            compiled.append((line_number, statement))

        extraction = self._extract_functions(compiled)
        if extraction is None:
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)
        compiled, functions = extraction
        self._executor.register_functions(functions)

        line_to_index = {line: idx for idx, (line, _) in enumerate(compiled)}
        while_to_wend, wend_to_while = self._build_loop_maps(compiled)
        if while_to_wend is None:
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)

        gosub_stack: List[int] = []
        idx = 0
        steps = 0
        while idx < len(compiled):
            line_number, statement = compiled[idx]
            if statement is None:
                idx += 1
                continue

            if isinstance(statement, (FuncStatement, EndFuncStatement)):
                idx += 1
                continue

            steps += 1
            if steps > self._step_limit:
                print("ERROR: Step limit exceeded (possible infinite loop)")
                return ExecutionResult(signal=ExecutionSignal.CONTINUE)

            if self._debug:
                print(f"TRACE: line {line_number}")

            if isinstance(statement, WhileStatement):
                skip_idx = while_to_wend.get(idx)
                if skip_idx is None:
                    print(f"Internal error: WHILE at line {line_number} is missing loop metadata.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                try:
                    condition_value = self._executor.evaluate_expression(statement.condition)
                except ZeroDivisionError:
                    print(f"Runtime error: division by zero in WHILE condition on line {line_number}.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                except Exception as exc:
                    print(f"Runtime error in WHILE condition on line {line_number}: {exc}")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)

                if condition_value == 0:
                    idx = skip_idx + 1
                    continue

                idx += 1
                continue

            if isinstance(statement, WendStatement):
                start_idx = wend_to_while.get(idx)
                if start_idx is None:
                    print(f"Internal error: WEND at line {line_number} is missing loop metadata.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                idx = start_idx
                continue

            result = self._executor.execute(statement)
            if result.signal is ExecutionSignal.EXIT:
                return result

            if result.goto_target is not None:
                target = result.goto_target
                if target not in line_to_index:
                    print(f"GOTO target {target} does not exist. Stopping RUN.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                idx = line_to_index[target]
                continue

            if result.gosub_target is not None:
                target = result.gosub_target
                if target not in line_to_index:
                    print(f"GOSUB target {target} does not exist. Stopping RUN.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                gosub_stack.append(idx + 1)
                if self._debug:
                    print(f"TRACE: GOSUB to line {target} (return -> index {gosub_stack[-1]})")
                idx = line_to_index[target]
                continue

            if result.gosub_return:
                if not gosub_stack:
                    print("Runtime error: RETURN without GOSUB.")
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                idx = gosub_stack.pop()
                if self._debug:
                    print(f"TRACE: RETURN to stored location (index {idx})")
                continue

            if result.return_value is not None:
                print("RETURN cannot be used outside of a function definition. Stopping RUN.")
                return ExecutionResult(signal=ExecutionSignal.CONTINUE)

            idx += 1

        return ExecutionResult(signal=ExecutionSignal.CONTINUE)

    def _build_loop_maps(
        self, compiled: List[Tuple[int, Optional[Statement]]]
    ) -> Tuple[Optional[Dict[int, int]], Optional[Dict[int, int]]]:
        """Build WHILE→WEND and WEND→WHILE index mappings for the main program."""

        while_stack: List[Tuple[int, int]] = []
        while_to_wend: Dict[int, int] = {}
        wend_to_while: Dict[int, int] = {}

        for idx, (line_number, statement) in enumerate(compiled):
            if isinstance(statement, WhileStatement):
                while_stack.append((idx, line_number))
            elif isinstance(statement, WendStatement):
                if not while_stack:
                    print(f"RUN parse error: WEND at line {line_number} does not have a matching WHILE.")
                    return None, None
                start_idx, _ = while_stack.pop()
                while_to_wend[start_idx] = idx
                wend_to_while[idx] = start_idx

        if while_stack:
            _, line_number = while_stack[-1]
            print(f"RUN parse error: WHILE at line {line_number} is missing a WEND.")
            return None, None

        return while_to_wend, wend_to_while

    def _extract_functions(
        self, compiled: List[Tuple[int, Optional[Statement]]]
    ) -> Optional[Tuple[List[Tuple[int, Optional[Statement]]], Dict[str, FunctionDefinition]]]:
        filtered: List[Tuple[int, Optional[Statement]]] = []
        functions: Dict[str, FunctionDefinition] = {}
        idx = 0
        while idx < len(compiled):
            line_number, statement = compiled[idx]
            if isinstance(statement, FuncStatement):
                collection = self._collect_function(idx, compiled)
                if collection is None:
                    return None
                definition, end_idx = collection
                if definition.name in functions:
                    print(f"RUN parse error: function {definition.name} is defined more than once.")
                    return None
                functions[definition.name] = definition
                idx = end_idx + 1
                continue
            if isinstance(statement, EndFuncStatement):
                print(f"RUN parse error: ENDFUNC at line {line_number} does not have a matching FUNC.")
                return None
            filtered.append((line_number, statement))
            idx += 1

        return filtered, functions

    def _collect_function(
        self, start_idx: int, compiled: List[Tuple[int, Optional[Statement]]]
    ) -> Optional[Tuple[FunctionDefinition, int]]:
        func_line, func_statement = compiled[start_idx]
        if not isinstance(func_statement, FuncStatement):
            raise ValueError("_collect_function must start at a FUNC statement")

        body: List[Tuple[int, Optional[Statement]]] = []
        idx = start_idx + 1
        while idx < len(compiled):
            line_number, statement = compiled[idx]
            if isinstance(statement, FuncStatement):
                print(f"RUN parse error: nested FUNC starting at line {line_number} is not supported.")
                return None
            if isinstance(statement, EndFuncStatement):
                while_to_wend, wend_to_while = self._build_function_loop_maps(body, func_statement.name)
                if while_to_wend is None or wend_to_while is None:
                    return None
                definition = FunctionDefinition(
                    name=func_statement.name,
                    parameters=func_statement.parameters,
                    body=body,
                    while_to_wend=while_to_wend,
                    wend_to_while=wend_to_while,
                )
                return definition, idx
            body.append((line_number, statement))
            idx += 1

        print(f"RUN parse error: FUNC at line {func_line} is missing an ENDFUNC.")
        return None

    def _build_function_loop_maps(
        self, body: List[Tuple[int, Optional[Statement]]], function_name: str
    ) -> Tuple[Optional[Dict[int, int]], Optional[Dict[int, int]]]:
        while_stack: List[Tuple[int, int]] = []
        while_to_wend: Dict[int, int] = {}
        wend_to_while: Dict[int, int] = {}
        for idx, (line_number, statement) in enumerate(body):
            if isinstance(statement, WhileStatement):
                while_stack.append((idx, line_number))
            elif isinstance(statement, WendStatement):
                if not while_stack:
                    print(
                        f"RUN parse error: WEND at line {line_number} inside function {function_name} does not have a matching WHILE."
                    )
                    return None, None
                start_idx, _ = while_stack.pop()
                while_to_wend[start_idx] = idx
                wend_to_while[idx] = start_idx

        if while_stack:
            _, line_number = while_stack[-1]
            print(
                f"RUN parse error: WHILE at line {line_number} inside function {function_name} is missing a WEND."
            )
            return None, None

        return while_to_wend, wend_to_while
