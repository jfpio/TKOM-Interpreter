from enum import Enum

from interpreter.models.constants import SimpleTypes
from interpreter.source.source_position import SourcePosition


class SemanticErrorCode(Enum):
    ID_NOT_FOUND = 'Identifier not found'
    DUPLICATE_ID = 'Duplicate declaration found'
    WRONG_NUMBER_OF_PARAMS = 'Wrong number of params passed to the function'


class SemanticError(Exception):
    def __init__(self, source_position: SourcePosition, error_code: SemanticErrorCode, name: str):
        self.error_code = error_code
        self.position = source_position
        self.name = name

    def __str__(self):
        return f"Semantic error: {self.error_code} in {self.position} for id named {self.name}"


class SemanticTypeError(Exception):
    def __init__(self, source_position: SourcePosition, expected_type: SimpleTypes, actual_type: SimpleTypes):
        self.source_position = source_position
        self.expected = expected_type
        self.actual = actual_type

    def __str__(self):
        return f"Wrong type: Expected {self.expected}, but get {self.actual}"
