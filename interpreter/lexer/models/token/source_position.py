from dataclasses import dataclass


@dataclass
class SourcePosition:
    line: int
    column: int
