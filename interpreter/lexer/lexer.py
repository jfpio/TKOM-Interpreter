import typing

from interpreter.lexer.lexer_error import LexerError
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class Lexer:
    def __init__(self, source: Source):
        self._source = source

    def get_next_token(self) -> Token:
        self._skip_whitespace()

        if self._get_char() == 'EOF':
            return Token(TokenType.EOF, '', self._get_position())

        token = self._build_one_of_number_value()

        if token:
            return token
        else:
            raise LexerError("Can't match any token", self._previous_position)

    def _get_char(self) -> str:
        return self._source.get_char()

    def _next_char(self):
        self._previous_position = self._get_position()
        self._source.next_char()

    def _get_position(self) -> SourcePosition:
        return self._source.get_position()

    def _build_one_of_number_value(self) -> typing.Union[None, Token]:
        char = self._get_char()
        last_position = self._get_position()

        if not char.isdigit():
            return None

        base = 0
        while char.isdigit():
            base = base * 10 + int(char)

            last_position = self._get_position()
            self._source.next_char()
            char = self._source.get_char()

        if char == '.':
            return self._build_float_or_currency(base)

        return Token(TokenType.INT_VALUE, base, last_position)

    def _build_float_or_currency(self, previous_base: int) -> typing.Union[None, Token]:
        base = float(previous_base)

        self._next_char()
        char = self._get_char()
        last_position = self._get_position()

        i = -1
        while char.isdigit():
            base = base + float(char) * 10**i

            last_position = self._get_position()
            self._source.next_char()
            char = self._source.get_char()
            i += -1

        if char.isupper() and char != 'EOF':
            return self._build_currency(base)

        return Token(TokenType.FLOAT_VALUE, base, last_position)

    def _build_currency(self, previous_base: float) -> typing.Union[None, Token]:
        number = previous_base
        currency_name = ''

        position = self._get_position()
        for i in range(3):
            if self._get_char().isupper() and self._get_char() != 'EOF':
                currency_name += self._get_char()
                position = self._get_position()
                self._next_char()

            else:
                return None

        return Token(TokenType.CURRENCY_VALUE, f"{number}{currency_name}", position)

    def _skip_whitespace(self):
        char = self._get_char()
        while char.isspace():
            self._next_char()
            char = self._get_char()


def tokens_generator(lexer):
    previous_token = Token(TokenType.INT_VALUE, 1, SourcePosition(0, 0))

    while previous_token.type != TokenType.EOF:
        new_token = lexer.get_next_token()
        previous_token = new_token
        yield new_token
