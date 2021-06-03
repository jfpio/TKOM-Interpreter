from abc import ABC
from dataclasses import dataclass
from typing import Union, List, Optional

from interpreter.models.base import Param
from interpreter.models.constants import Types
from interpreter.models.statements import Statements
from interpreter.source.source_position import SourcePosition


@dataclass
class Declaration(ABC):
    source_position: SourcePosition


@dataclass
class FunctionDeclaration(Declaration):
    return_type: Types
    id: str
    params: List[Param]
    statement: Statements


@dataclass
class VariableDeclaration(Declaration):
    type: Types
    id: str
    expression: Optional['Expression']


@dataclass
class CurrencyDeclaration(Declaration):
    name: str
    value: Union[int, float]