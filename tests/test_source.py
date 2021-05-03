import io

from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition


class TestSource:
    def test_get_chars_from_string(self):
        string = "a\nbc\nc"
        source = Source(io.StringIO(string))

        char_list, position_list = self.get_char_and_positions_from_source(source)

        assert char_list == ['a', '\n', 'b', 'c', '\n', 'c', 'EOF']
        assert position_list == [
            SourcePosition(1, 1),
            SourcePosition(1, 2),
            SourcePosition(2, 1),
            SourcePosition(2, 2),
            SourcePosition(2, 3),
            SourcePosition(3, 1),
            SourcePosition(4, 0)
        ]

    def test_get_chars_from_file(self):
        with open('tests/data/test_source.curr', 'r') as file:
            source = Source(file)

            char_list, position_list = self.get_char_and_positions_from_source(source)

            assert char_list == ['a', ',', 'b', '\n', 'a', '\n', 'EOF']
            assert position_list == [
                SourcePosition(1, 1),
                SourcePosition(1, 2),
                SourcePosition(1, 3),
                SourcePosition(1, 4),
                SourcePosition(2, 1),
                SourcePosition(2, 2),
                SourcePosition(4, 0)
            ]

    @staticmethod
    def get_char_and_positions_from_source(source) -> ([], []):
        char_list = []
        position_list = []

        char = source.get_char()
        char_list.append(char)
        position_list.append(source.get_position())

        source.next_char()
        while char != 'EOF':
            char = source.get_char()
            position_list.append(source.get_position())
            char_list.append(char)

            source.next_char()

        return char_list, position_list
