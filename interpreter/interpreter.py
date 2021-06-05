from interpreter.models.declarations import ParseTree


class Interpreter:
    def __init__(self, parse_tree: ParseTree):
        self.parse_tree = parse_tree
        self.global_variables = self.get_global_variables(parse_tree)
        self.functions_def = self.get_functions_def(parse_tree)
