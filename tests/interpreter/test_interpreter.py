from typing import io

from interpreter.lexer.lexer import Lexer
from interpreter.main import Interpreter
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class TestIntegratedTokens:
    def test_simple_main(self):
        string = 'int main(){return 3;}'
        source = Source(io.StringIO(string))
        parser = Parser(Lexer(source))
        interpreter = Interpreter(parser)
        assert interpreter.run_code() == '3'
