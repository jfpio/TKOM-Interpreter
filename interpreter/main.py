from interpreter.environment.environment import Environment
from interpreter.parser.parser import Parser


class Interpreter:
    def __init__(self, parser: Parser):
        self.environment = Environment(parser.parse_program())

    def run_code(self) -> str:
        return '0'
