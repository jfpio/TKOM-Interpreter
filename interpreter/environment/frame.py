from typing import List, Dict

from interpreter.environment.environment_errors import SemanticError, SemanticErrorCode, SemanticTypeError
from interpreter.models.constants import PossibleTypes, CurrencyValue, CurrencyType
from interpreter.models.declarations import FunctionDeclaration
from interpreter.source.source_position import SourcePosition


class Frame:
    def __init__(self, function_declaration: FunctionDeclaration, source_position: SourcePosition,
                 params_values_list: List[PossibleTypes]):
        self.local_variables: Dict[str, PossibleTypes] = {}
        self.function_name = function_declaration.id
        self.return_value_type = function_declaration.return_type
        self.return_value = None

        if len(function_declaration.params) != len(params_values_list):
            raise SemanticError(source_position, SemanticErrorCode.WRONG_NUMBER_OF_PARAMS, function_declaration.id)

        for param, param_value in zip(function_declaration.params, params_values_list):
            if isinstance(param_value, CurrencyValue) and isinstance(param.type, CurrencyType):
                if param_value.name != param.type.name:
                    raise SemanticTypeError(source_position, param.type, type(param_value))
            elif param.type != type(param_value):
                raise SemanticTypeError(source_position, param.type, type(param_value))
            self.local_variables[param.id] = param_value

    def check_return_value(self, value: PossibleTypes, source_position: SourcePosition) -> bool:
        if isinstance(value, CurrencyValue) and isinstance(self.return_value_type, CurrencyType):
            if value.name != self.return_value_type.name:
                raise SemanticTypeError(source_position, self.return_value_type, value)
            self.return_value = value
            return True
        elif type(value) != self.return_value_type:
            raise SemanticTypeError(source_position, self.return_value_type, type(value))
        self.return_value = value
        return True
