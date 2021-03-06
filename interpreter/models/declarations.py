from dataclasses import dataclass
from typing import List

from interpreter.models.base import Param, ParseTreeNode
from interpreter.models.constants import CustomTypeOfTypes
from interpreter.models.statements import Statements


@dataclass
class Declaration(ParseTreeNode):
    def accept(self, visitor: 'Environment', global_declaration: bool):
        pass


@dataclass
class FunctionDeclaration(Declaration):
    return_type: CustomTypeOfTypes
    id: str
    params: List[Param]
    statements: Statements

    def accept(self, visitor: 'Environment', global_declaration: bool):
        return visitor.visit_function_declaration(self)


@dataclass
class VariableDeclaration(Declaration):
    type: CustomTypeOfTypes
    id: str
    expression: 'Expression'

    def accept(self, visitor: 'Environment', global_declaration: bool = False):
        return visitor.visit_variable_declaration(self, global_declaration)


@dataclass
class CurrencyDeclaration(Declaration):
    name: str
    value: float

    def accept(self, visitor: 'Environment', global_declaration: bool):
        return visitor.visit_currency_declaration(self)


@dataclass
class ParseTree:
    declarations: List[Declaration]
