from dataclasses import dataclass
from typing import Union, List

from interpreter.models.constants import Types


@dataclass
class Currency:
    name: str
    value: Union[int, float]


@dataclass
class Constant:
    value: Union[str, int, float, bool, Currency]


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