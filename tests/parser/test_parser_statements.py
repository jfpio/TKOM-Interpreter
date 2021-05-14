import io
from typing import List
import pytest

from interpreter.lexer.lexer import Lexer, tokens_generator
from interpreter.lexer.lexer_error import LexerError
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
from interpreter.semantics import Statement, CurrencyDeclaration
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestParserStatements:
    def test_currency_assignment_statement(self):
        string = 'EUR := 4.92;'
        statements = self._get_statements(string)
        currency_declaration = statements[0]

        assert currency_declaration == CurrencyDeclaration('EUR', 4.92)

    def test_currency_assignment_statement_error1(self):
        string = 'EUR = 4.92;'
        with pytest.raises(ParserError):
            self._get_statements(string)

    def test_currency_assignment_statement_error2(self):
        string = 'EUR := 4.92'
        with pytest.raises(ParserError):
            self._get_statements(string)

    def test_currency_assignment_statement_error3(self):
        string = 'EUR := ;'
        with pytest.raises(ParserError):
            self._get_statements(string)

    @staticmethod
    def _get_statements(string: str) -> List[Statement]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        parser = Parser(lexer)

        return parser.parse_program()
