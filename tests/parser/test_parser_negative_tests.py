import io
from typing import List
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.lexer.lexer_error import LexerError
from interpreter.models.declarations import Declaration, ParseTree
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
from interpreter.source.source import Source


class TestParserNegative:
    def test_function_without_body(self):
        string = 'int main()'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_function_without_type(self):
        string = 'main(){}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_assigment_without_semicolon(self):
        string = 'int main() {a = 3}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_while_with_semicolon_before_body(self):
        string = 'int main(){while(true); {}}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_wrong_assign(self):
        string = 'int main(){3 = a;}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_wrong_string_concat(self):
        string = 'int main(){a = "bbbbb;}'
        with pytest.raises(LexerError):
            self.parse_program(string)

    def test_func_without_bracket(self):
        string = 'int main({a = 3;}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_func_without_curly_bracket(self):
        string = 'int main(){a = 3;'
        with pytest.raises(ParserError):
            self.parse_program(string)

    def test_func_with_currency_declaration(self):
        string = 'int main(){EUR := 3;}'
        with pytest.raises(ParserError):
            self.parse_program(string)

    @staticmethod
    def parse_program(string: str) -> ParseTree:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        parser = Parser(lexer)
        return parser.parse_program()
