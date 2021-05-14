from dataclasses import dataclass
from typing import List, Union, Tuple

from interpreter.models.constants import Types, RelationshipOperator, SumOperator, MulOperator
from interpreter.models.base import Currency, Constant, FunctionCall


class Factor:
    pass


@dataclass
class NegationFactor:
    factor: Union['Expression', FunctionCall, Constant]
    negation: bool = False


@dataclass
class TypeCastingFactor:
    negation_factor: NegationFactor
    castType: Union[Types, Currency]


@dataclass
class MultiplyExpression:
    type_casting_factor: TypeCastingFactor
    right_side: List[Tuple[MulOperator, TypeCastingFactor]]


@dataclass
class SumExpression:
    multiplyExpression: MultiplyExpression
    right_side: List[Tuple[SumOperator, MultiplyExpression]]


@dataclass
class RelationshipExpression:
    left_side: SumExpression
    operator: RelationshipOperator
    right_side: SumExpression


@dataclass
class AndExpression:
    relationship_expressions: List[RelationshipExpression]


@dataclass
class Expression:
    and_expression: List[AndExpression]

