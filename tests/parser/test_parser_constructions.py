import io

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Constant, Variable, FunctionCall, Assignment
from interpreter.parser.parser import Parser
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from tests.parser.utils import simple_expression_factory


class TestParserConstructions:
    def test_parse_constant(self):
        parser = self._get_parser("3")
        constant = parser.parse_factor()
        assert constant == Constant(SourcePosition(1, 1), 3)

    def test_parse_variable(self):
        parser = self._get_parser('abc')
        variable = parser.parse_factor()
        assert variable == Variable(SourcePosition(1, 3), 'abc')

    def test_function_call(self):
        parser = self._get_parser('abc(a, b)')
        function_call = parser.parse_factor()
        assert function_call == FunctionCall(SourcePosition(1, 9), 'abc', [
            simple_expression_factory(Variable(SourcePosition(1, 5), 'a')),
            simple_expression_factory(Variable(SourcePosition(1, 8), 'b')),
        ])

    def test_nested_expression(self):
        parser = self._get_parser('(a)')
        nested_expression = parser.parse_factor()
        assert nested_expression == simple_expression_factory(Variable(SourcePosition(1, 2), 'a'))

    def test_parse_assignment(self):
        parser = self._get_parser('= 3')
        assigment = parser.parse_assignment_with_id('a')
        assert assigment == Assignment(SourcePosition(1, 3), 'a',
                                       simple_expression_factory(Constant(SourcePosition(1, 3), 3)))

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
