import math
from typing import Tuple, Optional

from interpreter.lexer.lexer_error import LexerError
from interpreter.source.source import Source
from interpreter.source.source_position import SourcePosition
from interpreter.token.token import Token
from interpreter.token.token_type import TokenType

MAX_STRING = 1000
MAX_NUMBER_OF_DIGITS = 100


class Lexer:
    def __init__(self, source: Source):
        self._source = source
        self._previous_position = SourcePosition(0, 0)

    non_conflict_one_line_operators = {
        "+": TokenType.ADD_OPERATOR,
        "-": TokenType.SUB_OPERATOR,
        "*": TokenType.MUL_OPERATOR,
        "%": TokenType.MODULO_OPERATOR,
        "(": TokenType.LEFT_BRACKET,
        ")": TokenType.RIGHT_BRACKET,
        "{": TokenType.LEFT_CURLY_BRACKET,
        "}": TokenType.RIGHT_CURLY_BRACKET,
        ";": TokenType.SEMICOLON,
        ",": TokenType.COMMA
    }

    keywords_dict = {
        'if': TokenType.IF_NAME,
        'else': TokenType.ELSE_NAME,
        'return': TokenType.RETURN_NAME,
        'while': TokenType.WHILE_NAME,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'string': TokenType.STRING,
        'void': TokenType.VOID,
        'bool': TokenType.BOOL,
        'currency': TokenType.CURRENCY,
        'true': TokenType.BOOL_VALUE,
        'false': TokenType.BOOL_VALUE
    }

    def get_next_token(self) -> Token:
        self._skip_whitespace()
        token = \
            self._skip_comment_or_build_div_operator() \
            or self._build_eof() \
            or self._build_one_of_number_value() \
            or self._build_string() \
            or self._build_operators() \
            or self._build_one_char_tokens() \
            or self._build_alpha_keywords_or_identifier() \
            or self._build_currency_type_name()

        if token:
            return token

        raise LexerError("Can't match any token", self._previous_position)

    def _get_char(self) -> str:
        return self._source.get_char()

    def _next_char(self):
        self._previous_position = self._get_position()
        self._source.next_char()

    def _get_position(self) -> SourcePosition:
        return self._source.get_position()

    def _skip_comment_or_build_div_operator(self) -> Optional[Token]:
        char = self._get_char()

        if char == "/":
            self._next_char()
            char = self._get_char()
            if char == "*":
                self._skip_comment()
                self._next_char()
            else:
                token = Token(TokenType.DIV_OPERATOR, '', self._previous_position)
                self._next_char()
                return token

        return None

    def _build_eof(self) -> Optional[Token]:
        if self._get_char() == 'EOF':
            return Token(TokenType.EOF, '', self._get_position())
        return None

    def _build_alpha_keywords_or_identifier(self) -> Optional[Token]:
        buffer = ''
        char = self._get_char()

        i = 0
        while char.isalpha() and char.islower() or char == '_':
            if i == MAX_STRING:
                raise LexerError("Too many chars in ID", self._get_position())
            i += 1
            buffer += char
            self._next_char()
            char = self._get_char()

        if buffer == '':
            return None
        elif buffer in self.keywords_dict:
            if buffer in ['true', 'false']:
                if buffer == 'true':
                    return Token(TokenType.BOOL_VALUE, True, self._previous_position)
                else:
                    return Token(TokenType.BOOL_VALUE, False, self._previous_position)
            return Token(self.keywords_dict[buffer], '', self._previous_position)
        else:
            return Token(TokenType.ID, buffer, self._previous_position)

    def _build_currency_type_name(self) -> Optional[Token]:
        buffer = ''
        char = self._get_char()

        if not char.isupper():
            return None

        for i in range(3):
            buffer += char
            self._next_char()
            char = self._get_char()

        if len([char for char in buffer if char.isupper()]) == 3:
            return Token(TokenType.CURRENCY, buffer, self._previous_position)
        return None

    def _build_one_char_tokens(self) -> Optional[Token]:
        char = self._get_char()

        if char in self.non_conflict_one_line_operators:
            token = Token(self.non_conflict_one_line_operators[char], '', self._get_position())
            self._next_char()
            return token
        return None

    def _build_operators(self) -> Optional[Token]:
        token = \
            self.build_two_char_operators('&&', TokenType.AND_OPERATOR) \
            or self.build_two_char_operators('||', TokenType.OR_OPERATOR) \
            or self.build_two_char_operators(':=', TokenType.CURRENCY_DECLARATION_OPERATOR) \
            or self.build_one_char_token_or_two_char_token(
                ("!", TokenType.NEGATION_OPERATOR),
                ("!=", TokenType.NOT_EQUAL_OPERATOR)
            ) or self.build_one_char_token_or_two_char_token(
                ("=", TokenType.ASSIGN_OPERATOR),
                ("==", TokenType.EQUAL_OPERATOR)
            ) or self.build_one_char_token_or_two_char_token(
                ("<", TokenType.LESS_THAN_OPERATOR),
                ("<=", TokenType.LESS_THAN_OR_EQUAL_OPERATOR)
            ) or self.build_one_char_token_or_two_char_token(
                (">", TokenType.GREATER_THAN_OPERATOR),
                (">=", TokenType.GREATER_THAN_OPERATOR_OR_EQUAL)
            )
        if token:
            return token
        return None

    def _build_string(self) -> Optional[Token]:
        string = ''

        char = self._get_char()
        if char != '"':
            return None

        i = 0
        self._next_char()
        char = self._get_char()

        while char != '"':
            if i == MAX_STRING:
                raise LexerError(f"Too many char in string (above {MAX_STRING})", self._get_position())
            if char == 'EOF':
                raise LexerError("Can't match any token, unterminated string", self._get_position())
            i += 1

            string += char
            self._next_char()
            char = self._get_char()

        token = Token(TokenType.STRING_VALUE, string, self._get_position())
        self._next_char()
        return token

    def _build_one_of_number_value(self) -> Optional[Token]:
        if not self._get_char().isdigit():
            return None

        base = self.build_integer_part_of_the_number()

        if self._get_char() == '.':
            return self._build_float(base)
        return Token(TokenType.INT_VALUE, base, self._previous_position)

    def _build_float(self, integer_part: int) -> Optional[Token]:
        self._next_char()
        if not self._get_char().isdigit():
            raise LexerError(f"No digit after dot in float", self._get_position())

        fractional_part = self.build_integer_part_of_the_number()
        digits = int(math.log10(fractional_part)) + 1
        number = float(integer_part) + fractional_part * 10 ** -digits
        return Token(TokenType.FLOAT_VALUE, number, self._previous_position)

    def _build_currency(self, previous_base: float) -> Optional[Token]:
        number = previous_base
        currency_name = ''

        for i in range(3):
            if self._get_char().isupper() and self._get_char() != 'EOF':
                currency_name += self._get_char()
                self._next_char()

            else:
                return None
        return Token(TokenType.CURRENCY_VALUE, f"{number}{currency_name}", self._previous_position)

    def _skip_whitespace(self):
        char = self._get_char()
        while char.isspace():
            self._next_char()
            char = self._get_char()

    def _skip_comment(self):
        while True:
            if self._get_char() == "*":
                self._next_char()
                if self._get_char() == "/":
                    break

            self._next_char()

    def build_one_char_token_or_two_char_token(self,
                                               one_char_token: Tuple[str, TokenType],
                                               two_chars_token: Tuple[str, TokenType]) -> Optional[Token]:
        one_char_token_value, one_char_token_type = one_char_token
        two_chars_token_value, two_chars_token_type = two_chars_token

        if self._get_char() != one_char_token_value:
            return None

        self._next_char()
        if self._get_char() == two_chars_token_value[1]:
            token = Token(two_chars_token_type, '', self._get_position())
            self._next_char()
            return token
        else:
            return Token(one_char_token_type, '', self._previous_position)

    def build_two_char_operators(self, token_value: str, token_type: TokenType) -> Optional[Token]:
        if self._get_char() != token_value[0]:
            return None

        self._next_char()
        if self._get_char() == token_value[1]:
            token = Token(token_type, '', self._get_position())
            self._next_char()
            return token

        return None

    def build_integer_part_of_the_number(self) -> int:
        char = self._get_char()
        base = 0
        i = 0
        while char.isdigit():
            if i == MAX_NUMBER_OF_DIGITS:
                raise LexerError(f"Too many digits in number (above {MAX_NUMBER_OF_DIGITS})", self._get_position())
            i += 1

            base = base * 10 + int(char)
            self._next_char()
            char = self._get_char()
        return base


def tokens_generator(lexer):
    while (new_token := lexer.get_next_token()).type != TokenType.EOF:
        yield new_token
    yield new_token
