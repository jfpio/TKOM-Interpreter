import io

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Constant
from interpreter.models.constants import Types, CurrencyType, MulOperator, SumOperator, RelationshipOperator
from interpreter.models.expressions import NegationFactor, TypeCastingFactor, MultiplyExpression, SumExpression, \
    RelationshipExpression, AndExpression, Expression
from interpreter.parser.parser import Parser
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from tests.parser.utils import mul_expression_factory, and_expression_factory, \
    relationship_expression_factory, type_casting_factor_factory, sum_expression_factory


class TestParserConstructions:
    def test_parse_negation_factor_1(self):
        parser = self._get_parser('!false')
        negation_factor = parser.parse_negation_factor()
        assert negation_factor == NegationFactor(Constant(SourcePosition(1, 6), False), True)

    def test_parse_negation_factor_2(self):
        parser = self._get_parser('true')
        negation_factor = parser.parse_negation_factor()
        assert negation_factor == NegationFactor(Constant(SourcePosition(1, 4), True), False)

    def test_parse_type_casting_factor_1(self):
        parser = self._get_parser('true')
        factor = parser.parse_type_casting_factor()
        assert factor == TypeCastingFactor(NegationFactor(Constant(SourcePosition(1, 4), True), False))

    def test_parse_type_casting_factor_2(self):
        types = ["int", "float", "string", "bool", "void"]
        types_enum = [Types.int, Types.float, Types.string, Types.bool, Types.void]
        for type, type_enum in zip(types, types_enum):
            string = f'({type}) true'
            parser = self._get_parser(string)
            factor = parser.parse_type_casting_factor()
            assert factor == \
                   TypeCastingFactor(
                       NegationFactor(
                           Constant(SourcePosition(1, len(string)), True), False), type_enum)

    def test_parse_type_casting_factor_3(self):
        string = '(EUR) true'
        parser = self._get_parser(string)
        factor = parser.parse_type_casting_factor()
        assert factor == \
               TypeCastingFactor(
                   NegationFactor(
                       Constant(SourcePosition(1, len(string)), True), False), CurrencyType('EUR'))

    def test_multiply_expression(self):
        string = '4 * 4 / 5 % 3'
        parser = self._get_parser(string)
        expression = parser.parse_multiply_expression()
        assert expression == MultiplyExpression(
            type_casting_factor_factory(4, 1),
            [
                (MulOperator.MUL, type_casting_factor_factory(4, 5)),
                (MulOperator.DIV, type_casting_factor_factory(5, 9)),
                (MulOperator.MODULO, type_casting_factor_factory(3, 13)),
            ]
        )

    def test_sum_expression(self):
        string = '4 + 3 - 3'
        parser = self._get_parser(string)
        expression = parser.parse_sum_expression()
        assert expression == SumExpression(
            mul_expression_factory(4, 1),
            [
                (SumOperator.ADD, mul_expression_factory(3, 5)),
                (SumOperator.SUB, mul_expression_factory(3, 9)),
            ]
        )

    def test_sum_and_mul_expression(self):
        string = '4 * 3 - 3'
        parser = self._get_parser(string)
        expression = parser.parse_sum_expression()
        assert expression == SumExpression(
            MultiplyExpression(
                type_casting_factor_factory(4, 1),
                [(MulOperator.MUL, type_casting_factor_factory(3, 5))]
            ),
            [
                (SumOperator.SUB, mul_expression_factory(3, 9)),
            ]
        )

    def relationship_expression_test_factory(self, relationship_operand_string: str,
                                             relationship_operand_type: RelationshipOperator):
        string = f'1 {relationship_operand_string} 2'
        parser = self._get_parser(string)
        expression = parser.parse_relationship_expression()
        assert expression == RelationshipExpression(
            sum_expression_factory(1, 1),
            relationship_operand_type,
            sum_expression_factory(2, len(string))
        )

    def test_relationship_expression(self):
        self.relationship_expression_test_factory('==', RelationshipOperator.EQUAL_OPERATOR)
        self.relationship_expression_test_factory('!=', RelationshipOperator.NOT_EQUAL_OPERATOR)
        self.relationship_expression_test_factory('<', RelationshipOperator.LESS_THAN_OPERATOR)
        self.relationship_expression_test_factory('>', RelationshipOperator.GREATER_THAN_OPERATOR)
        self.relationship_expression_test_factory('<=', RelationshipOperator.LESS_THAN_OR_EQUAL_OPERATOR)
        self.relationship_expression_test_factory('>=', RelationshipOperator.GREATER_THAN_OPERATOR_OR_EQUAL_OPERATOR)

    def test_and_expression(self):
        string = 'true && false'
        parser = self._get_parser(string)
        expression = parser.parse_and_expression()
        assert expression == AndExpression(
            [
                relationship_expression_factory(True, 4),
                relationship_expression_factory(False, len(string)),

            ]
        )

    def test_or_expression(self):
        string = 'true || false'
        parser = self._get_parser(string)
        expression = parser.parse_expression()
        assert expression == Expression(
            [
                and_expression_factory(True, 4),
                and_expression_factory(False, len(string)),
            ]
        )

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
