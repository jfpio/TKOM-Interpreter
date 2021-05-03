from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePosition:
    line: int
    column: int

    def advance(self):
        return SourcePosition(self.line, self.column + 1)

    def next_line(self):
        return SourcePosition(self.line + 1, 1)
