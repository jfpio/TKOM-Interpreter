from abc import ABC
from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import Types, CurrencyType
from interpreter.source.source_position import SourcePosition


class Factor(ABC):
    pass


@dataclass
class Currency:
    name: str
    value: Union[int, float]


@dataclass
class Constant(Factor):
    value: Union[str, int, float, bool, CurrencyType]
    source_position: SourcePosition


@dataclass
class Variable(Factor):
    id: str
    source_position: SourcePosition


@dataclass
class FunctionCall(Factor):
    id: str
    args: List['Expression']
    source_position: SourcePosition


@dataclass
class Params:
    id: str
    type: Types


@dataclass
class Assignment:
    id: str
    expression: 'Expression'
    source_position: SourcePosition
