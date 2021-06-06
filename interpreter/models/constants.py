from dataclasses import dataclass
from enum import Enum
from typing import Union, Type

from interpreter.token.token_type import TokenType


@dataclass
class CurrencyType:
    name: str


@dataclass
class CurrencyValue:
    name: str
    value: float

    def __str__(self):
        return f"{self.value}{self.name}"

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return self.value

    def __bool__(self):
        if self.value == 0:
            return False
        else:
            return True


CustomTypeTypes = Union[Type, CurrencyType]
PossibleTypes = Union[int, float, str, bool, CurrencyValue]

TOKEN_TYPES_INTO_TYPES = {
    TokenType.INT: int,
    TokenType.FLOAT: float,
    TokenType.STRING: str,
    TokenType.BOOL: bool,
}
POSSIBLE_TOKEN_TYPES = list(TOKEN_TYPES_INTO_TYPES.keys()) + [TokenType.CURRENCY]


class RelationshipOperator(Enum):
    EQUAL_OPERATOR = '=='
    NOT_EQUAL_OPERATOR = '/='
    LESS_THAN_OPERATOR = '<'
    GREATER_THAN_OPERATOR = '>'
    LESS_THAN_OR_EQUAL_OPERATOR = '<='
    GREATER_THAN_OPERATOR_OR_EQUAL_OPERATOR = '>='


TOKEN_TYPE_INTO_RELATIONSHIP_OPERAND = {
    TokenType.EQUAL_OPERATOR: RelationshipOperator.EQUAL_OPERATOR,
    TokenType.NOT_EQUAL_OPERATOR: RelationshipOperator.NOT_EQUAL_OPERATOR,
    TokenType.LESS_THAN_OPERATOR: RelationshipOperator.LESS_THAN_OPERATOR,
    TokenType.GREATER_THAN_OPERATOR: RelationshipOperator.GREATER_THAN_OPERATOR,
    TokenType.LESS_THAN_OR_EQUAL_OPERATOR: RelationshipOperator.LESS_THAN_OR_EQUAL_OPERATOR,
    TokenType.GREATER_THAN_OPERATOR_OR_EQUAL: RelationshipOperator.GREATER_THAN_OPERATOR_OR_EQUAL_OPERATOR
}

RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION = {
    RelationshipOperator.EQUAL_OPERATOR: lambda x, y: x == y,
    RelationshipOperator.NOT_EQUAL_OPERATOR: lambda x, y: x != y,
    RelationshipOperator.LESS_THAN_OPERATOR: lambda x, y: x < y,
    RelationshipOperator.GREATER_THAN_OPERATOR: lambda x, y: x > y,
    RelationshipOperator.LESS_THAN_OR_EQUAL_OPERATOR: lambda x, y: x <= y,
    RelationshipOperator.GREATER_THAN_OPERATOR_OR_EQUAL_OPERATOR: lambda x, y: x >= y
}


class SumOperator(Enum):
    ADD = '+'
    SUB = '-'


TOKEN_TYPE_INTO_SUM_OPERATOR = {
    TokenType.ADD_OPERATOR: SumOperator.ADD,
    TokenType.SUB_OPERATOR: SumOperator.SUB
}


class MulOperator(Enum):
    MUL = '*'
    DIV = '/'
    MODULO = '%'


token_type_into_mul_operator = {
    TokenType.MUL_OPERATOR: MulOperator.MUL,
    TokenType.DIV_OPERATOR: MulOperator.DIV,
    TokenType.MODULO_OPERATOR: MulOperator.MODULO
}

ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION = {
    SumOperator.ADD: lambda x, y: x + y,
    SumOperator.SUB: lambda x, y: x - y,
    MulOperator.MUL: lambda x, y: x * y,
    MulOperator.DIV: lambda x, y: x / y,
    MulOperator.MODULO: lambda x, y: x % y
}
