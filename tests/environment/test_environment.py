import io

import pytest

from interpreter.environment.environment import Environment
from interpreter.environment.environment_errors import SemanticTypeError, RunTimeEnvError
from interpreter.lexer.lexer import Lexer
from interpreter.models.constants import PossibleTypes, CurrencyValue
from interpreter.parser.parser import Parser
from interpreter.parser.parser_error import ParserError
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

    def test_while_statement_1(self):
        string = """
        int main(){
            while(true) {
                    return 1;
            }
            return 0;
        }"""
        result = self.get_result_of_main(string)
        assert result == 1

    def test_while_statement_2(self):
        string = """
        int main(){
            while(true) {
            }
        }"""
        with pytest.raises(RunTimeEnvError):
            self.get_result_of_main(string)

    # def test_while_statement_3(self):
    #     string = """
    #     int main(){
    #         while(false) {
    #         }
    #     }"""
    #     with pytest.raises(RunTimeEnvError):
    #         self.get_result_of_main(string)

    def test_or_expression_1(self):
        string = 'bool main(){return true || true;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_or_expression_2(self):
        string = 'bool main(){return false || false;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_or_expression_3(self):
        string = 'bool main(){return 1 || 1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_and_expression_1(self):
        string = 'bool main(){return true && true;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_and_expression_2(self):
        string = 'bool main(){return true && false;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_and_expression_3(self):
        string = 'bool main(){return 1 && 1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_relationship_expression_1(self):
        string = 'bool main(){return 3.0 > 2.0;}'
        result = self.get_result_of_main(string)
        assert result == True

    def test_relationship_expression_2(self):
        string = 'bool main(){return 3.0 > 2;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_type_casting_1(self):
        string = 'int main(){return int 3.0;}'
        result = self.get_result_of_main(string)
        assert result == 3

    def test_type_casting_2(self):
        string = """
        EUR := 2.0;
        
        EUR main(){return EUR 3.0;}
        """
        result = self.get_result_of_main(string)
        assert result == CurrencyValue('EUR', 3.0)

    def test_type_casting_3(self):
        string = """
        EUR := 2.0;
        USD := 1.0;

        EUR main(){
        return 3.0USD;
        }
        """
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_type_casting_4(self):
        string = """
        EUR := 2.0;
        USD := 1.0;

        EUR main(){
        return EUR 1.0USD;
        }
        """
        result = self.get_result_of_main(string)
        assert result == CurrencyValue('EUR', 0.5)

    def test_arithmetic_order(self):
        string = """
        int main(){
            return 2 + 2 * 2;
        }
        """
        result = self.get_result_of_main(string)
        assert result == 6

    def test_strings(self):
        string = """
        string main(){
            string a = "aa";
            string b = "bb";
            return a + b;
        }
        """
        result = self.get_result_of_main(string)
        assert result == "aabb"

    def test_negation_success(self):
        string = 'bool main(){return !true;}'
        result = self.get_result_of_main(string)
        assert result == False

    def test_negation_fail(self):
        string = 'bool main(){return !1;}'
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_global_variable(self):
        string = """
        int a = 3;
        int main(){return a;}
        """
        result = self.get_result_of_main(string)
        assert result == 3

    def test_function_call_1(self):
        string = """
        int a(){return 3;}
        int main(){return a();}
        """
        result = self.get_result_of_main(string)
        assert result == 3

    def test_function_call_2(self):
        string = """
        int a(int b){return 3;}
        int main(){return a(2);}
        """
        result = self.get_result_of_main(string)
        assert result == 3

    def test_function_call_3(self):
        string = """
        int a(bool b){return 3;}
        int main(){return a(2);}
        """
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_function_call_4(self):
        string = """
        bool a(int b){return 3;}
        int main(){return a(2);}
        """
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_function_call_5(self):
        string = """
        int a(){return a();}
        int main(){return a();}
        """
        with pytest.raises(RunTimeEnvError):
            self.get_result_of_main(string)

    def test_function_call_6(self):
        string = """
        bool a(int b){return 3;}
        int main(){return a(2);}
        """
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_assignment_1(self):
        string = """
        int main(){
        int a = 3;
        return a;
        }
        """
        result = self.get_result_of_main(string)
        assert result == 3

    def test_assignment_2(self):
        string = """
        int main(){
        int a = 3;
        return a;
        }
        """
        result = self.get_result_of_main(string)
        assert result == 3

    def test_assignment_3(self):
        string = """
        int main(){
        int a = 3.0;
        return a;
        }
        """
        with pytest.raises(SemanticTypeError):
            self.get_result_of_main(string)

    def test_assignment_4(self):
        string = """
        int main(){
        int a == 3.0;
        return a;
        }
        """
        with pytest.raises(ParserError):
            self.get_result_of_main(string)

    def test_recursion(self):
        string = \
            """
            USD := 3.0;
            float power(float basis, int exponent) {
                if (exponent == 0) {
                    return 1.0;
                }
                return basis * power(basis, exponent - 1);
            }
    
            USD compound_interest(USD capital, float interest_rate, int number_of_times) {
                return capital * power(1.0 + interest_rate, number_of_times);
            }
            
            USD main(){
            return compound_interest(10USD, 0.1, 5); 
            }
            """
        result = self.get_result_of_main(string)
        result = CurrencyValue(result.name, round(result.value, 4))
        assert result == CurrencyValue('USD', 16.1051)

    def test_while_loop(self):
        string = \
            """
            USD := 3.0;
            USD compound_interest(USD capital, float interest_rate, int number_of_times) {
                int i = number_of_times;
                USD sum = capital;
            
                while(i != 0) {
                    sum = sum * (1 + interest_rate);
                    i = i - 1;       
                }
                return sum;
            }
            USD main(){
            return compound_interest(10USD, 0.1, 5); 
            }
            """
        result = self.get_result_of_main(string)
        result = CurrencyValue(result.name, round(result.value, 4))
        assert result == CurrencyValue('USD', 16.1051)

    @staticmethod
    def get_result_of_main(string) -> PossibleTypes:
        source = Source(io.StringIO(string))
        parser = Parser(Lexer(source))
        env = Environment(parser.parse_program())
        return env.run_main()
