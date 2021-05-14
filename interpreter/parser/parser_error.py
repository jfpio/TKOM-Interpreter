from typing import Tuple

from interpreter.source.source_position import SourcePosition
from interpreter.token.token_type import TokenType


class ParserError(Exception):
    def __init__(self, position: SourcePosition, actual: TokenType, expected: Tuple[TokenType]):
        self.position = position
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return f"Syntax error\n" \
               f"in line: {self.position.line} column: {self.position.column}\n" \
               f"get {self.actual},\n" \
               f"when expected {self.expected},\n" \

