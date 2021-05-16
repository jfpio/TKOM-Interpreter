from abc import ABC
from dataclasses import dataclass
from typing import Optional, List, Union

from interpreter.models.base import Assignment, FunctionCall
from interpreter.models.expressions import Expression
from interpreter.source.source_position import SourcePosition


@dataclass
class Statement(ABC):
    source_position: SourcePosition


@dataclass
class ReturnStatement(Statement):
    expression: Optional['Expression']


@dataclass
class WhileStatement(Statement):
    expression: 'Expression'
    statement: 'Statements'


@dataclass
class IfStatement(Statement):
    expression: 'Expression'
    statement: 'Statements'


StatementsTypes = Union['VariableDeclaration', 'CurrencyDeclaration', Assignment, FunctionCall, ReturnStatement,
                        WhileStatement, IfStatement]


@dataclass
class Statements:
    list_of_statements: List[StatementsTypes]
