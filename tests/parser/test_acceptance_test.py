import io
from typing import List
import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.models.declarations import Declaration
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
from interpreter.source.source import Source


class TestParserAcceptance:
    def test_acceptance_1(self):
        string = 'int main(){}'
        self.parse_program(string)

    def test_acceptance_2(self):
        string = 'int main(){a = a + 3;}'
        self.parse_program(string)

    def test_acceptance_3(self):
        string = \
            '''
            int a = 3;
            int main(){a = a + 3; return a;}
            '''
        self.parse_program(string)

    @staticmethod
    def parse_program(string: str) -> List[Declaration]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        parser = Parser(lexer)
        return parser.parse_program()
