import io

from interpreter.lexer.lexer import Lexer
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestLexer:
    def test_get_chars_from_string(self):
        string = "return"
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        token = lexer.get_next_token()

        assert token == Token(TokenType.RETURN_NAME, '', SourcePosition(1, 1))
