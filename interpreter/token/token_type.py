from enum import Enum, auto


class TokenType(Enum):
    ID = auto()

    # Operators
    CURRENCY_DECLARATION_OPERATOR = auto()
    ASSIGN_OPERATOR = auto()
    AND_OPERATOR = auto()
    OR_OPERATOR = auto()
    ADD_OPERATOR = auto()
    SUB_OPERATOR = auto()
    MUL_OPERATOR = auto()
    DIV_OPERATOR = auto()
    MODULO_OPERATOR = auto()
    NEGATION_OPERATOR = auto()
    EQUAL_OPERATOR = auto()
    NOT_EQUAL_OPERATOR = auto()
    LESS_THAN_OPERATOR = auto()
    GREATER_THAN_OPERATOR = auto()
    LESS_THAN_OR_EQUAL_OPERATOR = auto()
    GREATER_THAN_OPERATOR_OR_EQUAL = auto()

    # TYPES
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    CURRENCY = auto()

    # VALUES
    INT_VALUE = auto()
    FLOAT_VALUE = auto()
    STRING_VALUE = auto()
    BOOL_VALUE = auto()
    CURRENCY_VALUE = auto()
    TRUE = auto()
    FALSE = auto()

    # RESERVED NAMES AND CHARS
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    LEFT_CURLY_BRACKET = auto()
    RIGHT_CURLY_BRACKET = auto()
    SEMICOLON = auto()
    IF_NAME = auto()
    ELSE_NAME = auto()
    RETURN_NAME = auto()
    WHILE_NAME = auto()
    EOF = auto()
