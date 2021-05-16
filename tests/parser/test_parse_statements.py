import io

import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Variable, Assignment, Constant, FunctionCall
from interpreter.models.constants import Types
from interpreter.models.declarations import VariableDeclaration, CurrencyDeclaration
from interpreter.models.statements import ReturnStatement, IfStatement, Statements, WhileStatement
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
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

    def test_parse_if_statement_1(self):
        string = 'if(a){a = 3;}'
        parser = self._get_parser(string)
        if_statement = parser.parse_if_statement()
        assert if_statement == IfStatement(
            SourcePosition(1, 13),
            simple_expression_factory(Variable(SourcePosition(1, 4), 'a')),
            Statements([Assignment(SourcePosition(1, 11), 'a',
                                   simple_expression_factory(Constant(SourcePosition(1, 11), 3)))])
        )

    def test_parse_if_statement_2(self):
        string = 'if(a){}'
        parser = self._get_parser(string)
        if_statement = parser.parse_if_statement()
        assert if_statement == IfStatement(
            SourcePosition(1, 7),
            simple_expression_factory(Variable(SourcePosition(1, 4), 'a')),
            Statements([])
        )

    def test_parse_if_statement_3(self):
        string = 'if(){}'
        with pytest.raises(ParserError):
            parser = self._get_parser(string)
            parser.parse_if_statement()

    def test_parse_while_statement_1(self):
        string = 'while(a){a = 3;}'
        parser = self._get_parser(string)
        while_statement = parser.parse_while_statement()
        assert while_statement == WhileStatement(
            SourcePosition(1, 16),
            simple_expression_factory(Variable(SourcePosition(1, 7), 'a')),
            Statements([Assignment(SourcePosition(1, 14), 'a',
                                   simple_expression_factory(Constant(SourcePosition(1, 14), 3)))])
        )

    def test_parse_while_statement_2(self):
        string = 'while(a){}'
        parser = self._get_parser(string)
        while_statement = parser.parse_while_statement()
        assert while_statement == WhileStatement(
            SourcePosition(1, 10),
            simple_expression_factory(Variable(SourcePosition(1, 7), 'a')),
            Statements([])
        )

    def test_parse_while_statement_3(self):
        string = 'while(){}'
        with pytest.raises(ParserError):
            parser = self._get_parser(string)
            parser.parse_while_statement()

    def test_parse_variable_and_currency_declaration_statements(self):
        string = 'int a = 3; EUR := 3;'
        parser = self._get_parser(string)
        statement = parser.parse_statements()
        assert statement == Statements([
            VariableDeclaration(
                SourcePosition(1, 9), Types.int, 'a', simple_expression_factory(Constant(SourcePosition(1, 9), 3))
            ),
            CurrencyDeclaration(SourcePosition(1, 19), 'EUR', 3)
        ])

    def test_parse_assignment_and_function_call_statements(self):
        string = 'a=3; a();'
        parser = self._get_parser(string)
        statement = parser.parse_statements()
        assert statement == Statements([
            Assignment(
                SourcePosition(1, 3), 'a', simple_expression_factory(Constant(SourcePosition(1, 3), 3))
            ),
            FunctionCall(SourcePosition(1, 8), 'a', [])
        ])

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
