import io
from typing import List

from interpreter.lexer.lexer import Lexer
from interpreter.models.declarations import Declaration
from interpreter.parser.parser import Parser
from interpreter.source.source import Source


class TestParserAcceptance:
    def test_acceptance_1(self):
        string = 'int main(){}'
        self.parse_program(string)

    def test_acceptance_2(self):
        string = 'int main(){a = a + 3;}'
        self.parse_program(string)

    def test_acceptance_3(self):
        string = \
            '''
            int a = 3;
            int main(){a = a + 3; return a;}
            '''
        self.parse_program(string)

    def test_acceptance_4(self):
        string = \
            '''
            int after_how_many_years_dollar_account_rise_to_value_in_pln(USD capital, float interest_rate, PLN value) {

                USD sum = capital;
                int counter = 0;

                while(capital > value) {
                    sum = sum * (1 + interest_rate);
                    counter = counter + 1;
                }

                return counter;
            }
            '''
        self.parse_program(string)

    def test_acceptance_5(self):
        string = \
            '''
            USD compound_interest(USD capital, float interest_rate, int number_of_times) {
                int i = number_of_times;
                USD sum = capital;

                while(i == 0) {
                    sum = sum * (1 + interest_rate);
                    i = i - 1;
                }
                return sum;
            }
            '''
        self.parse_program(string)

    def test_acceptance_6(self):
        string = \
            """
            int power(float basis, int exponent) {
                if (exponent == 0) {
                    return 1;
                }
                return basis * power(basis, exponent - 1);
            }
    
            USD compound_interest(USD capital, float interest_rate, int number_of_times) {
                return capital * power(1+interest_rate, number_of_times);
            }
            """
        self.parse_program(string)

    @staticmethod
    def parse_program(string: str) -> List[Declaration]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        parser = Parser(lexer)
        return parser.parse_program()
