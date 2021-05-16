import io

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Constant, Variable, FunctionCall
from interpreter.parser.parser import Parser
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from tests.parser.utils import simple_expression_factory


class TestParserConstructions:
    def test_parse_constant(self):
        parser = self._get_parser("3")
        constant = parser.parse_factor()
        assert constant == Constant(3, SourcePosition(1, 1))

    def test_parse_variable(self):
        parser = self._get_parser('abc')
        variable = parser.parse_factor()
        assert variable == Variable('abc', SourcePosition(1, 3))

    def test_function_call(self):
        parser = self._get_parser('abc(a, b)')
        function_call = parser.parse_factor()
        assert function_call == FunctionCall('abc', [
            simple_expression_factory(Variable('a', SourcePosition(1, 5))),
            simple_expression_factory(Variable('b', SourcePosition(1, 8))),
        ], SourcePosition(1, 9))

    def test_nested_expression(self):
        parser = self._get_parser('(a)')
        nested_expression = parser.parse_factor()
        assert nested_expression == simple_expression_factory(Variable('a', SourcePosition(1, 2)))

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
