from interpreter.source.source_position import SourcePosition
from interpreter.token.token_type import TokenType


class SyntaxError(Exception):
    def __init__(self, position: SourcePosition, expected: TokenType, actual: TokenType):
        self.position = position
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return f"Syntax error\n" \
               f"in line: {self.position.line} column: {self.position.column}\n" \
               f"expected {self.expected},\n" \
               f"but get {self.actual},\n"
