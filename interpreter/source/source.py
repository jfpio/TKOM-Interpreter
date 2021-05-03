import io
import typing

from .source_position import SourcePosition


class Source:
    def __init__(self, source: typing.Union[io.TextIOBase, io.StringIO]):
        self.current_position = SourcePosition(1, 0)
        self.next_position = SourcePosition(1, 1)
        self.current_char = 'EOF'
        self.source = source
        self.next_char()

    def next_char(self):
        char = self.source.read(1)

        if not char:
            self.current_char = 'EOF'
            self.current_position = SourcePosition(self.next_position.line + 1, 0)

        elif char == '\n':
            self.current_char = char
            self.current_position = self.next_position
            self.next_position = self.current_position.next_line()

        else:
            self.current_char = char
            self.current_position = self.next_position
            self.next_position = self.current_position.advance()

    def get_char(self) -> str:
        return self.current_char

    def get_position(self) -> SourcePosition:
        return self.current_position
