from dataclasses import dataclass

from interpreter.models.constants import Types


@dataclass
class CurrencyValue:
    value: str
    currency_name: str


TypesIntoEnvironmentTypes = {
    Types.int: int,
    Types.float: float,
    Types.string: str,
    Types.bool: bool,
    Types.currency: CurrencyValue
}

EnvironmentTypesIntoTypes = {
    int: Types.int,
    float: Types.float,
    str: Types.string,
    bool: Types.bool,
    CurrencyValue: Types.currency
}
