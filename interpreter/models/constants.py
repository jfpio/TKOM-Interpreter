from enum import Enum


class Types(Enum):
    int = 'int'
    float = 'float'
    string = 'string'
    bool = 'bool'
    void = 'void'


class RelationshipOperator(Enum):
    EQUAL_OPERATOR = '=='
    NOT_EQUAL_OPERATOR = '/='
    LESS_THAN_OPERATOR = '<'
    GREATER_THAN_OPERATOR = '>'
    LESS_THAN_OR_EQUAL_OPERATOR = '<='
    GREATER_THAN_OPERATOR_OR_EQUAL = '>='


class SumOperator(Enum):
    ADD = '+'
    SUB = '-'


class MulOperator(Enum):
    MUL = '*'
    DIV = '/'
    MODULO = '%'
