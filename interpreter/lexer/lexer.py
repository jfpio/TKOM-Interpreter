from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class Lexer:
    def __init__(self, source: Source):
        self._source = source

    def get_next_token(self) -> Token:
        return Token(TokenType.RETURN_NAME, '', SourcePosition(1, 1))
