from dataclasses import dataclass
from typing import Union

from interpreter.models.constants import Types


@dataclass
class CurrencyValue:
    value: float
    currency_name: str

    def __str__(self):
        return f"{self.value}{self.currency_name}"

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
    Types.int: int,
    Types.float: float,
    Types.string: str,
    Types.bool: bool,
}

EnvironmentTypesIntoTypes = {
    int: Types.int,
    float: Types.float,
    str: Types.string,
    bool: Types.bool,
    CurrencyValue: Types.currency
}
