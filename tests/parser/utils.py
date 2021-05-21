from typing import Union

from interpreter.models.base import Constant, Variable, FunctionCall
from interpreter.models.expressions import AndExpression, RelationshipExpression, SumExpression, MultiplyExpression, \
    TypeCastingFactor, NegationFactor, Expression
from interpreter.source.source_position import SourcePosition


def simple_expression_factory(factor: Union[Constant, Variable, FunctionCall]):
    """
    Function that creates simple expression, so pass only string that is Constant, Variable or FunctionCall
    I.E.: 'a', a(), 3, b(a)
    """
    return Expression(
        [
            AndExpression(
                [
                    RelationshipExpression(
                        SumExpression(
                            MultiplyExpression(
                                TypeCastingFactor(
                                    NegationFactor(
                                        factor, False)))))
                ])])


def mul_expression_factory(value, source_column):
    return MultiplyExpression(
        TypeCastingFactor(
            NegationFactor(
                Constant(SourcePosition(1, source_column), value), False)))


def type_casting_factor_factory(value, source_column):
    return TypeCastingFactor(
        NegationFactor(
            Constant(SourcePosition(1, source_column), value), False))


def sum_expression_factory(value, source_column):
    return SumExpression(
        MultiplyExpression(
            TypeCastingFactor(
                NegationFactor(
                    Constant(SourcePosition(1, source_column), value), False))))


def relationship_expression_factory(value, source_column):
    return RelationshipExpression(
        SumExpression(
            MultiplyExpression(
                TypeCastingFactor(
                    NegationFactor(
                        Constant(SourcePosition(1, source_column), value), False)))))


def and_expression_factory(value, source_column):
    return AndExpression(
        [
            RelationshipExpression(
                SumExpression(
                    MultiplyExpression(
                        TypeCastingFactor(
                            NegationFactor(
                                Constant(SourcePosition(1, source_column), value), False)))))
        ])
