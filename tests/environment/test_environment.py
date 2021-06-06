import io

import pytest

from interpreter.environment.environment import Environment
from interpreter.environment.semantic_errors import SemanticTypeError
from interpreter.environment.types import EnvironmentTypes
from interpreter.lexer.lexer import Lexer
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class TestEnvironment:
    def test_simple_main(self):
        string = 'int main(){return 3;}'
        result = self.get_result_of_main(string)
        assert result == 3

    def test_type_casting_int_1(self):
        string = 'int main(){return int 3.0;}'
        result = self.get_result_of_main(string)
        assert result == 3

    def test_type_casting_int_2(self):
        # string = 'int main(){return EUR 3.0;}'
        # result = self.get_result_of_main(string)
        # assert result == 3
        pass

    def test_negation_success(self):
        string = 'int main(){return !true;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_negation_fail(self):
        string = 'int main(){return !1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    @staticmethod
    def get_result_of_main(string) -> EnvironmentTypes:
        source = Source(io.StringIO(string))
        parser = Parser(Lexer(source))
        env = Environment(parser.parse_program())
        return env.run_main()
