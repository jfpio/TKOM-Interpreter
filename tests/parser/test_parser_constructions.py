import io

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Constant, Variable
from interpreter.parser.parser import Parser
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition


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
        pass  # TODO Add function call

    def test_nested_expression(self):
        pass  # TODO Add nested expression

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
