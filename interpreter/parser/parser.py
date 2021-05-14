from typing import List, Optional, Union

from interpreter.lexer.lexer import Lexer
from interpreter.models.declarations import Declaration, CurrencyDeclaration
from interpreter.models.base import Currency, FunctionCall, Constant, Variable
from interpreter.models.expressions import Expression
from interpreter.parser.parser_error import ParserError
from interpreter.token.token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = lexer.get_next_token()
        self.previous_token = self.token

    def next_token(self):
        self.previous_token = self.token
        self.token = self.lexer.get_next_token()

    def expect(self, *args: TokenType) -> bool:
        for token_type in args:
            if self.token.type == token_type:
                return True
        raise ParserError(self.token.source_position, self.token.type, list(args))

    def parse_program(self) -> List[Declaration]:
        statements = []
        while self.token.type != TokenType.EOF:
            statements.append(self.parse_declarations())
        return statements

    def parse_declarations(self) -> Declaration:
        if self.token.type == TokenType.CURRENCY:
            return self.parse_currency_declarations()

    def parse_currency_declarations(self) -> CurrencyDeclaration:
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

    def parse_expression(self) -> Expression:
        # TODO Handle right bracket
        ...

    def parse_function_call(self, id: str) -> FunctionCall:
        # TODO Remember that this function don't need to end with semicolon
        ...

    def parse_factor(self) -> Union[Expression, FunctionCall, Variable, Constant]:
        """
        factor =
           "(", expression, ")"
           | (ID, [("(", args, ")"]) (*variable or function call*)
           | constant
        ;
        """
        if self.token.type == TokenType.LEFT_BRACKET:
            self.next_token()
            expression = self.parse_expression()
            self.expect(TokenType.RIGHT_BRACKET)
            self.next_token()
            return expression

        elif self.token.type == TokenType.ID:
            id = self.token.value
            self.next_token()
            if self.token.type == TokenType.LEFT_BRACKET:
                return self.parse_function_call(id)
            else:
                variable = Variable(id, self.previous_token.source_position)
                self.next_token()
                return variable
        elif self.token.type in [TokenType.INT_VALUE,
                                 TokenType.FLOAT_VALUE,
                                 TokenType.STRING_VALUE,
                                 TokenType.BOOL_VALUE,
                                 TokenType.CURRENCY_VALUE]:
            constant = Constant(self.token.value, self.token.source_position)
            self.next_token()
            return constant

        raise ParserError(self.token.source_position, self.token.type, [], "Invalid factor, nested expression, "
                                                                           "constant, variable or function call "
                                                                           "expected")
