import typing

from interpreter.source.source_position import SourcePosition
from interpreter.token.token_type import TokenType


class Token:
    def __init__(self, type: TokenType, value:  typing.Union[str, float, int], source_position: SourcePosition):
        self.type = type
        self.value = value
        self.source_position = source_position

    def __str__(self):
        return f"position: {self.source_position.line}:{self.source_position.column} type: {self.type} value: {self.value}"

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value and self.source_position == other.source_position
