from abc import ABC


class Node(ABC):
    pass


class Statement(ABC):
    pass


class CurrencyDeclaration(Statement):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class FunctionDeclaration(Statement):
    def __init__(self, id, params, block):
        self.id = id
        self.params = params
        self.block = block
