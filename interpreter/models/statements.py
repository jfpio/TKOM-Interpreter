from abc import ABC
from dataclasses import dataclass
from typing import Optional, List, Union

from interpreter.models.base import Assignment


class Statement(ABC):
    pass


@dataclass
class ReturnStatement(Statement):
    expression: Optional['Expression']


@dataclass
class WhileStatement(Statement):
    expression: 'Expression'
    statement: Statement


@dataclass
class IfStatement(Statement):
    expression: 'Expression'
    statement: Statement


@dataclass
class CompoundStatement(Statement):
    statements: List[Union['VariableDeclaration', Assignment, Statement]]
