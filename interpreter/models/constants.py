from dataclasses import dataclass
from enum import Enum

from interpreter.token.token_type import TokenType


class Types(Enum):
    int = 'int'
    float = 'float'
    string = 'string'
    bool = 'bool'
    void = 'void'


TOKEN_TYPES_INTO_TYPES = {
    TokenType.INT: Types.int,
    TokenType.FLOAT: Types.float,
    TokenType.STRING: Types.string,
    TokenType.BOOL: Types.bool,
    TokenType.VOID: Types.void
}
POSSIBLE_TYPES = list(TOKEN_TYPES_INTO_TYPES.keys()) + [TokenType.CURRENCY]


@dataclass
class CurrencyType:
    name: str


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


class SumOperator(Enum):
    ADD = '+'
    SUB = '-'


token_type_into_sum_operator = {
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
