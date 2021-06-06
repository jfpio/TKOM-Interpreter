from functools import reduce
from typing import Union, Optional, Dict, List

from interpreter.environment.frame import Frame
from interpreter.models.base import Constant
from interpreter.models.constants import RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION, \
    ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION, PossibleTypes, CustomTypeTypes, CurrencyType, CurrencyValue
from interpreter.models.declarations import ParseTree, VariableDeclaration, CurrencyDeclaration, FunctionDeclaration
from interpreter.models.expressions import Expression, AndExpression, RelationshipExpression, MultiplyExpression, \
    SumExpression, TypeCastingFactor, NegationFactor
from interpreter.environment.environment_errors import SemanticError, SemanticErrorCode, SemanticTypeError, \
    RunTimeEnvError, RuntimeErrorCode
from interpreter.models.statements import ReturnStatement, IfStatement, Statements, WhileStatement
from interpreter.source.source_position import SourcePosition


class Environment:
    def __init__(self, parse_tree: ParseTree):
        self.global_variables: Dict[str, VariableDeclaration] = {}
        self.functions_declarations: Dict[str, FunctionDeclaration] = {}
        self.currency_declarations: Dict[str, CurrencyDeclaration] = {}
        self.frames_stack: List[Frame] = []

        for declaration in parse_tree.declarations:
            declaration.accept(self, True)

        self.current_frame = Frame(
            self.functions_declarations['main'],
            SourcePosition(0, 0),
            []
        )

    def run_main(self) -> Optional[PossibleTypes]:
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
            return_value = statement.accept(self)
            if return_value is not None:
                return return_value
        return None

    def visit_if_statement(self, if_statement: IfStatement):
        condition = if_statement.expression.accept(self)
        self.check_type(bool, condition, if_statement.expression.source_position)
        if condition:
            return if_statement.statements.accept(self)

    def visit_while_statement(self, while_statement: WhileStatement):
        condition = while_statement.expression.accept(self)
        self.check_type(bool, condition, while_statement.expression.source_position)
        i = 0

        while condition:
            return_value = while_statement.statements.accept(self)
            if return_value:
                return return_value
            if i == 100:
                raise RunTimeEnvError(while_statement.source_position,
                                      RuntimeErrorCode.INFINITE_LOOP,
                                      self.current_frame.function_name)

            condition = while_statement.expression.accept(self)
            i += 1

    def visit_return_statement(self, return_statement: ReturnStatement):
        return_value = None
        if return_statement.expression:
            return_value = return_statement.expression.accept(self)

        self.current_frame.check_return_value(return_value, return_statement.source_position)
        return return_value

    def visit_expression(self, expression: Expression) -> Optional[PossibleTypes]:
        if len(expression.and_expressions) == 1:
            and_expression = expression.and_expressions[0]
            return and_expression.accept(self)

        and_expressions = []
        for exp in expression.and_expressions:
            exp_result = exp.accept(self)
            self.check_type(bool, exp_result, exp.source_position)
            and_expressions.append(exp_result)
        return reduce(lambda acc, x: acc or x, and_expressions)

    def visit_and_expression(self, expression: AndExpression) -> Optional[PossibleTypes]:
        if len(expression.relationship_expressions) == 1:
            relationship_expression = expression.relationship_expressions[0]
            return relationship_expression.accept(self)

        relationship_expressions = []
        for exp in expression.relationship_expressions:
            exp_result = exp.accept(self)
            self.check_type(bool, exp_result, exp.source_position)
            relationship_expressions.append(exp_result)
        return reduce(lambda acc, x: acc and x, relationship_expressions)

    def visit_relationship_expression(self, expression: RelationshipExpression) -> Optional[PossibleTypes]:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side = expression.left_side.accept(self)
        right_side = expression.right_side.accept(self)

        left_side_type = type(left_side)
        self.check_type(left_side_type, right_side, expression.right_side.source_position)
        operator = expression.operator
        relationship_function = RELATIONSHIP_OPERAND_INTO_LAMBDA_EXPRESSION[operator]
        return relationship_function(left_side, right_side)

    def visit_arithmetic_expression(self, expression: Union[SumExpression, MultiplyExpression]) \
            -> Optional[PossibleTypes]:
        if expression.right_side is None:
            return expression.left_side.accept(self)

        left_side_type = type(expression.left_side)
        right_side = []
        for operator, expression in expression.right_side:
            expression_result = expression.accept(self)
            self.check_type(left_side_type, expression_result, expression.source_position)
            right_side.append((operator, expression_result))

        accumulator = expression.left_side.accept(self)
        for operator, arithmetic_expression in right_side:
            evaluate_function = ARITHMETIC_OPERATOR_INTO_LAMBDA_EXPRESSION[operator]
            accumulator = evaluate_function(accumulator, arithmetic_expression)
        return accumulator

    def visit_type_casting_factor(self, factor: TypeCastingFactor) -> Optional[PossibleTypes]:
        if not factor.cast_type:
            return factor.negation_factor.accept(self)

        return self.cast(factor.cast_type, factor.negation_factor.accept(self), factor.source_position)

    def visit_negation_factor(self, negation_factor: NegationFactor):
        if negation_factor.is_negated:
            value = negation_factor.factor.accept(self)
            self.check_type(bool, value, negation_factor.source_position)
            return not value
        return negation_factor.factor.accept(self)

    def visit_factor(self, constant: Constant) -> Optional[PossibleTypes]:
        return constant.value

    def cast(self, casting_type: CustomTypeTypes, value: PossibleTypes, source_position: SourcePosition) \
            -> PossibleTypes:
        if casting_type is CurrencyType:
            if type(value) is float:
                return CurrencyValue(casting_type.name, float(value))
            elif type(value) is CurrencyType and casting_type is CurrencyType:
                to_cast_currency = self.get_currency_declaration(casting_type.name, source_position)
                casting_currency = self.get_currency_declaration(value.name, source_position)
                new_value = casting_currency.value / to_cast_currency.value
                return CurrencyValue(to_cast_currency.name, new_value)
            else:
                SemanticTypeError(source_position, float, value)
        else:
            return casting_type(value)

    def get_function_declaration(self, name: str, source_position: SourcePosition):
        if name in self.functions_declarations:
            return self.functions_declarations[name]
        raise SemanticError(source_position, SemanticErrorCode.FUN_ID_NOT_FOUND, name)

    def get_variable_declaration(self, name: str, source_position: SourcePosition):
        if name in self.current_frame.local_variables:
            return self.current_frame.local_variables[name]
        elif name in self.global_variables:
            return self.global_variables[name]
        raise SemanticError(source_position, SemanticErrorCode.VAR_ID_NOT_FOUND, name)

    def get_currency_declaration(self, name: str, source_position: SourcePosition):
        if name in self.currency_declarations:
            return self.currency_declarations[name]
        raise SemanticError(source_position, SemanticErrorCode.CURR_ID_NOT_FOUND, name)

    @staticmethod
    def check_type(value_type: CustomTypeTypes, value, source_position: SourcePosition) -> bool:
        if type(value) == value_type:
            return True
        else:
            raise SemanticTypeError(source_position, value_type, type(value))
