from interpreter.parser.parser import Parser


class Interpreter:
    def __init__(self, parser: Parser):
        self.parser = parser

    def run_code(self) -> str:
        return '0'
