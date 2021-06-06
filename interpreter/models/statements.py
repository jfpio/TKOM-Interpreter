from abc import ABC
from dataclasses import dataclass
from typing import Optional, List, Union

from interpreter.environment.types import EnvironmentTypes
from interpreter.models.base import Assignment, FunctionCall
from interpreter.models.expressions import Expression
from interpreter.source.source_position import SourcePosition


@dataclass
class Statement(ABC):
    source_position: SourcePosition


@dataclass
class ReturnStatement(Statement):
    expression: Optional['Expression']

    def accept(self, visitor: 'Environment') -> Optional[EnvironmentTypes]:
        return visitor.visit_return_statement(self)


@dataclass
class WhileStatement(Statement):
    expression: 'Expression'
    statements: 'Statements'


@dataclass
class IfStatement(Statement):
    expression: 'Expression'
    statements: 'Statements'

    def accept(self, visitor: 'Environment') -> Optional[EnvironmentTypes]:
        return visitor.visit_if_statement(self)


StatementsTypes = Union['VariableDeclaration', 'CurrencyDeclaration', Assignment, FunctionCall, ReturnStatement,
                        WhileStatement, IfStatement]


@dataclass
class Statements:
    list_of_statements: List[StatementsTypes]

    def accept(self, visitor: 'Environment'):
        return visitor.visit_statements(self)
