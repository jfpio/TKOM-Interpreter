import io

from interpreter.environment.environment import Environment
from interpreter.lexer.lexer import Lexer
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class TestEnvironment:
    def test_simple_main(self):
        string = 'int main(){return 3;}'
        source = Source(io.StringIO(string))
        parser = Parser(Lexer(source))
        env = Environment(parser.parse_program())
        assert env.run_main() == '3'
