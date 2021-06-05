from abc import ABC
from typing import Union, List, Tuple

from interpreter.models.base import Param
from interpreter.models.constants import Types


class Symbol(ABC):
    def __init__(self, name: str):
        self.name = name


class VarSymbol(Symbol):
    def __init__(self, name: str, type: Types, value: Union[int, float, str, bool]):
        super().__init__(name)
        self.type = type
        self.value = value


class CurrencySymbol(Symbol):
    def __init__(self, name: str, value: float):
        super().__init__(name)
        self.value = value


class FunctionSymbol(Symbol):
    def __init__(self, name: str, params: List[Param], return_type: Types):
        super().__init__(name)
        self.params = params
        self.return_type = return_type
