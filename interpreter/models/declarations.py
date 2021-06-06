from dataclasses import dataclass
from typing import List, Optional

from interpreter.models.base import Param, ParseTreeNode
from interpreter.models.constants import Types
from interpreter.models.statements import Statements


@dataclass
class Declaration(ParseTreeNode):
    pass


@dataclass
class FunctionDeclaration(Declaration):
    return_type: Types
    id: str
    params: List[Param]
    statements: Statements

    def accept(self, visitor: 'Environment'):
        return visitor.visit_function_call(self)


@dataclass
class VariableDeclaration(Declaration):
    type: Types
    id: str
    expression: Optional['Expression']

    def accept(self, visitor: 'Environment', global_declaration: bool):
        return visitor.visit_variable_declaration(self, global_declaration)


@dataclass
class CurrencyDeclaration(Declaration):
    name: str
    value: float

    def accept(self, visitor: 'Environment'):
        return visitor.visit_currency_declaration(self)


@dataclass
class ParseTree:
    declarations: List[Declaration]
