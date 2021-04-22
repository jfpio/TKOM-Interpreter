import io
import typing

from .source_position import SourcePosition


class Source:
    def __init__(self, source: typing.Union[io.TextIOBase, io.StringIO]):
        self.current_position = SourcePosition(0, 1)
        self.current_char = 'EOF'
        self.current_line = ''
        self.source = source

        self.next_char()

    def next_char(self):
        if len(self.current_line) != 0:
            head, *tail = self.current_line
            self.current_char = head
            self.current_line = tail
            self.current_position = SourcePosition(self.current_position.line, self.current_position.column + 1)

        else:
            self.current_line = self.source.readline()
            self.current_position = SourcePosition(self.current_position.line + 1, 0)

            if self.current_line != "":
                head, *tail = self.current_line
                self.current_char = head
                self.current_line = tail
                self.current_position = SourcePosition(self.current_position.line, 1)
            else:
                self.current_char = 'EOF'

    def get_char(self) -> str:
        return self.current_char

    def get_position(self) -> SourcePosition:
        return self.current_position
