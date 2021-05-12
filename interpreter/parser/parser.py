from typing import List

from interpreter.lexer.lexer import Lexer
from interpreter.parser.syntax_error import SyntaxError
from interpreter.semantics import Node, Statement
from interpreter.token.token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = lexer.get_next_token()

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def expect(self, type: TokenType) -> bool:
        if self.token.type == type:
            return True
        raise SyntaxError(self.token.source_position, type, self.token.type)

    def parse_program(self) -> List[Statement]:
        statements = []
        while self.token.type == TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> Statement:
        return Statement()
