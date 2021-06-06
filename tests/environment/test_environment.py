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

    def test_if_statement(self):
        string = """
        int main(){
            if(true || false) {
                return 1;
            }
            return 0;
        }"""
        result = self.get_result_of_main(string)
        assert result == 1

    def test_nested_if_statement(self):
        string = """
        int main(){
            if(true || false) {
                if(true && true) {
                    return 1;
                }
            }
            return 0;
        }"""
        result = self.get_result_of_main(string)
        assert result == 1

    def test_or_expression_1(self):
        string = 'int main(){return true || true;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_or_expression_2(self):
        string = 'int main(){return false || false;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_or_expression_3(self):
        string = 'int main(){return 1 || 1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_and_expression_1(self):
        string = 'int main(){return true && true;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_and_expression_2(self):
        string = 'int main(){return true && false;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_and_expression_3(self):
        string = 'int main(){return 1 && 1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_relationship_expression_1(self):
        string = 'int main(){return 3.0 > 2.0;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_relationship_expression_2(self):
        string = 'int main(){return 3.0 > 2;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

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
