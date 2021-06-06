from dataclasses import dataclass
from typing import Union

from interpreter.models.constants import SimpleTypes, CurrencyType


@dataclass
class CurrencyValue(CurrencyType):
    value: float

    def __str__(self):
        return f"{self.value}{self.name}"

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return self.value

    def __bool__(self):
        if self.value == 0:
            return False
        else:
            return True


EnvironmentTypes = Union[int, float, str, bool, CurrencyValue]

SimpleTypesIntoEnvironmentTypes = {
    SimpleTypes.int: int,
    SimpleTypes.float: float,
    SimpleTypes.string: str,
    SimpleTypes.bool: bool,
}

EnvironmentTypesIntoTypes = {
    int: SimpleTypes.int,
    float: SimpleTypes.float,
    str: SimpleTypes.string,
    bool: SimpleTypes.bool,
    CurrencyValue: SimpleTypes.currency
}
