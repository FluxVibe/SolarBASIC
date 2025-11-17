"""Simple tokenizer for early SolarBASIC prototypes (Stage 3)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    """Token categories recognized by the SolarBASIC tokenizer."""

    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()


@dataclass
class Token:
    """Hold the type, lexeme, and starting column of a token."""

    type: TokenType
    lexeme: str
    column: int


class TokenizerError(Exception):
    """Raised when the tokenizer finds malformed input."""


class Tokenizer:
    """Convert a single line of SolarBASIC source into tokens."""

    KEYWORDS = {
        "PRINT",
        "LED",
        "LIST",
        "LISTF",
        "FUNCS",
        "RUN",
        "NEW",
        "EXIT",
        "QUIT",
        "HELP",
        "ABOUT",
        "ON",
        "OFF",
        "IF",
        "THEN",
        "GOTO",
        "WHILE",
        "WEND",
        "FUNC",
        "ENDFUNC",
        "RETURN",
        "GOSUB",
        "LET",
    }

    TWO_CHAR_OPERATORS = {"<=", ">=", "<>"}
    SINGLE_CHAR_OPERATORS = {"+", "-", "*", "/", "=", "<", ">"}
    PUNCTUATION = {"(", ")", ",", ":"}

    def tokenize(self, source: str) -> List[Token]:
        """Tokenize a single source line into Token objects."""

        tokens: List[Token] = []
        idx = 0
        length = len(source)

        while idx < length:
            ch = source[idx]

            if ch.isspace():
                idx += 1
                continue

            if ch == '"':
                token, idx = self._consume_string(source, idx)
                tokens.append(token)
                continue

            if ch.isdigit():
                token, idx = self._consume_number(source, idx)
                tokens.append(token)
                continue

            if ch.isalpha() or ch == "_":
                token, idx = self._consume_identifier(source, idx)
                tokens.append(token)
                continue

            token, idx = self._consume_operator_or_punct(source, idx)
            tokens.append(token)

        return tokens

    def _consume_string(self, source: str, start: int) -> tuple[Token, int]:
        end = start + 1
        value_chars: List[str] = []

        while end < len(source) and source[end] != '"':
            value_chars.append(source[end])
            end += 1

        if end >= len(source) or source[end] != '"':
            raise TokenizerError("Unterminated string literal.")

        lexeme = ''.join(value_chars)
        token = Token(TokenType.STRING, lexeme, start)
        return token, end + 1

    def _consume_number(self, source: str, start: int) -> tuple[Token, int]:
        end = start
        while end < len(source) and source[end].isdigit():
            end += 1

        lexeme = source[start:end]
        token = Token(TokenType.NUMBER, lexeme, start)
        return token, end

    def _consume_identifier(self, source: str, start: int) -> tuple[Token, int]:
        end = start
        while end < len(source) and (source[end].isalnum() or source[end] == "_"):
            end += 1

        lexeme = source[start:end]
        upper_lexeme = lexeme.upper()
        token_type = TokenType.KEYWORD if upper_lexeme in self.KEYWORDS else TokenType.IDENTIFIER
        token = Token(token_type, upper_lexeme if token_type is TokenType.KEYWORD else lexeme, start)
        return token, end

    def _consume_operator_or_punct(self, source: str, start: int) -> tuple[Token, int]:
        # Check two-character operators first.
        if start + 1 < len(source):
            candidate = source[start:start + 2]
            if candidate in self.TWO_CHAR_OPERATORS:
                return Token(TokenType.OPERATOR, candidate, start), start + 2

        ch = source[start]
        if ch in self.SINGLE_CHAR_OPERATORS:
            return Token(TokenType.OPERATOR, ch, start), start + 1

        if ch in self.PUNCTUATION:
            return Token(TokenType.PUNCTUATION, ch, start), start + 1

        raise TokenizerError(f"Unexpected character '{ch}' at column {start}.")
