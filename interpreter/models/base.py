from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import Types, CurrencyType
from interpreter.source.source_position import SourcePosition


@dataclass
class Currency:
    name: str
    value: Union[int, float]


@dataclass
class Constant:
    source_position: SourcePosition
    value: Union[str, int, float, bool, CurrencyType]

    def accept(self, visitor: 'Environment'):
        return visitor.visit_factor(self)

@dataclass
class Variable:
    source_position: SourcePosition
    id: str


@dataclass
class FunctionCall:
    source_position: SourcePosition
    id: str
    args: List['Expression']


@dataclass
class Param:
    id: str
    type: Types


@dataclass
class Assignment:
    source_position: SourcePosition
    id: str
    expression: 'Expression'


Factor = Union[FunctionCall, Variable, 'Expression', Constant]
