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
    source_position = factor.source_position
    return Expression(
        source_position,
        [
            AndExpression(
                source_position,
                [
                    RelationshipExpression(
                        source_position,
                        SumExpression(
                            source_position,
                            MultiplyExpression(
                                source_position,
                                TypeCastingFactor(
                                    source_position,
                                    NegationFactor(
                                        source_position,
                                        factor, False)))))
                ])])


def mul_expression_factory(value, source_column):
    source_position = SourcePosition(1, source_column)
    return MultiplyExpression(
        source_position,
        TypeCastingFactor(
            source_position,
            NegationFactor(
                source_position,
                Constant(source_position, value), False)))


def type_casting_factor_factory(value, source_column):
    source_position = SourcePosition(1, source_column)
    return TypeCastingFactor(source_position,
                             NegationFactor(source_position,
                                            Constant(source_position, value), False))


def sum_expression_factory(value, source_column):
    source_position = SourcePosition(1, source_column)
    return SumExpression(source_position,
                         MultiplyExpression(source_position,
                                            TypeCastingFactor(source_position,
                                                              NegationFactor(source_position,
                                                                             Constant(source_position,
                                                                                      value), False))))


def relationship_expression_factory(value, source_column):
    source_position = SourcePosition(1, source_column)
    return RelationshipExpression(
        source_position,
        SumExpression(
            source_position,
            MultiplyExpression(
                source_position,
                TypeCastingFactor(
                    source_position,
                    NegationFactor(
                        source_position,
                        Constant(
                            source_position,
                            value),
                        False)))))


def and_expression_factory(value, source_column):
    source_position = SourcePosition(1, source_column)
    return AndExpression(
        source_position,
        [
            RelationshipExpression(
                source_position,
                SumExpression(
                    source_position,
                    MultiplyExpression(
                        source_position,
                        TypeCastingFactor(
                            source_position,
                            NegationFactor(
                                source_position,
                                Constant(source_position, value), False)))))
        ])
