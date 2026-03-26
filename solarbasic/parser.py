"""Expression and command parsers for SolarBASIC."""
from __future__ import annotations

from typing import List, Optional, Sequence

from .ast_nodes import (
    AssignmentStatement,
    BinaryExpression,
    EndFuncStatement,
    Expression,
    ExitStatement,
    FuncStatement,
    FunctionCallExpression,
    GotoStatement,
    GosubStatement,
    HelpStatement,
    AboutStatement,
    IdentifierExpression,
    IfStatement,
    LedStatement,
    ListFunctionsStatement,
    ListStatement,
    NewStatement,
    NumberLiteral,
    ParseError,
    PrintStatement,
    ReturnStatement,
    RunStatement,
    Statement,
    UnaryExpression,
    WhileStatement,
    WendStatement,
)
from .tokenizer import Token, TokenType, Tokenizer


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

    def _match_operator(self, operators: set) -> bool:
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

        dispatch = {
            "PRINT": self._parse_print,
            "LED": self._parse_led,
            "IF": self._parse_if,
            "GOTO": self._parse_goto,
            "GOSUB": self._parse_gosub,
            "WHILE": self._parse_while,
            "FUNC": self._parse_func,
            "RETURN": self._parse_return,
            "LIST": self._parse_list,
        }

        if keyword in dispatch:
            return dispatch[keyword](body)

        no_arg_map = {
            "WEND": WendStatement,
            "ENDFUNC": EndFuncStatement,
            "LISTF": ListFunctionsStatement,
            "NEW": NewStatement,
            "RUN": RunStatement,
            "HELP": HelpStatement,
            "ABOUT": AboutStatement,
        }

        if keyword in no_arg_map:
            self._ensure_no_extra(body, keyword)
            return no_arg_map[keyword]()

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

        expression_tokens = tokens[start + 2:]
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

        consequence_tokens = tokens[then_index + 1:]
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
