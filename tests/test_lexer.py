import io

import pytest

from interpreter.lexer.lexer import Lexer, tokens_generator
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

    def test_get_float(self):
        token = self._get_first_token('111.1')
        assert token.type == TokenType.FLOAT_VALUE
        assert token.value == 111.1
        assert token.source_position == SourcePosition(1, 5)

    def test_get_currency(self):
        token = self._get_first_token('111.1USD')
        assert token.type == TokenType.CURRENCY_VALUE
        assert token.value == '111.1USD'
        assert token.source_position == SourcePosition(1, 8)

    def test_string(self):
        token = self._get_first_token('"abc"')
        assert token.type == TokenType.STRING_VALUE
        assert token.value == 'abc'
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


    @staticmethod
    def _get_first_token(string: str) -> Token:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)
        return lexer.get_next_token()


class TestManyTokens:
    def test_two_integers(self):
        tokens = list(self._get_tokens("111 222"))

        token_types = [token.type for token in tokens]

        assert token_types == [TokenType.INT_VALUE, TokenType.INT_VALUE, TokenType.EOF]

        assert tokens == [
            Token(TokenType.INT_VALUE, 111, SourcePosition(1, 3)),
            Token(TokenType.INT_VALUE, 222, SourcePosition(1, 7)),
            Token(TokenType.EOF, '', SourcePosition(2, 0)),
        ]

    @staticmethod
    def _get_tokens(string: str) -> [Token]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)

        return tokens_generator(lexer)
