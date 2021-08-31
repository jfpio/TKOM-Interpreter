import sys

from interpreter.environment.environment import Environment
from interpreter.lexer.lexer import Lexer
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class Interpreter:
    def __init__(self, source: Source):
        lexer = Lexer(source)
        parser = Parser(lexer)
        self.environment = Environment(parser.parse_program())
        self.result = self.environment.run_main()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as file:
            source = Source(file)
            interpreter = Interpreter(source)
            print(str(interpreter.result))
