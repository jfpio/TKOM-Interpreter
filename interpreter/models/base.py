from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import Types
from interpreter.source.source_position import SourcePosition


@dataclass
class Currency:
    name: str
    value: Union[int, float]


@dataclass
class Constant:
    value: Union[str, int, float, bool, Currency]
    source_position: SourcePosition


@dataclass
class Variable:
    id: str
    source_position: SourcePosition


@dataclass
class Assignment:
    id: str
    expression: 'Expression'


@dataclass
class FunctionCall:
    id: str
    args: List['Expression']


@dataclass
class Params:
    id: str
    type: Types
