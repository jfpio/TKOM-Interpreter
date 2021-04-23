import io

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestLexer:
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