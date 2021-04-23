from interpreter.source.source_position import SourcePosition


class LexerError(Exception):
    def __init__(self, message: str, source_position: SourcePosition):
        self.message = message
        self.position = source_position

    def __str__(self):
        return f"Lexer error with message: {self.message}" \
               f"in line: {self.position.line}\n" \
               f"column: {self.position.column}"
