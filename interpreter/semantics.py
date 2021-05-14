import string
from abc import ABC
from dataclasses import dataclass
from typing import Union


class Node(ABC):
    pass


class Statement(ABC):
    pass


@dataclass(frozen=True)
class CurrencyDeclaration(Statement):
    name: str
    value: Union[int, float]


class FunctionDeclaration(Statement):
    def __init__(self, id, params, block):
        self.id = id
        self.params = params
        self.block = block
