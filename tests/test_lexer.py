import io

from interpreter.lexer.lexer import Lexer, tokens_generator
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestSingleTokens:
    def test_get_EOF(self):
        token = self._get_first_token('')
        assert token.type == TokenType.EOF

    def test_get_int(self):
        token = self._get_first_token('111')
        assert token.type == TokenType.INT_VALUE
        assert token.value == 111
        assert token.source_position == SourcePosition(1, 3)

    def test_get_float(self):
        token = self._get_first_token('111.1')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 111.1
        assert token.source_position == SourcePosition(1, 5)

    def test_get_currency(self):
        token = self._get_first_token('111.1USD')
        assert token.type == TokenType.CURRENCY_VALUE
        assert token.value == '111.1USD'
        assert token.source_position == SourcePosition(1, 8)

    @staticmethod
    def _get_first_token(string: str) -> Token:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return lexer.get_next_token()


class TestManyTokens:
    def test_two_integers(self):
        tokens = list(self._get_tokens("111 222"))

        token_types = [token.type for token in tokens]

        assert token_types == [TokenType.INT_VALUE, TokenType.INT_VALUE, TokenType.EOF]

        assert tokens == [
            Token(TokenType.INT_VALUE, 111, SourcePosition(1, 3)),
            Token(TokenType.INT_VALUE, 222, SourcePosition(1, 7)),
            Token(TokenType.EOF, '', SourcePosition(2, 0)),
        ]

    @staticmethod
    def _get_tokens(string: str) -> [Token]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)

        return tokens_generator(lexer)
