from dataclasses import dataclass, field
from typing import List, Union, Tuple, Optional

from interpreter.models.constants import Types, RelationshipOperator, SumOperator, MulOperator, CurrencyType
from interpreter.models.base import Factor, ParseTreeNode


@dataclass
class NegationFactor(ParseTreeNode):
    factor: Factor
    is_negated: bool = False

    def accept(self, visitor: 'Environment'):
        return visitor.visit_negation_factor(self)


@dataclass
class TypeCastingFactor(ParseTreeNode):
    negation_factor: NegationFactor
    castType: Optional[Union[Types, CurrencyType]] = None

    def accept(self, visitor: 'Environment'):
        return visitor.visit_type_casting_factor(self)


@dataclass
class MultiplyExpression(ParseTreeNode):
    left_side: TypeCastingFactor
    right_side: List[Tuple[MulOperator, TypeCastingFactor]] = field(default_factory=lambda: [])

    def accept(self, visitor: 'Environment'):
        return visitor.visit_arithmetic_expression(self)


@dataclass
class SumExpression(ParseTreeNode):
    left_side: MultiplyExpression
    right_side: List[Tuple[SumOperator, MultiplyExpression]] = field(default_factory=lambda: [])

    def accept(self, visitor: 'Environment'):
        return visitor.visit_arithmetic_expression(self)


@dataclass
class RelationshipExpression(ParseTreeNode):
    left_side: SumExpression
    operator: Optional[RelationshipOperator] = None
    right_side: Optional[SumExpression] = None

    def accept(self, visitor: 'Environment'):
        return visitor.visit_relationship_expression(self)


@dataclass
class AndExpression(ParseTreeNode):
    relationship_expressions: List[RelationshipExpression]

    def accept(self, visitor: 'Environment'):
        return visitor.visit_and_expression(self)


@dataclass
class Expression(ParseTreeNode):
    and_expressions: List[AndExpression]

    def accept(self, visitor: 'Environment'):
        return visitor.visit_expression(self)
