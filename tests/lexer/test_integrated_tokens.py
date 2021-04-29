import io

import pytest

from interpreter.lexer.lexer import Lexer, tokens_generator
from interpreter.lexer.lexer_error import LexerError
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType


class TestIntegratedTokens:
    def test_two_integers(self):
        tokens = self._get_tokens("111 222")
        token_types = [token.type for token in tokens]

        assert token_types == [TokenType.INT_VALUE, TokenType.INT_VALUE, TokenType.EOF]

        assert tokens == [
            Token(TokenType.INT_VALUE, 111, SourcePosition(1, 3)),
            Token(TokenType.INT_VALUE, 222, SourcePosition(1, 7)),
            Token(TokenType.EOF, '', SourcePosition(2, 0)),
        ]

    def test_currency_assignment(self):
        tokens = self._get_tokens("USD := 3.92;")
        token_types = [token.type for token in tokens]
        assert token_types == [
            TokenType.CURRENCY,
            TokenType.CURRENCY_DECLARATION_OPERATOR,
            TokenType.FLOAT_VALUE,
            TokenType.SEMICOLON,
            TokenType.EOF
        ]

        token_values = [token.value for token in tokens]
        assert token_values == ["USD", '', 3.92, '', '']

    def test_currency_assignment_negative_1(self):
        with pytest.raises(LexerError):
            self._get_tokens("US := 3.92;")

    def test_currency_assignment_negative_2(self):
        with pytest.raises(LexerError):
            self._get_tokens("US := 3A92;")

    def test_currency_assignment_negative_3(self):
        with pytest.raises(LexerError):
            self._get_tokens("US : 3.92;")

    def test_sum(self):
        string = "sum = a + b; /*4.16USD*/"

        tokens = self._get_tokens(string)
        token_types = [token.type for token in tokens]
        assert token_types == [
            TokenType.ID,
            TokenType.ASSIGN_OPERATOR,
            TokenType.ID,
            TokenType.ADD_OPERATOR,
            TokenType.ID,
            TokenType.SEMICOLON,
            TokenType.EOF
        ]

        token_values = [token.value for token in tokens]
        assert token_values == ['sum', '', 'a', '', 'b', '', '']

    def test_function(self):
        string = """USD compound_interest(USD capital, float interest_rate) {
        return capital * power(1+interest_rate, number_of_times);
        }
        """
        tokens = self._get_tokens(string)
        token_types = [token.type for token in tokens]
        assert token_types == [
            TokenType.CURRENCY,
            TokenType.ID,
            TokenType.LEFT_BRACKET,
            TokenType.CURRENCY,
            TokenType.ID,
            TokenType.COMMA,
            TokenType.FLOAT,
            TokenType.ID,
            TokenType.RIGHT_BRACKET,
            TokenType.LEFT_CURLY_BRACKET,
            TokenType.RETURN_NAME,
            TokenType.ID,
            TokenType.MUL_OPERATOR,
            TokenType.ID,
            TokenType.LEFT_BRACKET,
            TokenType.INT_VALUE,
            TokenType.ADD_OPERATOR,
            TokenType.ID,
            TokenType.COMMA,
            TokenType.ID,
            TokenType.RIGHT_BRACKET,
            TokenType.SEMICOLON,
            TokenType.RIGHT_CURLY_BRACKET,
            TokenType.EOF
        ]

    @staticmethod
    def _get_tokens(string: str) -> [Token]:
        source = Source(io.StringIO(string))
        lexer = Lexer(source)

        return list(tokens_generator(lexer))
