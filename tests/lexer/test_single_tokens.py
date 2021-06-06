import io

import pytest

from interpreter.lexer.lexer import Lexer
from interpreter.lexer.lexer_error import LexerError
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestSingleTokens:
    def test_get_EOF(self):
        token = self._get_first_token('')
        assert token.type == TokenType.EOF

    def test_get_int(self):
        token = self._get_first_token('111')
        assert token.type == TokenType.INT_VALUE
        assert token.value == 111
        assert token.source_position == SourcePosition(1, 3)

    def test_get_extreme_big_int(self):
        big_int_string = ''.join('1' for _ in range(10000))
        with pytest.raises(LexerError):
            self._get_first_token(big_int_string)

    def test_unterminated_string(self):
        with pytest.raises(LexerError, match=r"Can't match any token"):
            self._get_first_token('"abc')

    def test_get_float_1(self):
        token = self._get_first_token('111.1')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 111.1
        assert token.source_position == SourcePosition(1, 5)

    def test_get_float_2(self):
        token = self._get_first_token('0.1')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 0.1
        assert token.source_position == SourcePosition(1, 3)

    def test_float_no_fraction_part(self):
        # float = int, '.' , DIGIT, {DIGIT};
        with pytest.raises(LexerError, match=r"No digit after dot in float"):
            self._get_first_token('4.')

    def test_string(self):
        token = self._get_first_token('"abc"')
        assert token.type == TokenType.STRING_VALUE
        assert token.value == 'abc'
        assert token.source_position == SourcePosition(1, 5)

    def test_true_value(self):
        token = self._get_first_token('true')
        assert token.type == TokenType.BOOL_VALUE
        assert token.value is True
        assert token.source_position == SourcePosition(1, 4)

    def test_false_value(self):
        token = self._get_first_token('false')
        assert token.type == TokenType.BOOL_VALUE
        assert token.value is False
        assert token.source_position == SourcePosition(1, 5)

    def test_get_extreme_big_string(self):
        big_string = ''.join('i' for _ in range(10000))
        with pytest.raises(LexerError):
            self._get_first_token('"' + big_string)

    def test_comment(self):
        token = self._get_first_token('/* aaa*/')
        assert token.type == TokenType.EOF

    def test_equal_operator(self):
        token = self._get_first_token(' == ')
        assert token.type == TokenType.EQUAL_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_assign_operator(self):
        token = self._get_first_token(' = ')
        assert token.type == TokenType.ASSIGN_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_divide_operator(self):
        token = self._get_first_token(' /a ')
        assert token.type == TokenType.DIV_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_and_operator(self):
        token = self._get_first_token(' && ')
        assert token.type == TokenType.AND_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_or_operator(self):
        token = self._get_first_token(' || ')
        assert token.type == TokenType.OR_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_add_operator(self):
        token = self._get_first_token(' + ')
        assert token.type == TokenType.ADD_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_sub_operator(self):
        token = self._get_first_token(' - ')
        assert token.type == TokenType.SUB_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_mul_operator(self):
        token = self._get_first_token(' * ')
        assert token.type == TokenType.MUL_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_div_operator(self):
        token = self._get_first_token(' / ')
        assert token.type == TokenType.DIV_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_modulo_operator(self):
        token = self._get_first_token(' % ')
        assert token.type == TokenType.MODULO_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_negation_operator(self):
        token = self._get_first_token(' ! ')
        assert token.type == TokenType.NEGATION_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_not_equal_operator(self):
        token = self._get_first_token(' != ')
        assert token.type == TokenType.NOT_EQUAL_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_less_than_operator(self):
        token = self._get_first_token(' < ')
        assert token.type == TokenType.LESS_THAN_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_greater_than_operator(self):
        token = self._get_first_token(' > ')
        assert token.type == TokenType.GREATER_THAN_OPERATOR
        assert token.source_position == SourcePosition(1, 2)

    def test_less_than_or_equal_operator(self):
        token = self._get_first_token(' <= ')
        assert token.type == TokenType.LESS_THAN_OR_EQUAL_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_greater_than_or_equal_operator(self):
        token = self._get_first_token(' >= ')
        assert token.type == TokenType.GREATER_THAN_OPERATOR_OR_EQUAL
        assert token.source_position == SourcePosition(1, 3)

    def test_currency_declaration(self):
        token = self._get_first_token(' := ')
        assert token.type == TokenType.CURRENCY_DECLARATION_OPERATOR
        assert token.source_position == SourcePosition(1, 3)

    def test_currency_declaration_error(self):
        with pytest.raises(LexerError):
            self._get_first_token(' : ')

    def test_if_keyword(self):
        token = self._get_first_token(' if a b ')
        assert token.type == TokenType.IF_NAME

    def test_while_keyword(self):
        token = self._get_first_token(' while a b ')
        assert token.type == TokenType.WHILE_NAME
        assert token.source_position == SourcePosition(1, 6)

    def test_id(self):
        token = self._get_first_token(' alfa ')
        assert token.type == TokenType.ID
        assert token.value == 'alfa'
        assert token.source_position == SourcePosition(1, 5)

    def test_currency_name(self):
        token = self._get_first_token(' USD ')
        assert token.type == TokenType.CURRENCY
        assert token.value == 'USD'
        assert token.source_position == SourcePosition(1, 4)

    def test_int_keyword(self):
        token = self._get_first_token(' int ')
        assert token.type == TokenType.INT
        assert token.source_position == SourcePosition(1, 4)

    def test_float_keyword(self):
        token = self._get_first_token(' float ')
        assert token.type == TokenType.FLOAT
        assert token.source_position == SourcePosition(1, 6)

    def test_string_keyword(self):
        token = self._get_first_token(' string ')
        assert token.type == TokenType.STRING
        assert token.source_position == SourcePosition(1, 7)

    def test_bool_keyword(self):
        token = self._get_first_token(' bool ')
        assert token.type == TokenType.BOOL
        assert token.source_position == SourcePosition(1, 5)

    def test_currency_keyword(self):
        token = self._get_first_token(' currency ')
        assert token.type == TokenType.CURRENCY
        assert token.source_position == SourcePosition(1, 9)

    def test_left_bracket(self):
        token = self._get_first_token('(')
        assert token.type == TokenType.LEFT_BRACKET
        assert token.source_position == SourcePosition(1, 1)

    def test_right_bracket(self):
        token = self._get_first_token(')')
        assert token.type == TokenType.RIGHT_BRACKET
        assert token.source_position == SourcePosition(1, 1)

    def test_comma_bracket(self):
        token = self._get_first_token(',')
        assert token.type == TokenType.COMMA
        assert token.source_position == SourcePosition(1, 1)

    def test_left_curly_bracket(self):
        token = self._get_first_token('{')
        assert token.type == TokenType.LEFT_CURLY_BRACKET
        assert token.source_position == SourcePosition(1, 1)

    def test_right_curly_bracket(self):
        token = self._get_first_token('}')
        assert token.type == TokenType.RIGHT_CURLY_BRACKET
        assert token.source_position == SourcePosition(1, 1)

    def test_semicolon(self):
        token = self._get_first_token(';')
        assert token.type == TokenType.SEMICOLON
        assert token.source_position == SourcePosition(1, 1)

    def test_if(self):
        token = self._get_first_token('if')
        assert token.type == TokenType.IF_NAME
        assert token.source_position == SourcePosition(1, 2)

    def test_else(self):
        token = self._get_first_token('else')
        assert token.type == TokenType.ELSE_NAME
        assert token.source_position == SourcePosition(1, 4)

    def test_return(self):
        token = self._get_first_token('return')
        assert token.type == TokenType.RETURN_NAME
        assert token.source_position == SourcePosition(1, 6)

    @staticmethod
    def _get_first_token(string: str) -> Token:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return lexer.get_next_token()
