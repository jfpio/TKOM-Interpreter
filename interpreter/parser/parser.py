from typing import List, Optional

from interpreter.lexer.lexer import Lexer
from interpreter.parser.parser_error import ParserError
from interpreter.semantics import Node, Statement, CurrencyDeclaration
from interpreter.token.token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = lexer.get_next_token()

    def next_token(self):
        self.token = self.lexer.get_next_token()

    def expect(self, *args: TokenType) -> bool:
        for token_type in args:
            if self.token.type == token_type:
                return True
        raise ParserError(self.token.source_position, self.token.type, args)

    def parse_program(self) -> List[Statement]:
        statements = []
        while self.token.type != TokenType.EOF:
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self) -> Statement:
        if self.token.type == TokenType.CURRENCY:
            return self.parse_currency_assignment()

    def parse_currency_assignment(self) -> CurrencyDeclaration:
        """
        currencyDeclaration = currency_ID, ":=", float | int, ";";
        """
        currency_name = self.token.value
        self.next_token()

        self.expect(TokenType.CURRENCY_DECLARATION_OPERATOR)
        self.next_token()

        self.expect(TokenType.INT_VALUE, TokenType.FLOAT_VALUE)
        currency_value = self.token.value
        self.next_token()

        self.expect(TokenType.SEMICOLON)
        self.next_token()

        return CurrencyDeclaration(currency_name, currency_value)
