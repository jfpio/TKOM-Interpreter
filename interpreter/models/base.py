from abc import ABC
from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import Types, CurrencyType
from interpreter.source.source_position import SourcePosition


@dataclass
class ParseTreeNode(ABC):
    source_position: SourcePosition


@dataclass
class Constant(ParseTreeNode):
    value: Union[str, int, float, bool, CurrencyType]

    def accept(self, visitor: 'Environment'):
        return visitor.visit_factor(self)


@dataclass
class Variable(ParseTreeNode):
    id: str


@dataclass
class FunctionCall(ParseTreeNode):
    id: str
    args: List['Expression']


@dataclass
class Param(ParseTreeNode):
    id: str
    type: Types


@dataclass
class Assignment(ParseTreeNode):
    id: str
    expression: 'Expression'


Factor = Union[FunctionCall, Variable, 'Expression', Constant]
