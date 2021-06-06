from enum import Enum
from typing import Union

from interpreter.models.constants import PossibleTypes
from interpreter.source.source_position import SourcePosition


class SemanticErrorCode(Enum):
    FUN_ID_NOT_FOUND = 'Function identifier not found'
    VAR_ID_NOT_FOUND = 'Variable identifier not found'
    CURR_ID_NOT_FOUND = 'Currency identifier not found'
    DUPLICATE_ID = 'Duplicate declaration found'
    WRONG_NUMBER_OF_PARAMS = 'Wrong number of params passed to the function'


class RuntimeErrorCode(Enum):
    INFINITE_LOOP = 'Infinite loop found'


class EnvironmentException(Exception):
    def __init__(self, source_position: SourcePosition, error_code: Union[SemanticErrorCode, RuntimeErrorCode],
                 name: str):
        self.error_code = error_code
        self.position = source_position
        self.name = name


class SemanticError(EnvironmentException):
    def __str__(self):
        return f"Semantic error: {self.error_code} in {self.position} for id named {self.name}"


class RunTimeEnvError(EnvironmentException):
    def __str__(self):
        return f"Runtime Error: {self.error_code} in {self.position} for id named {self.name}"


class SemanticTypeError(Exception):
    def __init__(self, source_position: SourcePosition, expected_type, actual_type: PossibleTypes):
        self.source_position = source_position
        self.expected = expected_type
        self.actual = actual_type

    def __str__(self):
        return f"Wrong type: Expected {self.expected}, but get {self.actual}"
