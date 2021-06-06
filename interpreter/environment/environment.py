from builtins import str
from functools import reduce
from typing import Dict, Union

from interpreter.models.base import Constant
from interpreter.models.constants import Types, RelationshipOperator, RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION, \
    ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION
from interpreter.models.declarations import ParseTree, VariableDeclaration, CurrencyDeclaration, FunctionDeclaration
from interpreter.models.expressions import Expression, AndExpression, RelationshipExpression, MultiplyExpression, \
    SumExpression, TypeCastingFactor, NegationFactor
from interpreter.environment.semantic_errors import SemanticError, SemanticErrorCode, SemanticTypeError
from interpreter.environment.symbols import VarSymbol, CurrencySymbol, FunctionSymbol
from interpreter.environment.types import SimpleTypesIntoEnvironmentTypes, EnvironmentTypesIntoTypes, EnvironmentTypes
from interpreter.models.statements import ReturnStatement
from interpreter.source.source_position import SourcePosition


class Environment:
    def __init__(self, parse_tree: ParseTree):
        self.global_variables = Dict[str, VarSymbol]
        self.currency_declarations = Dict[str, CurrencySymbol]
        self.functions_declarations = {}
        self.local_variables = Dict[str, VarSymbol]

        for declaration in parse_tree.declarations:
            if isinstance(declaration, VariableDeclaration):
                declaration.accept(self, True)
            self.functions_declarations[declaration.id] = declaration

    def run_main(self):
        main_function = self.functions_declarations['main']
        return main_function.accept(self)

    def visit_variable_declaration(self, declaration: VariableDeclaration, global_declaration: bool):
        if global_declaration:
            scope = self.global_variables
        else:
            scope = self.local_variables
        if declaration.id in scope:
            raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.id)
        scope[declaration.id] = VarSymbol(
            declaration.id,
            declaration.type,
            declaration.expression.accept()
        )

    def visit_currency_declaration(self, declaration: CurrencyDeclaration):
        if declaration.name in self.currency_declarations:
            raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.name)
        self.currency_declarations[declaration.name] = CurrencySymbol(
            declaration.name,
            declaration.value
        )

    # def visit_function_declaration(self, declaration: FunctionDeclaration):
    #     if declaration.id in self.functions_declarations:
    #         raise SemanticError(declaration.source_position, SemanticErrorCode.DUPLICATE_ID, declaration.id)
    #     self.functions_declarations[declaration.id] = declaration

    def visit_function_call(self, declaration: FunctionDeclaration):
        for i in declaration.statements.list_of_statements:
            if isinstance(i, ReturnStatement):
                return i.expression.accept(self)

    def visit_expression(self, expression: Expression) -> EnvironmentTypes:
        if len(expression.and_expressions) == 1:
            and_expression = expression.and_expressions[0]
            return and_expression.accept(self)

        and_expressions = [exp.accept(self) for exp in expression.and_expressions]
        and_expressions = [exp for exp in and_expressions if self.check_type(Types.bool, exp)]
        return reduce(lambda acc, x: acc or x, and_expressions)

    def visit_and_expression(self, expression: AndExpression) -> EnvironmentTypes:
        if len(expression.relationship_expressions) == 1:
            relationship_expression = expression.relationship_expressions[0]
            return relationship_expression.accept(self)

        relationship_expressions = [exp.accept(self) for exp in expression.relationship_expressions]
        and_expressions = [exp for exp in relationship_expressions if self.check_type(Types.bool, exp)]
        return reduce(lambda acc, x: acc and x, and_expressions)

    def visit_relationship_expression(self, expression: RelationshipExpression) -> EnvironmentTypes:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side_type = type(expression.left_side)
        self.check_type(EnvironmentTypesIntoTypes[left_side_type], expression.right_side)
        operator = expression.operator
        relationship_function = RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION[operator]
        left_side = expression.left_side.accept(self)
        right_side = expression.right_side.accept(self)
        return relationship_function(left_side, right_side)

    def visit_arithmetic_expression(self, expression: Union[SumExpression, MultiplyExpression]) -> EnvironmentTypes:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side_type = type(expression.left_side)
        right_side = [(operator, expression) for operator, expression in expression.right_side
                      if self.check_type(EnvironmentTypesIntoTypes[left_side_type], expression)]

        accumulator = expression.left_side.accept(self)
        for operator, multiply_expression in right_side:
            evaluate_function = ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION[operator]
            accumulator = evaluate_function(accumulator, multiply_expression.accept(self))
        return accumulator

    def visit_type_casting_factor(self, factor: TypeCastingFactor) -> EnvironmentTypes:
        if not factor.cast_type:
            return factor.negation_factor.accept(self)

        cast_type = SimpleTypesIntoEnvironmentTypes[factor.cast_type]
        return cast_type(factor.negation_factor.accept(self))

    def visit_negation_factor(self, negation_factor: NegationFactor):
        if negation_factor.is_negated:
            value = negation_factor.factor.accept(self)
            if not isinstance(value, bool):
                raise SemanticTypeError(negation_factor.source_position, Types.bool, type(value))
            return not value
        return negation_factor.factor.accept(self)

    def visit_factor(self, constant: Constant) -> EnvironmentTypes:
        return constant.value

    @staticmethod
    def check_type(value_type: Types, value) -> bool:
        if isinstance(value, SimpleTypesIntoEnvironmentTypes[value_type]):
            return True
        else:
            # TODO Fix source position
            raise SemanticTypeError(SourcePosition(0, 0), value_type, EnvironmentTypesIntoTypes[type(value)])
