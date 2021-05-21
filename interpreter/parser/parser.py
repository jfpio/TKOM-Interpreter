from typing import List, Union, Optional

from interpreter.lexer.lexer import Lexer
from interpreter.models.constants import token_type_into_relationship_operand, token_type_into_sum_operator, \
    token_type_into_mul_operator, Types, token_type_into_types, CurrencyType
from interpreter.models.declarations import Declaration, CurrencyDeclaration, VariableDeclaration, FunctionDeclaration
from interpreter.models.base import FunctionCall, Constant, Variable, Factor, Assignment, Param
from interpreter.models.expressions import Expression, AndExpression, RelationshipExpression, SumExpression, \
    MultiplyExpression, TypeCastingFactor, NegationFactor
from interpreter.models.statements import ReturnStatement, IfStatement, WhileStatement, \
    Statements, StatementsTypes
from interpreter.parser.parser_error import ParserError
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.token = lexer.get_next_token()
        self.previous_token = self.token  # TODO remove that

    def next_token(self):
        self.previous_token = self.token
        self.token = self.lexer.get_next_token()

    def expect_token(self, *args: TokenType) -> bool:
        for token_type in args:
            if self.token.type == token_type:
                return True
        raise ParserError(self.token.source_position, self.token.type, list(args))

    def consume_token(self, *args: TokenType) -> Token:
        self.expect_token(*args)
        token = self.token
        self.next_token()
        return token

    def parse_program(self) -> List[Declaration]:
        """
        program = declaration, {declaration};
        """
        declarations = [self.parse_declaration()]
        while self.token.type != TokenType.EOF:
            declarations.append(self.parse_declaration())
        return declarations

    def parse_declaration(self) -> Declaration:
        """
        declaration = (varDeclaration | currencyDeclaration, ";") |  functionDeclaration;
        """
        declaration = self.parse_currency_declaration() or self.parse_function_declaration_or_variable_declaration()
        if type(declaration) is VariableDeclaration or type(declaration) is CurrencyDeclaration:
            self.consume_token(TokenType.SEMICOLON)

        if declaration is None:
            raise ParserError(
                self.token.source_position, self.token.type, [TokenType.CURRENCY] + list(token_type_into_types.keys())
            )
        return declaration

    def parse_currency_declaration(self) -> Optional[CurrencyDeclaration]:
        """
        currencyDeclaration = currency_ID, ":=", float | int;
        """
        if self.token.type != TokenType.CURRENCY:
            return None
        currency_token = self.consume_token(TokenType.CURRENCY)
        currency_name = currency_token.value

        self.consume_token(TokenType.CURRENCY_DECLARATION_OPERATOR)
        value_token = self.consume_token(TokenType.INT_VALUE, TokenType.FLOAT_VALUE)
        currency_value = value_token.value
        currency_declaration = CurrencyDeclaration(value_token.source_position, currency_name, currency_value)
        return currency_declaration

    def parse_function_declaration_or_variable_declaration(self) \
            -> Optional[Union[FunctionDeclaration, VariableDeclaration]]:
        """
        functionDeclaration = type, ID, "(", parms, ")", "{", statements, "}";
        varDeclaration = type, ID, ['=', expression];
        """

        if self.token.type not in token_type_into_types:
            return None
        type = token_type_into_types[self.token.type]
        self.next_token()

        id_token = self.consume_token(TokenType.ID)
        id = id_token.value

        declaration = self.parse_rest_of_function_declaration(type, id) \
                      or self.parse_rest_of_variable_declaration(type, id)
        return declaration

    def parse_rest_of_function_declaration(self, type: Types, id: str) -> Optional[FunctionDeclaration]:
        """
        functionDeclaration = type, ID, "(", parms, ")", "{", statements, "}";
        """
        if self.token.type != TokenType.LEFT_BRACKET:
            return None
        self.consume_token(TokenType.LEFT_BRACKET)
        params = self.parse_params()
        self.consume_token(TokenType.RIGHT_BRACKET)
        self.consume_token(TokenType.LEFT_CURLY_BRACKET)
        statements = self.parse_statements()
        self.consume_token(TokenType.RIGHT_CURLY_BRACKET)
        return FunctionDeclaration(self.previous_token.source_position, type, id, params, statements)

    def parse_rest_of_variable_declaration(self, type: Types, id: str) -> VariableDeclaration:
        """
        varDeclaration = type, ID, ['=', expression];
        """
        if self.token.type == TokenType.ASSIGN_OPERATOR:
            self.next_token()
            expression = self.parse_expression()
            return VariableDeclaration(self.previous_token.source_position, type, id, expression)
        return VariableDeclaration(self.previous_token.source_position, type, id, None)

    def parse_assignment_with_id(self, id: str) -> Assignment:
        """
        restOfAssignment = "=", expression;
        """
        self.expect_token(TokenType.ASSIGN_OPERATOR)
        self.next_token()

        expression = self.parse_expression()
        return Assignment(self.previous_token.source_position, id, expression)

    def parse_statements(self) -> Statements:
        """
        statements = {
            (
                varDeclaration
                | currencyDeclaration
                | ID, (restOfAssignment | restOfFunctionCall)
                | returnStatement
                | whileStatement
                | ifStatement
            ), ";"};
        """
        statements: List[StatementsTypes] = []
        while True:
            token_type = self.token.type
            if token_type in token_type_into_types:
                type = token_type_into_types[token_type]
                self.next_token()
                self.expect_token(TokenType.ID)
                id = self.token.value
                self.next_token()
                statements.append(self.parse_rest_of_variable_declaration(type, id))
            elif token_type == TokenType.CURRENCY:
                statements.append(self.parse_currency_declaration())
            elif token_type == TokenType.ID:
                id = self.token.value
                self.next_token()
                if self.token.type == TokenType.ASSIGN_OPERATOR:
                    statements.append(self.parse_assignment_with_id(id))
                else:
                    statements.append(self.parse_function_call(id))
            elif token_type == TokenType.RETURN_NAME:
                statements.append(self.parse_return_statement())
            elif token_type == TokenType.WHILE_NAME:
                statements.append(self.parse_while_statement())
            elif token_type == TokenType.IF_NAME:
                statements.append(self.parse_if_statement())
            else:
                break
            self.expect_token(TokenType.SEMICOLON)
            self.next_token()

        return Statements(statements)

    def parse_return_statement(self) -> ReturnStatement:
        """
        returnStatement = "return", [expression];
        """
        self.next_token()
        if self.token.type == TokenType.SEMICOLON:
            return ReturnStatement(self.previous_token.source_position, None)
        expression = self.parse_expression()
        return ReturnStatement(self.previous_token.source_position, expression)

    def parse_while_statement(self) -> WhileStatement:
        """
        whileStatement = "while", "(", expression, ")", "{", statements, "}";
        """
        self.next_token()
        self.expect_token(TokenType.LEFT_BRACKET)
        self.next_token()

        expression = self.parse_expression()
        self.expect_token(TokenType.RIGHT_BRACKET)
        self.next_token()
        self.expect_token(TokenType.LEFT_CURLY_BRACKET)
        self.next_token()
        statements = self.parse_statements()
        self.expect_token(TokenType.RIGHT_CURLY_BRACKET)
        self.next_token()
        return WhileStatement(self.previous_token.source_position, expression, statements)

    def parse_if_statement(self) -> IfStatement:
        """
        ifStatement = "if", "(", expression, ")", "{", statements, "}";
        """
        self.next_token()
        self.expect_token(TokenType.LEFT_BRACKET)
        self.next_token()

        expression = self.parse_expression()
        self.expect_token(TokenType.RIGHT_BRACKET)
        self.next_token()
        self.expect_token(TokenType.LEFT_CURLY_BRACKET)
        self.next_token()
        statements = self.parse_statements()
        self.expect_token(TokenType.RIGHT_CURLY_BRACKET)
        self.next_token()
        return IfStatement(self.previous_token.source_position, expression, statements)

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
            self.expect_token(TokenType.RIGHT_BRACKET)
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
        (ID, [restOfFunctionCall]) (*variable or function call*)
        restOfFunctionCall = "(", args, ")";
        args = [expression, {",", expression}];
        """
        expressions = []

        self.next_token()
        while self.token.type != TokenType.RIGHT_BRACKET:
            while expression := self.parse_expression():
                expressions.append(expression)
                if self.token.type != TokenType.COMMA:
                    break
                self.next_token()

        self.next_token()
        return FunctionCall(self.previous_token.source_position, id, expressions)

    def parse_factor(self) -> Factor:
        """
        factor =
           "(", expression, ")"
           | (ID, [restOfFunctionCall]) (*variable or function call*)
           | constant
        ;
        """
        if self.token.type == TokenType.LEFT_BRACKET:
            self.next_token()
            expression = self.parse_expression()
            self.expect_token(TokenType.RIGHT_BRACKET)
            self.next_token()
            return expression

        elif self.token.type == TokenType.ID:
            id = self.token.value
            self.next_token()
            if self.token.type == TokenType.LEFT_BRACKET:
                return self.parse_function_call(id)
            else:
                variable = Variable(self.previous_token.source_position, id)
                return variable
        elif self.token.type in [TokenType.INT_VALUE,
                                 TokenType.FLOAT_VALUE,
                                 TokenType.STRING_VALUE,
                                 TokenType.BOOL_VALUE,
                                 TokenType.CURRENCY_VALUE]:
            constant = Constant(self.token.source_position, self.token.value)
            self.next_token()
            return constant

        raise ParserError(self.token.source_position, self.token.type, [], "Invalid factor, nested expression, "
                                                                           "constant, variable or function call "
                                                                           "expected")

    def parse_params(self) -> List[Param]:
        """
        parms = [type, ID, {",", type, ID}];
        """
        params = []
        token_type = self.token.type

        if token_type not in token_type_into_types:
            return []

        type = self.parse_type_name()
        self.expect_token(TokenType.ID)
        id = self.token.value
        params.append(Param(id, type))
        self.next_token()
        token_type = self.token.type

        while token_type == TokenType.COMMA:
            self.next_token()
            type = self.parse_type_name()
            self.expect_token(TokenType.ID)
            id = self.token.value
            params.append(Param(id, type))
            self.next_token()
            token_type = self.token.type
        return params

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
            currency = CurrencyType(self.token.value)
            self.next_token()
            return currency
        raise ParserError(self.token.source_position, self.token.type,
                          list(token_type_into_types.keys()) + [TokenType.CURRENCY])
