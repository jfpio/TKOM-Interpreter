from builtins import str
from functools import reduce
from typing import Dict, Union, Optional

from interpreter.environment.frame import Frame
from interpreter.models.base import Constant
from interpreter.models.constants import SimpleTypes, RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION, \
    ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION
from interpreter.models.declarations import ParseTree, VariableDeclaration, CurrencyDeclaration, FunctionDeclaration
from interpreter.models.expressions import Expression, AndExpression, RelationshipExpression, MultiplyExpression, \
    SumExpression, TypeCastingFactor, NegationFactor
from interpreter.environment.semantic_errors import SemanticError, SemanticErrorCode, SemanticTypeError
from interpreter.environment.types import SimpleTypesIntoEnvironmentTypes, EnvironmentTypesIntoTypes, EnvironmentTypes
from interpreter.models.statements import ReturnStatement, IfStatement, Statements
from interpreter.source.source_position import SourcePosition


class Environment:
    def __init__(self, parse_tree: ParseTree):
        self.global_variables = {}
        self.functions_declarations = {}
        self.currency_declarations = {}
        self.frames_stack = []

        for declaration in parse_tree.declarations:
            declaration.accept(self, True)

        self.current_frame = Frame(
            self.functions_declarations['main'],
            SourcePosition(0, 0),
            []
        )

    def run_main(self) -> Optional[EnvironmentTypes]:
        main_function = self.functions_declarations['main']
        return main_function.statements.accept(self)

    def visit_variable_declaration(self, declaration: VariableDeclaration, global_declaration: bool):
        if global_declaration:
            scope = self.global_variables
        else:
            scope = self.current_frame.local_variables
        if declaration.id in scope:
            raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.id)
        scope[declaration.id] = declaration

    def visit_currency_declaration(self, declaration: CurrencyDeclaration):
        if declaration.name in self.currency_declarations:
            raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.name)
        self.currency_declarations[declaration.name] = declaration

    def visit_function_declaration(self, declaration: FunctionDeclaration):
        if declaration.id in self.functions_declarations:
            raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.id)
        self.functions_declarations[declaration.id] = declaration

    def visit_function_call(self, declaration: FunctionDeclaration):
        pass

    def visit_statements(self, statements: Statements):
        for statement in statements.list_of_statements:
            return_value = None
            while return_value is None:
                return_value = statement.accept(self)
            return return_value

    def visit_if_statement(self, if_statement: IfStatement):
        condition = if_statement.expression.accept(self)
        self.check_type(SimpleTypes.bool, condition, if_statement.expression.source_position)
        if condition:
            return if_statement.statements.accept(self)

    def visit_return_statement(self, return_statement: ReturnStatement):
        return_value = None
        if return_statement.expression:
            return_value = return_statement.expression.accept(self)

        self.current_frame.check_return_value(return_value)
        return return_value

    def visit_expression(self, expression: Expression) -> Optional[EnvironmentTypes]:
        if len(expression.and_expressions) == 1:
            and_expression = expression.and_expressions[0]
            return and_expression.accept(self)

        and_expressions = []
        for exp in expression.and_expressions:
            exp_result = exp.accept(self)
            self.check_type(SimpleTypes.bool, exp_result, exp.source_position)
            and_expressions.append(exp_result)
        return reduce(lambda acc, x: acc or x, and_expressions)

    def visit_and_expression(self, expression: AndExpression) -> Optional[EnvironmentTypes]:
        if len(expression.relationship_expressions) == 1:
            relationship_expression = expression.relationship_expressions[0]
            return relationship_expression.accept(self)

        relationship_expressions = []
        for exp in expression.relationship_expressions:
            exp_result = exp.accept(self)
            self.check_type(SimpleTypes.bool, exp_result, exp.source_position)
            relationship_expressions.append(exp_result)
        return reduce(lambda acc, x: acc and x, relationship_expressions)

    def visit_relationship_expression(self, expression: RelationshipExpression) -> Optional[EnvironmentTypes]:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side = expression.left_side.accept(self)
        right_side = expression.right_side.accept(self)

        left_side_type = type(left_side)
        self.check_type(EnvironmentTypesIntoTypes[left_side_type], right_side, expression.right_side.source_position)
        operator = expression.operator
        relationship_function = RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION[operator]
        return relationship_function(left_side, right_side)

    def visit_arithmetic_expression(self, expression: Union[SumExpression, MultiplyExpression]) \
            -> Optional[EnvironmentTypes]:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side_type = type(expression.left_side)
        right_side = []
        for operator, expression in expression.right_side:
            expression_result = expression.accept(self)
            self.check_type(EnvironmentTypesIntoTypes[left_side_type], expression_result, expression.source_position)
            right_side.append((operator, expression_result))

        accumulator = expression.left_side.accept(self)
        for operator, arithmetic_expression in right_side:
            evaluate_function = ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION[operator]
            accumulator = evaluate_function(accumulator, arithmetic_expression)
        return accumulator

    def visit_type_casting_factor(self, factor: TypeCastingFactor) -> Optional[EnvironmentTypes]:
        if not factor.cast_type:
            return factor.negation_factor.accept(self)

        cast_type = SimpleTypesIntoEnvironmentTypes[factor.cast_type]
        return cast_type(factor.negation_factor.accept(self))

    def visit_negation_factor(self, negation_factor: NegationFactor):
        if negation_factor.is_negated:
            value = negation_factor.factor.accept(self)
            if not isinstance(value, bool):
                raise SemanticTypeError(negation_factor.source_position, SimpleTypes.bool, type(value))
            return not value
        return negation_factor.factor.accept(self)

    def visit_factor(self, constant: Constant) -> Optional[EnvironmentTypes]:
        return constant.value

    @staticmethod
    def check_type(value_type: SimpleTypes, value, source_position: SourcePosition) -> bool:
        if isinstance(value, SimpleTypesIntoEnvironmentTypes[value_type]):
            return True
        else:
            raise SemanticTypeError(source_position, value_type, EnvironmentTypesIntoTypes[type(value)])
