"""SolarBASIC interpreter components for early development stages."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import random
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .tokenizer import Token, TokenType, Tokenizer, TokenizerError
from .version import AUTHOR as SOLARBASIC_AUTHOR, TAGLINE, VERSION_LABEL as SOLARBASIC_VERSION


DEFAULT_STEP_LIMIT = 10_000


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


class ParseError(Exception):
    """Raised when user input cannot be parsed into a statement."""


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


@dataclass
class Statement:
    """Base type for SolarBASIC statements."""


@dataclass
class Expression:
    """Base type for SolarBASIC expressions."""


@dataclass
class NumberLiteral(Expression):
    value: int


@dataclass
class IdentifierExpression(Expression):
    name: str


@dataclass
class AssignmentStatement(Statement):
    name: str
    expression: Expression
    force_global: bool = False


@dataclass
class FunctionCallExpression(Expression):
    name: str
    arguments: List[Expression]


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


@dataclass
class FunctionDefinition:
    """Store metadata for a SolarBASIC function block."""

    name: str
    parameters: List[str]
    body: List[Tuple[int, Optional[Statement]]]
    while_to_wend: Dict[int, int]
    wend_to_while: Dict[int, int]


class EvaluationError(Exception):
    """Raised when an expression cannot be evaluated."""


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


class ExpressionParser:
    """Parse expression tokens into an AST."""

    def parse(self, tokens: Sequence[Token]) -> Expression:
        if not tokens:
            raise ParseError("Expression expected but not found.")

        self._tokens = list(tokens)
        self._idx = 0
        expr = self._parse_equality()
        if self._idx != len(self._tokens):
            token = self._tokens[self._idx]
            raise ParseError(
                f"Unexpected token '{token.lexeme}' at column {token.column} in expression."
            )
        return expr

    def _parse_equality(self) -> Expression:
        node = self._parse_comparison()
        while self._match_operator({"=", "<>"}):
            operator = self._previous().lexeme
            right = self._parse_comparison()
            node = BinaryExpression(operator=operator, left=node, right=right)
        return node

    def _parse_comparison(self) -> Expression:
        node = self._parse_add_sub()
        while self._match_operator({"<", ">", "<=", ">="}):
            operator = self._previous().lexeme
            right = self._parse_add_sub()
            node = BinaryExpression(operator=operator, left=node, right=right)
        return node

    def _parse_add_sub(self) -> Expression:
        node = self._parse_mul_div()
        while self._match_operator({"+", "-"}):
            operator = self._previous().lexeme
            right = self._parse_mul_div()
            node = BinaryExpression(operator=operator, left=node, right=right)
        return node

    def _parse_mul_div(self) -> Expression:
        node = self._parse_unary()
        while self._match_operator({"*", "/"}):
            operator = self._previous().lexeme
            right = self._parse_unary()
            node = BinaryExpression(operator=operator, left=node, right=right)
        return node

    def _parse_unary(self) -> Expression:
        if self._match_operator({"-"}):
            operator = self._previous().lexeme
            operand = self._parse_unary()
            return UnaryExpression(operator=operator, operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        if self._is_at_end():
            raise ParseError("Unexpected end of expression.")

        token = self._advance()

        if token.type is TokenType.NUMBER:
            return NumberLiteral(value=int(token.lexeme))

        if token.type is TokenType.IDENTIFIER:
            identifier = token.lexeme
            if self._match_punctuation("("):
                arguments = self._parse_arguments()
                return FunctionCallExpression(name=identifier.upper(), arguments=arguments)
            return IdentifierExpression(name=identifier.upper())

        if token.type is TokenType.PUNCTUATION and token.lexeme == "(":
            expr = self._parse_equality()
            if self._is_at_end() or self._peek().lexeme != ")":
                raise ParseError("Missing closing parenthesis in expression.")
            self._advance()  # consume ')'
            return expr

        raise ParseError(
            f"Unexpected token '{token.lexeme}' in expression; only integers, parentheses, unary '-', and comparison/arithmetic operators are supported."
        )

    def _parse_arguments(self) -> List[Expression]:
        arguments: List[Expression] = []
        if self._match_punctuation(")"):
            return arguments
        while True:
            arguments.append(self._parse_equality())
            if self._match_punctuation(")"):
                break
            if not self._match_punctuation(","):
                raise ParseError("Function call arguments must be separated by commas.")
        return arguments

    def _match_operator(self, operators: set[str]) -> bool:
        if self._is_at_end():
            return False
        token = self._peek()
        if token.type is TokenType.OPERATOR and token.lexeme in operators:
            self._advance()
            return True
        return False

    def _previous(self) -> Token:
        return self._tokens[self._idx - 1]

    def _advance(self) -> Token:
        token = self._tokens[self._idx]
        self._idx += 1
        return token

    def _peek(self) -> Token:
        return self._tokens[self._idx]

    def _is_at_end(self) -> bool:
        return self._idx >= len(self._tokens)

    def _match_punctuation(self, lexeme: str) -> bool:
        if self._is_at_end():
            return False
        token = self._peek()
        if token.type is TokenType.PUNCTUATION and token.lexeme == lexeme:
            self._advance()
            return True
        return False


class CommandParser:
    """Translate raw user input into structured statements."""

    def __init__(self, tokenizer: Optional[Tokenizer] = None) -> None:
        self._tokenizer = tokenizer or Tokenizer()
        self._expression_parser = ExpressionParser()

    def parse(self, source: str) -> Statement:
        tokens = self._tokenizer.tokenize(source)
        if not tokens:
            raise ParseError("No input to parse.")
        return self._parse_from_tokens(tokens)

    def _parse_from_tokens(self, tokens: Sequence[Token]) -> Statement:
        if not tokens:
            raise ParseError("No input to parse.")

        head = tokens[0]

        if self._looks_like_assignment(tokens):
            return self._parse_assignment(tokens)

        if head.type is not TokenType.KEYWORD:
            raise ParseError("Expected a keyword or assignment at the start of the command.")

        keyword = head.lexeme
        body = tokens[1:]

        if keyword == "PRINT":
            return self._parse_print(body)
        if keyword == "LED":
            return self._parse_led(body)
        if keyword == "IF":
            return self._parse_if(body)
        if keyword == "GOTO":
            return self._parse_goto(body)
        if keyword == "GOSUB":
            return self._parse_gosub(body)
        if keyword == "WHILE":
            return self._parse_while(body)
        if keyword == "WEND":
            self._ensure_no_extra(body, keyword)
            return WendStatement()
        if keyword == "FUNC":
            return self._parse_func(body)
        if keyword == "ENDFUNC":
            self._ensure_no_extra(body, keyword)
            return EndFuncStatement()
        if keyword == "RETURN":
            return self._parse_return(body)
        if keyword == "LIST":
            return self._parse_list(body)
        if keyword == "LISTF":
            self._ensure_no_extra(body, keyword)
            return ListFunctionsStatement()
        if keyword == "NEW":
            self._ensure_no_extra(body, keyword)
            return NewStatement()
        if keyword == "RUN":
            self._ensure_no_extra(body, keyword)
            return RunStatement()
        if keyword == "HELP":
            self._ensure_no_extra(body, keyword)
            return HelpStatement()
        if keyword == "ABOUT":
            self._ensure_no_extra(body, keyword)
            return AboutStatement()
        if keyword in {"EXIT", "QUIT"}:
            self._ensure_no_extra(body, keyword)
            return ExitStatement(keyword=keyword)

        raise ParseError(f"Unknown command '{keyword}'.")

    def _looks_like_assignment(self, tokens: Sequence[Token]) -> bool:
        if not tokens:
            return False
        head = tokens[0]
        if head.type is TokenType.KEYWORD and head.lexeme == "LET":
            return True
        if (
            head.type is TokenType.IDENTIFIER
            and len(tokens) >= 2
            and tokens[1].type is TokenType.OPERATOR
            and tokens[1].lexeme == "="
        ):
            return True
        return False

    def _parse_assignment(self, tokens: Sequence[Token]) -> AssignmentStatement:
        force_global = tokens[0].type is TokenType.KEYWORD and tokens[0].lexeme == "LET"
        start = 1 if force_global else 0

        if start >= len(tokens) or tokens[start].type is not TokenType.IDENTIFIER:
            raise ParseError("Assignment must specify a target identifier.")

        if start + 1 >= len(tokens):
            raise ParseError("Assignment requires '=' followed by an expression.")

        equals_token = tokens[start + 1]
        if equals_token.type is not TokenType.OPERATOR or equals_token.lexeme != "=":
            raise ParseError("Assignment requires '=' after the target name.")

        expression_tokens = tokens[start + 2 :]
        if not expression_tokens:
            raise ParseError("Assignment requires an expression after '='.")

        expression = self._expression_parser.parse(expression_tokens)
        return AssignmentStatement(
            name=tokens[start].lexeme.upper(), expression=expression, force_global=force_global
        )

    def _parse_print(self, tokens: Sequence[Token]) -> PrintStatement:
        if not tokens:
            return PrintStatement(argument=None)

        if len(tokens) == 1 and tokens[0].type is TokenType.STRING:
            return PrintStatement(argument=tokens[0].lexeme)

        expression = self._expression_parser.parse(tokens)
        return PrintStatement(argument=expression)

    def _parse_led(self, tokens: Sequence[Token]) -> LedStatement:
        if len(tokens) != 3:
            raise ParseError("LED expects: LED <x> <y> ON|OFF")

        x_token, y_token, state_token = tokens
        x = self._require_int(x_token, "x coordinate")
        y = self._require_int(y_token, "y coordinate")

        if state_token.type is not TokenType.KEYWORD or state_token.lexeme not in {"ON", "OFF"}:
            raise ParseError("LED requires ON or OFF as the final argument.")

        return LedStatement(x=x, y=y, on=state_token.lexeme == "ON")

    def _require_int(self, token: Token, name: str) -> int:
        if token.type is not TokenType.NUMBER:
            raise ParseError(f"LED {name} must be an integer.")
        return int(token.lexeme)

    def _ensure_no_extra(self, tokens: Sequence[Token], keyword: str) -> None:
        if tokens:
            raise ParseError(f"{keyword} does not take any arguments.")

    def _parse_if(self, tokens: Sequence[Token]) -> IfStatement:
        if not tokens:
            raise ParseError("IF requires a condition before THEN.")

        then_index = None
        for idx, token in enumerate(tokens):
            if token.type is TokenType.KEYWORD and token.lexeme == "THEN":
                then_index = idx
                break

        if then_index is None:
            raise ParseError("IF statement must contain THEN.")

        condition_tokens = tokens[:then_index]
        if not condition_tokens:
            raise ParseError("Condition expected before THEN.")

        consequence_tokens = tokens[then_index + 1 :]
        if not consequence_tokens:
            raise ParseError("THEN must be followed by a command.")

        condition = self._expression_parser.parse(condition_tokens)
        consequence = self._parse_from_tokens(consequence_tokens)
        return IfStatement(condition=condition, consequence=consequence)

    def _parse_goto(self, tokens: Sequence[Token]) -> GotoStatement:
        if len(tokens) != 1 or tokens[0].type is not TokenType.NUMBER:
            raise ParseError("GOTO requires exactly one line-number argument.")
        return GotoStatement(target_line=int(tokens[0].lexeme))

    def _parse_gosub(self, tokens: Sequence[Token]) -> GosubStatement:
        if len(tokens) != 1 or tokens[0].type is not TokenType.NUMBER:
            raise ParseError("GOSUB requires exactly one line-number argument.")
        return GosubStatement(target_line=int(tokens[0].lexeme))

    def _parse_while(self, tokens: Sequence[Token]) -> WhileStatement:
        if not tokens:
            raise ParseError("WHILE requires a condition expression.")
        condition = self._expression_parser.parse(tokens)
        return WhileStatement(condition=condition)

    def _parse_func(self, tokens: Sequence[Token]) -> FuncStatement:
        if not tokens or tokens[0].type is not TokenType.IDENTIFIER:
            raise ParseError("FUNC requires a function name.")
        name = tokens[0].lexeme.upper()
        idx = 1
        if idx >= len(tokens) or tokens[idx].type is not TokenType.PUNCTUATION or tokens[idx].lexeme != "(":
            raise ParseError("FUNC header must include parentheses for the parameter list.")
        params: List[str] = []
        idx += 1
        expecting_identifier = True
        while True:
            if idx >= len(tokens):
                raise ParseError("FUNC header missing closing parenthesis.")
            token = tokens[idx]
            if token.type is TokenType.PUNCTUATION and token.lexeme == ")":
                idx += 1
                break
            if expecting_identifier:
                if token.type is not TokenType.IDENTIFIER:
                    raise ParseError("Parameter names must be identifiers.")
                params.append(token.lexeme.upper())
                expecting_identifier = False
            else:
                if token.type is not TokenType.PUNCTUATION or token.lexeme != ",":
                    raise ParseError("Parameter names must be separated by commas.")
                expecting_identifier = True
            idx += 1
        if idx != len(tokens):
            raise ParseError("FUNC header should end after the closing parenthesis.")
        if len(params) != len(set(params)):
            raise ParseError("Parameter names must be unique within a function.")
        return FuncStatement(name=name, parameters=params)

    def _parse_return(self, tokens: Sequence[Token]) -> ReturnStatement:
        if not tokens:
            return ReturnStatement(value=None)
        expression = self._expression_parser.parse(tokens)
        return ReturnStatement(value=expression)

    def _parse_list(self, tokens: Sequence[Token]) -> Statement:
        if not tokens:
            return ListStatement()

        if (
            len(tokens) == 1
            and tokens[0].type is TokenType.KEYWORD
            and tokens[0].lexeme in {"FUNCS", "FUNC"}
        ):
            return ListFunctionsStatement()

        raise ParseError("LIST only supports no arguments or the FUNCS suffix.")


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
        elif isinstance(statement, FuncStatement):
            self._reject_function_statement()
        elif isinstance(statement, EndFuncStatement):
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

    def _reject_return_statement(self) -> None:
        print("RETURN is only meaningful inside a FUNC ... ENDFUNC block.")

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
            value = self._evaluate_expression(statement.value) if statement.value else 0
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
        print("Program cleared.")

    def _execute_run(self) -> ExecutionResult:
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
        while_stack: List[Tuple[int, int]] = []
        while_to_wend: Dict[int, int] = {}
        wend_to_while: Dict[int, int] = {}
        gosub_stack: List[int] = []
        for idx, (line_number, statement) in enumerate(compiled):
            if isinstance(statement, WhileStatement):
                while_stack.append((idx, line_number))
            elif isinstance(statement, WendStatement):
                if not while_stack:
                    print(
                        f"RUN parse error: WEND at line {line_number} does not have a matching WHILE."
                    )
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                start_idx, _ = while_stack.pop()
                while_to_wend[start_idx] = idx
                wend_to_while[idx] = start_idx

        if while_stack:
            _, line_number = while_stack[-1]
            print(f"RUN parse error: WHILE at line {line_number} is missing a WEND.")
            return ExecutionResult(signal=ExecutionSignal.CONTINUE)

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
                    print(
                        f"Internal error: WHILE at line {line_number} is missing loop metadata."
                    )
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                try:
                    condition_value = self._executor.evaluate_expression(statement.condition)
                except ZeroDivisionError:
                    print(
                        f"Runtime error: division by zero in WHILE condition on line {line_number}."
                    )
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)
                except Exception as exc:
                    print(
                        f"Runtime error in WHILE condition on line {line_number}: {exc}"
                    )
                    return ExecutionResult(signal=ExecutionSignal.CONTINUE)

                if condition_value == 0:
                    idx = skip_idx + 1
                    continue

                idx += 1
                continue

            if isinstance(statement, WendStatement):
                start_idx = wend_to_while.get(idx)
                if start_idx is None:
                    print(
                        f"Internal error: WEND at line {line_number} is missing loop metadata."
                    )
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


class SolarBasicRepl:
    """Provide SolarBASIC REPL behavior for the v1.0.0 release."""

    PROMPT = "READY> "

    def __init__(self, *, debug: bool = False, step_limit: int = DEFAULT_STEP_LIMIT) -> None:
        self._running = True
        self._debug = debug
        self._step_limit = step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT
        self._line_storage = LineStorage()
        self._parser = CommandParser()
        self._executor = CommandExecutor(
            self._line_storage,
            self._parser,
            debug=self._debug,
            step_limit=self._step_limit,
        )

    def start(self) -> None:
        """Show the READY> prompt repeatedly and process early-stage input."""

        self._print_banner()
        while self._running:
            try:
                user_input = input(self.PROMPT)
            except EOFError:
                print()
                self._say_goodbye()
                break
            except KeyboardInterrupt:
                print()
                self._say_goodbye()
                break

            normalized = user_input.strip()
            if not normalized:
                continue

            if self._try_store_program_line(user_input):
                continue
            if self._handle_direct_mode(normalized):
                break

    def _print_banner(self) -> None:
        stage = f"SolarBASIC {SOLARBASIC_VERSION} — {TAGLINE}"
        if self._debug:
            stage += " [debug trace]"
        print(stage)
        print("Type HELP for a quick command summary.")

    def _say_goodbye(self) -> None:
        print("Bye. :)")

    def _try_store_program_line(self, raw_input: str) -> bool:
        """Return True when the input begins with a line number and got stored."""

        parsed = split_line_number(raw_input)
        if not parsed:
            return False

        line_number, content = parsed
        result = self._line_storage.set_line(line_number, content)
        self._report_line_storage(result, content)
        return True

    def _report_line_storage(self, result: StoreResult, content: str) -> None:
        """Give lightweight feedback about how the line buffer changed."""

        if result.action is StoreAction.ADDED:
            print(f"Stored line {result.line_number}: {content or '(blank)'}")
        elif result.action is StoreAction.UPDATED:
            print(f"Updated line {result.line_number}: {content or '(blank)'}")
        elif result.action is StoreAction.DELETED:
            print(f"Deleted line {result.line_number}.")
        else:
            print(f"No change for line {result.line_number} (it was already empty).")

    def _handle_direct_mode(self, normalized_input: str) -> bool:
        """Parse and execute direct-mode commands.

        Returns True when the caller should exit the REPL.
        """

        try:
            statement = self._parser.parse(normalized_input)
        except (ParseError, TokenizerError) as exc:
            print(f"Parse error: {exc}")
            return False

        result = self._executor.execute(statement)
        if result.goto_target is not None:
            print("GOTO is only available when RUN executes stored program lines.")
            return False

        if result.gosub_target is not None:
            print("GOSUB is only available when RUN executes stored program lines.")
            return False

        if result.gosub_return:
            print("RETURN without GOSUB has no effect in direct mode.")
            return False

        if result.signal is ExecutionSignal.EXIT:
            self._say_goodbye()
            return True

        return False


def run_script_file(
    path: str,
    *,
    debug: bool = False,
    step_limit: int = DEFAULT_STEP_LIMIT,
) -> int:
    """Execute a SolarBASIC source file without launching the REPL."""

    parser = CommandParser()
    storage = LineStorage()
    executor = CommandExecutor(
        storage,
        parser,
        debug=debug,
        step_limit=step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT,
    )

    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as exc:
        print(f"Unable to read script '{path}': {exc}")
        return 1

    used_numbers = set()
    next_auto_line = 10
    for raw_line in lines:
        stripped_line = raw_line.rstrip("\n")
        normalized = stripped_line.strip()
        if not normalized:
            continue

        parsed = split_line_number(stripped_line)
        if parsed:
            line_number, content = parsed
            used_numbers.add(line_number)
            next_auto_line = max(next_auto_line, line_number + 10)
        else:
            line_number = next_auto_line
            while line_number in used_numbers:
                line_number += 10
            next_auto_line = line_number + 10
            content = normalized
            used_numbers.add(line_number)

        storage.set_line(line_number, content)

    executor.execute(RunStatement())
    return 0
