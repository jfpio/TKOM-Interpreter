import io

from interpreter.lexer.lexer import Lexer
from interpreter.__main__ import Interpreter
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class TestInterpreter:
    pass
    # def test_simple_main(self):
    #     string = 'int main(){return 3;}'
    #     source = Source(io.StringIO(string))
    #     parser = Parser(Lexer(source))
    #     interpreter = Interpreter(parser)
    #     assert interpreter.run_code() == '3'
