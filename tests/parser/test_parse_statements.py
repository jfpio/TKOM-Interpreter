import io

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Variable
from interpreter.models.statements import ReturnStatement
from interpreter.parser.parser import Parser
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from tests.parser.utils import simple_expression_factory


class TestParserConstructions:
    def test_parse_return_statement_1(self):
        string = 'return;'
        parser = self._get_parser(string)
        return_statement = parser.parse_return_statement()
        assert return_statement == ReturnStatement(SourcePosition(1, 6), None)

    def test_parse_return_statement_2(self):
        string = 'return a;'
        parser = self._get_parser(string)
        return_statement = parser.parse_return_statement()
        assert return_statement == ReturnStatement(
            SourcePosition(1, 8),
            simple_expression_factory(Variable(SourcePosition(1, 8), 'a'))
        )

    def test_parse_compound_statement_variable_declaration(self):
        pass

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
