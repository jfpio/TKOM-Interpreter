from abc import ABC
from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import CustomTypeOfTypes, PossibleTypes
from interpreter.source.source_position import SourcePosition


@dataclass
class ParseTreeNode(ABC):
    source_position: SourcePosition


@dataclass
class Constant(ParseTreeNode):
    value: PossibleTypes

    def accept(self, visitor: 'Environment'):
        return visitor.visit_constant(self)


@dataclass
class Variable(ParseTreeNode):
    id: str

    def accept(self, visitor: 'Environment'):
        return visitor.visit_variable(self)


@dataclass
class FunctionCall(ParseTreeNode):
    id: str
    args: List['Expression']

    def accept(self, visitor: 'Environment'):
        return visitor.visit_function_call(self)


@dataclass
class Param(ParseTreeNode):
    id: str
    type: CustomTypeOfTypes


@dataclass
class Assignment(ParseTreeNode):
    id: str
    expression: 'Expression'

    def accept(self, visitor: 'Environment'):
        return visitor.visit_assignment(self)


Factor = Union[FunctionCall, Variable, 'Expression', Constant]
