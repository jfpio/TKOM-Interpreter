from typing import Union

from interpreter.models.base import Constant, Variable, FunctionCall
from interpreter.models.expressions import AndExpression, RelationshipExpression, SumExpression, MultiplyExpression, \
    TypeCastingFactor, NegationFactor, Expression


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
