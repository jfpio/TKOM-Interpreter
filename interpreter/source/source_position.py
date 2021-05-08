from dataclasses import dataclass


@dataclass(frozen=True)
class SourcePosition:
    line: int
    column: int
