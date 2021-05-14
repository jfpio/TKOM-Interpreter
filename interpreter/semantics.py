import string
from abc import ABC
from dataclasses import dataclass
from typing import Union


class Node(ABC):
    pass


class Declaration(ABC):
    pass


@dataclass(frozen=True)
class CurrencyDeclaration(Declaration):
    name: str
    value: Union[int, float]


class FunctionDeclaration(Declaration):
    def __init__(self, id, params, block):
        self.id = id
        self.params = params
        self.block = block
