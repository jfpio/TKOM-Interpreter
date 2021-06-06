from typing import List, Union, Optional

from interpreter.lexer.lexer import Lexer
from interpreter.models.constants import TOKEN_TYPE_INTO_RELATIONSHIP_OPERAND, TOKEN_TYPE_INTO_SUM_OPERATOR, \
    token_type_into_mul_operator, Types, TOKEN_TYPES_INTO_TYPES, CurrencyType, POSSIBLE_TYPES
from interpreter.models.declarations import Declaration, CurrencyDeclaration, VariableDeclaration, \
    FunctionDeclaration, ParseTree
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

    def parse_program(self) -> ParseTree:
        """
        program = declaration, {declaration};
        """
        declarations = [self.parse_declaration()]
        while self.token.type != TokenType.EOF:
            declarations.append(self.parse_declaration())
        return ParseTree(declarations)

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

    def advance_token(self) -> Token:
        token = self.token
        self.next_token()
        return token

    def parse_declaration(self) -> Declaration:
        """
        declaration = (varDeclaration | currencyDeclaration, ";") |  functionDeclaration;
        """
        var_type = self.parse_type_name()
        declaration = self.parse_rest_of_currency_declaration(var_type) \
                      or self.parse_rest_of_function_declaration_or_variable_declaration(var_type)

        if type(declaration) is VariableDeclaration or type(declaration) is CurrencyDeclaration:
            self.consume_token(TokenType.SEMICOLON)

        if declaration is None:
            raise ParserError(
                self.token.source_position, self.token.type, [TokenType.CURRENCY] + list(TOKEN_TYPES_INTO_TYPES.keys())
            )
        return declaration

    def parse_rest_of_currency_declaration(self, currency: CurrencyType) -> Optional[CurrencyDeclaration]:
        """
        currencyDeclaration = currency_ID, ":=", float;
        """
        if self.token.type != TokenType.CURRENCY_DECLARATION_OPERATOR:
            return None
        self.consume_token(TokenType.CURRENCY_DECLARATION_OPERATOR)

        currency_name = currency.name
        value_token = self.consume_token(TokenType.FLOAT_VALUE)
        currency_value = value_token.value
        currency_declaration = CurrencyDeclaration(value_token.source_position, currency_name, currency_value)
        return currency_declaration

    def parse_rest_of_function_declaration_or_variable_declaration(self, type: Types) \
            -> Optional[Union[FunctionDeclaration, VariableDeclaration]]:
        """
        functionDeclaration = type, ID, "(", parms, ")", "{", statements, "}";
        varDeclaration = type, ID, ['=', expression];
        """

        if self.token.type != TokenType.ID:
            return None
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

    def parse_variable_declaration(self) -> Optional[VariableDeclaration]:
        if self.token.type not in TOKEN_TYPES_INTO_TYPES and self.token.type != TokenType.CURRENCY:
            return None
        type = self.parse_type_name()
        id_token = self.consume_token(TokenType.ID)
        return self.parse_rest_of_variable_declaration(type, id_token.value)

    def parse_rest_of_variable_declaration(self, type: Types, id: str) -> VariableDeclaration:
        """
        varDeclaration = type, ID, ['=', expression];
        """
        if self.token.type == TokenType.ASSIGN_OPERATOR:
            self.next_token()
            expression = self.parse_expression()
            return VariableDeclaration(self.previous_token.source_position, type, id, expression)
        return VariableDeclaration(self.previous_token.source_position, type, id, None)

    def parse_assignment_with_id(self, id: str) -> Optional[Assignment]:
        """
        restOfAssignment = "=", expression;
        """
        if self.token.type != TokenType.ASSIGN_OPERATOR:
            return None
        self.consume_token(TokenType.ASSIGN_OPERATOR)
        expression = self.parse_expression()
        return Assignment(self.previous_token.source_position, id, expression)

    def parse_statements(self) -> Statements:
        """
        statements = {
              ((
                 varDeclaration
                 | currencyDeclaration
                 | ID, (restOfAssignment | restOfFunctionCall)
                 | returnStatement
              ), ";")
              | (
                whileStatement
                | ifStatement
              )
        };
        """
        statements: List[StatementsTypes] = []
        while True:
            statement = self.parse_variable_declaration() \
                        or self.parse_assignment_or_function_call() \
                        or self.parse_return_statement() \
                        or self.parse_while_statement() \
                        or self.parse_if_statement()
            if type(statement) is WhileStatement or type(statement) is IfStatement:
                statements.append(statement)
            elif statement:
                statements.append(statement)
                self.consume_token(TokenType.SEMICOLON)
            else:
                break
        return Statements(statements)

    def parse_assignment_or_function_call(self) -> Optional[Union[Assignment, FunctionCall]]:
        if self.token.type != TokenType.ID:
            return None
        id_token = self.advance_token()
        id = id_token.value
        return self.parse_assignment_with_id(id) or self.parse_function_call(id)

    def parse_return_statement(self) -> Optional[ReturnStatement]:
        """
        returnStatement = "return", [expression];
        """
        if self.token.type != TokenType.RETURN_NAME:
            return None

        self.consume_token(TokenType.RETURN_NAME)
        if self.token.type == TokenType.SEMICOLON:
            return ReturnStatement(self.previous_token.source_position, None)
        expression = self.parse_expression()
        return ReturnStatement(self.previous_token.source_position, expression)

    def parse_while_statement(self) -> Optional[WhileStatement]:
        """
        whileStatement = "while", "(", expression, ")", "{", statements, "}";
        """
        if self.token.type != TokenType.WHILE_NAME:
            return None
        self.advance_token()
        self.consume_token(TokenType.LEFT_BRACKET)

        expression = self.parse_expression()

        self.consume_token(TokenType.RIGHT_BRACKET)
        self.consume_token(TokenType.LEFT_CURLY_BRACKET)

        statements = self.parse_statements()

        self.consume_token(TokenType.RIGHT_CURLY_BRACKET)
        return WhileStatement(self.previous_token.source_position, expression, statements)

    def parse_if_statement(self) -> Optional[IfStatement]:
        """
        ifStatement = "if", "(", expression, ")", "{", statements, "}";
        """
        if self.token.type != TokenType.IF_NAME:
            return None
        self.advance_token()
        self.consume_token(TokenType.LEFT_BRACKET)

        expression = self.parse_expression()

        self.consume_token(TokenType.RIGHT_BRACKET)
        self.consume_token(TokenType.LEFT_CURLY_BRACKET)

        statements = self.parse_statements()

        self.consume_token(TokenType.RIGHT_CURLY_BRACKET)
        return IfStatement(self.previous_token.source_position, expression, statements)

    def parse_expression(self) -> Optional[Expression]:
        """
        expression = andExpression, {"or", andExpression};
        """
        and_expression = self.parse_and_expression()
        if and_expression is None:
            return None

        and_expressions = [and_expression]
        while self.token.type == TokenType.OR_OPERATOR:
            self.next_token()
            and_expressions.append(self.parse_and_expression())
        return Expression(self.previous_token.source_position, and_expressions)

    def parse_and_expression(self) -> Optional[AndExpression]:
        """
        andExpression = relationshipExpression, {"and", relationshipExpression};
        """
        relationship_expression = self.parse_relationship_expression()
        if relationship_expression is None:
            return None

        relationship_expressions = [relationship_expression]
        while self.token.type == TokenType.AND_OPERATOR:
            self.next_token()
            relationship_expressions.append(self.parse_relationship_expression())
        return AndExpression(self.previous_token.source_position, relationship_expressions)

    def parse_relationship_expression(self) -> Optional[RelationshipExpression]:
        """
        relationshipExpression = sumExpression, [relationshipExpression, sumExpression];
        """
        left_side = self.parse_sum_expression()
        if left_side is None:
            return None

        if self.token.type in TOKEN_TYPE_INTO_RELATIONSHIP_OPERAND:
            operator = TOKEN_TYPE_INTO_RELATIONSHIP_OPERAND[self.token.type]
            self.next_token()
            right_side = self.parse_sum_expression()
            return RelationshipExpression(self.previous_token.source_position, left_side, operator, right_side)
        return RelationshipExpression(self.previous_token.source_position, left_side)

    def parse_sum_expression(self) -> Optional[SumExpression]:
        """
        sumExpression = left_side, {sumOperand, left_side};
        """
        left_side = self.parse_multiply_expression()
        if left_side is None:
            return None

        right_side = []
        while self.token.type in [TokenType.ADD_OPERATOR, TokenType.SUB_OPERATOR]:
            add_operator = TOKEN_TYPE_INTO_SUM_OPERATOR[self.token.type]
            self.next_token()
            expression = self.parse_multiply_expression()
            right_side.append((add_operator, expression))
        return SumExpression(self.previous_token.source_position, left_side, right_side)

    def parse_multiply_expression(self) -> Optional[MultiplyExpression]:
        """
        left_side = typeCastingFactor, {multiplyOperand, typeCastingFactor};
        """
        left_side = self.parse_type_casting_factor()
        if left_side is None:
            return None

        right_side = []
        while self.token.type in [TokenType.MUL_OPERATOR, TokenType.DIV_OPERATOR, TokenType.MODULO_OPERATOR]:
            mul_operator = token_type_into_mul_operator[self.token.type]
            self.next_token()
            expression = self.parse_type_casting_factor()
            right_side.append((mul_operator, expression))
        return MultiplyExpression(self.previous_token.source_position, left_side, right_side)

    def parse_type_casting_factor(self) -> Optional[TypeCastingFactor]:
        """
        typeCastingFactor = ["(", type, ")"], negationFactor;
        """
        if self.token.type not in POSSIBLE_TYPES:
            negation_factor = self.parse_negation_factor()
            if negation_factor is None:
                return None
            else:
                return TypeCastingFactor(self.previous_token.source_position, negation_factor)

        type = self.parse_type_name()
        negation_factor = self.parse_negation_factor()
        return TypeCastingFactor(self.previous_token.source_position, negation_factor, type)

    def parse_negation_factor(self) -> Optional[NegationFactor]:
        """
        negationFactor = ["!"], factor;
        """
        if self.token.type != TokenType.NEGATION_OPERATOR:
            factor = self.parse_factor()
            if factor is None:
                return None
            else:
                return NegationFactor(self.previous_token.source_position, factor, False)
        self.consume_token(TokenType.NEGATION_OPERATOR)
        factor = self.parse_factor()
        return NegationFactor(self.previous_token.source_position, factor, True)

    def parse_factor(self) -> Factor:
        """
        factor =
           "(", expression, ")"
           | (ID, [restOfFunctionCall]) (*variable or function call*)
           | constant
        ;
        """
        factor = self.parse_nested_expression() or self.parse_function_call_or_variable() or self.parse_constant()
        if factor is None:
            raise ParserError(
                self.token.source_position, self.token.type, [],
                "Invalid factor, nested expression, constant, variable or function call expected"
            )
        return factor

    def parse_nested_expression(self) -> Optional[Expression]:
        """
        "(", expression, ")"
        """
        if self.token.type != TokenType.LEFT_BRACKET:
            return None

        self.consume_token(TokenType.LEFT_BRACKET)
        expression = self.parse_expression()
        self.consume_token(TokenType.RIGHT_BRACKET)
        return expression

    def parse_function_call_or_variable(self) -> Optional[Expression]:
        """
        (ID, [restOfFunctionCall]) (*variable or function call*)
        """
        if self.token.type != TokenType.ID:
            return None
        id_token = self.consume_token(TokenType.ID)
        id = id_token.value
        return self.parse_function_call(id) or Variable(self.previous_token.source_position, id)

    def parse_constant(self) -> Optional[Constant]:
        if self.token.type not in [TokenType.INT_VALUE,
                                   TokenType.FLOAT_VALUE,
                                   TokenType.STRING_VALUE,
                                   TokenType.BOOL_VALUE,
                                   TokenType.CURRENCY_VALUE]:
            return None
        constant = Constant(self.token.source_position, self.token.value)
        self.next_token()
        return constant

    def parse_function_call(self, id: str) -> Optional[FunctionCall]:
        """
        (ID, [restOfFunctionCall]) (*variable or function call*)
        restOfFunctionCall = "(", args, ")";
        args = [expression, {",", expression}];
        """
        if self.token.type != TokenType.LEFT_BRACKET:
            return None

        expressions = []
        self.consume_token(TokenType.LEFT_BRACKET)
        while self.token.type != TokenType.RIGHT_BRACKET:
            while expression := self.parse_expression():
                expressions.append(expression)
                if self.token.type != TokenType.COMMA:
                    break
                self.next_token()

        self.next_token()
        return FunctionCall(self.previous_token.source_position, id, expressions)

    def parse_params(self) -> List[Param]:
        """
        parms = [type, ID, {",", type, ID}];
        """
        params = []
        token_type = self.token.type

        if token_type not in TOKEN_TYPES_INTO_TYPES and token_type != TokenType.CURRENCY:
            return []

        type = self.parse_type_name()
        id_token = self.consume_token(TokenType.ID)
        id = id_token.value
        params.append(Param(id_token.source_position, id, type))

        while self.token.type == TokenType.COMMA:
            self.next_token()
            type = self.parse_type_name()
            self.expect_token(TokenType.ID)
            id = self.token.value
            params.append(Param(self.token.source_position, id, type))
            self.next_token()
        return params

    def parse_type_name(self) -> Optional[Union[Types, CurrencyType]]:
        """
        type = "int"
            | "float"
            | "string"
            | "bool"
            | "void"
            | currency_ID
        ;
        """
        if self.token.type in TOKEN_TYPES_INTO_TYPES:
            type = TOKEN_TYPES_INTO_TYPES[self.token.type]
            self.next_token()
            return type
        elif self.token.type == TokenType.CURRENCY:
            currency = CurrencyType(self.token.value)
            self.next_token()
            return currency
        raise ParserError(self.token.source_position, self.token.type,
                          list(TOKEN_TYPES_INTO_TYPES.keys()) + [TokenType.CURRENCY])
