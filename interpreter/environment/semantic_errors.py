from enum import Enum

from interpreter.models.constants import Types
from interpreter.source.source_position import SourcePosition


class SemanticErrorCode(Enum):
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate declaration found'


class SemanticError(Exception):
    def __init__(self, source_position: SourcePosition, error_code: SemanticErrorCode, id: str):
        self.error_code = error_code
        self.position = source_position

    def __str__(self):
        return f"Semantic error: {self.error_code} in {self.position}"


class SemanticTypeError(Exception):
    def __init__(self, source_position: SourcePosition, expected_type: Types, actual_type: Types):
        self.source_position = source_position
        self.expected = expected_type
        self.actual = actual_type

    def __str__(self):
        return f"Wrong type: Expected {self.expected}, but get {self.actual}"
