from dataclasses import dataclass, field
from typing import List, Union, Tuple, Optional

from interpreter.models.constants import Types, RelationshipOperator, SumOperator, MulOperator, CurrencyType
from interpreter.models.base import Constant, FunctionCall


@dataclass
class NegationFactor:
    factor: Union['Expression', FunctionCall, Constant]
    is_negated: bool = False


@dataclass
class TypeCastingFactor:
    negation_factor: NegationFactor
    castType: Optional[Union[Types, CurrencyType]] = None


@dataclass
class MultiplyExpression:
    type_casting_factor: TypeCastingFactor
    right_side: List[Tuple[MulOperator, TypeCastingFactor]] = field(default_factory=lambda: [])


@dataclass
class SumExpression:
    multiplyExpression: MultiplyExpression
    right_side: List[Tuple[SumOperator, MultiplyExpression]] = field(default_factory=lambda: [])


@dataclass
class RelationshipExpression:
    left_side: SumExpression
    operator: Optional[RelationshipOperator] = None
    right_side: Optional[SumExpression] = None


@dataclass
class AndExpression:
    relationship_expressions: List[RelationshipExpression]


@dataclass
class Expression:
    and_expression: List[AndExpression]

