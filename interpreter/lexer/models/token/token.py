from interpreter.lexer.models.token.source_position import SourcePosition
from interpreter.lexer.models.token.token_type import TokenType


class Token:
    def __init__(self, type: TokenType, value, source_position: SourcePosition):
        self.type = type
        self.value = value
        self.source_position = source_position

    def __str__(self):
        return f"position: {self.source_position.line}:{self.source_position.column} type: {self.type} value: {self.value}"
