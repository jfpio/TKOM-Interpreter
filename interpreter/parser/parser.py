from typing import List, Union

from interpreter.lexer.lexer import Lexer
from interpreter.models.constants import token_type_into_relationship_operand, token_type_into_sum_operator, \
    token_type_into_mul_operator, Types, token_type_into_types, CurrencyType
from interpreter.models.declarations import Declaration, CurrencyDeclaration
from interpreter.models.base import FunctionCall, Constant, Variable, Factor
from interpreter.models.expressions import Expression, AndExpression, RelationshipExpression, SumExpression, \
    MultiplyExpression, TypeCastingFactor, NegationFactor
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
        # TODO Add rest of declarations

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
        """
        expression = andExpression, {"or", andExpression};
        """
        and_expressions = [self.parse_and_expression()]
        while self.token.type == TokenType.OR_OPERATOR:
            self.next_token()
            and_expressions.append(self.parse_and_expression())
        return Expression(and_expressions)

    def parse_and_expression(self) -> AndExpression:
        """
        andExpression = relationshipExpression, {"and", relationshipExpression};
        """
        relationship_expressions = [self.parse_relationship_expression()]
        while self.token.type == TokenType.AND_OPERATOR:
            self.next_token()
            relationship_expressions.append(self.parse_relationship_expression())
        return AndExpression(relationship_expressions)

    def parse_relationship_expression(self) -> RelationshipExpression:
        """
        relationshipExpression = sumExpression, [relationshipExpression, sumExpression];
        """
        left_side = self.parse_sum_expression()
        if self.token.type in token_type_into_relationship_operand:
            operator = token_type_into_relationship_operand[self.token.type]
            self.next_token()
            right_side = self.parse_sum_expression()
            return RelationshipExpression(left_side, operator, right_side)
        return RelationshipExpression(left_side)

    def parse_sum_expression(self) -> SumExpression:
        """
        sumExpression = multiplyExpression, {sumOperand, multiplyExpression};
        """
        left_side = self.parse_multiply_expression()
        right_side = []
        while self.token.type in [TokenType.ADD_OPERATOR, TokenType.SUB_OPERATOR]:
            add_operator = token_type_into_sum_operator[self.token.type]
            self.next_token()
            expression = self.parse_multiply_expression()
            right_side.append((add_operator, expression))
        return SumExpression(left_side, right_side)

    def parse_multiply_expression(self) -> MultiplyExpression:
        """
        multiplyExpression = typeCastingFactor, {multiplyOperand, typeCastingFactor};
        """
        left_side = self.parse_type_casting_factor()
        right_side = []
        while self.token.type in [TokenType.MUL_OPERATOR, TokenType.DIV_OPERATOR, TokenType.MODULO_OPERATOR]:
            mul_operator = token_type_into_mul_operator[self.token.type]
            self.next_token()
            expression = self.parse_type_casting_factor()
            right_side.append((mul_operator, expression))
        return MultiplyExpression(left_side, right_side)

    def parse_type_casting_factor(self) -> TypeCastingFactor:
        """
        typeCastingFactor = ["(", type, ")"], negationFactor;
        """
        if self.token.type == TokenType.LEFT_BRACKET:
            self.next_token()
            type = self.parse_type_name()
            self.expect(TokenType.RIGHT_BRACKET)
            self.next_token()
            return TypeCastingFactor(self.parse_negation_factor(), type)
        return TypeCastingFactor(self.parse_negation_factor())

    def parse_negation_factor(self) -> NegationFactor:
        """
        negationFactor = ["!"], factor;
        """
        token_type = self.token.type
        if token_type == TokenType.NEGATION_OPERATOR:
            self.next_token()
            return NegationFactor(self.parse_factor(), True)
        return NegationFactor(self.parse_factor(), False)

    def parse_function_call(self, id: str) -> FunctionCall:
        """
        (ID, [("(", args, ")"]) (*variable or function call*)
        """
        expressions = []
        while self.token.type != TokenType.RIGHT_BRACKET:
            while expression := self.parse_expression():
                expressions.append(expression)
                if self.token.type != TokenType.COMMA:
                    break
                self.next_token()
        return FunctionCall(id, expressions, self.token.source_position)

    def parse_factor(self) -> Factor:
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
                self.next_token()
                return self.parse_function_call(id)
            else:
                variable = Variable(id, self.previous_token.source_position)
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

    def parse_type_name(self) -> Union[Types, CurrencyType]:
        """
        type = "int"
            | "float"
            | "string"
            | "bool"
            | "void"
            | currency_ID
        ;
        """
        if self.token.type in token_type_into_types:
            type = token_type_into_types[self.token.type]
            self.next_token()
            return type
        elif self.token.type == TokenType.CURRENCY:
            type = CurrencyType(self.token.value)
            self.next_token()
            return type
        raise ParserError(self.token.source_position, self.token.type,
                          list(token_type_into_types.keys()) + [TokenType.CURRENCY])
