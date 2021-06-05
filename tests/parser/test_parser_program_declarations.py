import io
from typing import List
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.models.base import Constant, Param, Variable
from interpreter.models.constants import Types
from interpreter.models.declarations import CurrencyDeclaration, Declaration, VariableDeclaration, FunctionDeclaration
from interpreter.models.statements import Statements, ReturnStatement
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from tests.parser.utils import simple_expression_factory


class TestParserDeclarations:
    def test_currency_declaration(self):
        string = 'EUR := 4.92;'
        statements = self._get_program_declarations(string)
        currency_declaration = statements[0]

        assert currency_declaration == CurrencyDeclaration(SourcePosition(1, 11), 'EUR', 4.92)

    def test_currency_declaration_error1(self):
        string = 'EUR = 4.92;'
        with pytest.raises(ParserError):
            self._get_program_declarations(string)

    def test_currency_declaration_error2(self):
        string = 'EUR := 4.92'
        with pytest.raises(ParserError):
            self._get_program_declarations(string)

    def test_currency_declaration_error3(self):
        string = 'EUR := ;'
        with pytest.raises(ParserError):
            self._get_program_declarations(string)

    def test_variable_declaration_1(self):
        string = 'int a = 4.92;'
        declarations = self._get_program_declarations(string)
        declaration = declarations[0]
        assert declaration == VariableDeclaration(SourcePosition(1, 12), Types.int, 'a',
                                                  simple_expression_factory(Constant(SourcePosition(1, 12), 4.92)))

    def test_variable_declaration_2(self):
        string = 'int a;'
        declarations = self._get_program_declarations(string)
        declaration = declarations[0]
        assert declaration == VariableDeclaration(SourcePosition(1, 5), Types.int, 'a', None)

    def test_function_declaration_1(self):
        string = 'int a(int b, int c){return b;}'
        declarations = self._get_program_declarations(string)
        declaration = declarations[0]
        assert declaration == FunctionDeclaration(
            SourcePosition(1, len(string)), Types.int, 'a',
            [Param('b', Types.int), Param('c', Types.int)],
            Statements([ReturnStatement(SourcePosition(1, 28),
                                        simple_expression_factory(Variable(SourcePosition(1, 28), 'b')))]))

    def test_function_declaration_2(self):
        string = 'int a(){}'
        declarations = self._get_program_declarations(string)
        declaration = declarations[0]
        assert declaration == FunctionDeclaration(
            SourcePosition(1, len(string)), Types.int, 'a',
            [],
            Statements([]))

    @staticmethod
    def _get_program_declarations(string: str) -> List[Declaration]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        parser = Parser(lexer)
        parse_tree = parser.parse_program()
        return parse_tree.declarations

    @staticmethod
    def _get_parser(string: str) -> Parser:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return Parser(lexer)
