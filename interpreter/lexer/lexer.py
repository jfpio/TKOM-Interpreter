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

    def get_next_token(self) -> Token:
        self._skip_whitespace()

        token = self._build_one_of_number_value()
        if token:
            return token

        token = self._build_string()
        if token:
            return token

        token = self._build_operators()
        if token:
            return token

        token = self._build_one_char_tokens()
        if token:
            return token

        token = self._build_alpha_keywords_or_identifier()
        if token:
            return token

        if self._get_char() == 'EOF':
            return Token(TokenType.EOF, '', self._get_position())

        raise LexerError("Can't match any token", self._previous_position)

    def _get_char(self) -> str:
        return self._source.get_char()

    def _next_char(self):
        self._previous_position = self._get_position()
        self._source.next_char()

    def _get_position(self) -> SourcePosition:
        return self._source.get_position()

    def _build_alpha_keywords_or_identifier(self) -> Optional[Token]:
        keywords_dict = {
            'if': TokenType.IF_NAME,
            'else': TokenType.ELSE_NAME,
            'return': TokenType.RETURN_NAME,
            'while': TokenType.WHILE_NAME,
            'int': TokenType.INT,
            'float': TokenType.FLOAT_VALUE,
            'string': TokenType.STRING_VALUE,
            'bool': TokenType.BOOL_VALUE,
            'currency': TokenType.CURRENCY,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE
        }

        buffer = ''
        char = self._get_char()

        while char.isalpha() and char != 'EOF':
            buffer += char
            self._next_char()
            char = self._get_char()

        if buffer == '':
            return None
        elif buffer in keywords_dict:
            return Token(keywords_dict[buffer], '', self._previous_position)
        else:
            return Token(TokenType.ID, buffer, self._previous_position)

    def _build_one_char_tokens(self) -> Optional[Token]:
        non_conflict_one_line_operators = {
            "+": TokenType.ADD_OPERATOR,
            "-": TokenType.SUB_OPERATOR,
            "*": TokenType.MUL_OPERATOR,
            "%": TokenType.MODULO_OPERATOR,
            "(": TokenType.LEFT_BRACKET,
            ")": TokenType.RIGHT_BRACKET,
            "{": TokenType.LEFT_CURLY_BRACKET,
            "}": TokenType.RIGHT_CURLY_BRACKET,
            ";": TokenType.SEMICOLON
        }
        char = self._get_char()

        if char in non_conflict_one_line_operators:
            token = Token(non_conflict_one_line_operators[char], '', self._get_position())
            self._next_char()
            return token
        else:
            return None

    def _build_operators(self) -> Optional[Token]:
        char = self._get_char()

        if char == "/":
            self._next_char()
            char = self._get_char()
            if char == "*":
                self._skip_comment()
                self._next_char()
            else:
                token = Token(TokenType.DIV_OPERATOR, '', self._get_position())
                self._next_char()
                return token

        if char == ":":
            self._next_char()
            if self._get_char() == "=":
                token = Token(TokenType.CURRENCY_DECLARATION_OPERATOR, '', self._get_position())
                self._next_char()
                return token
            else:
                raise LexerError('Unknown operator ":"', self._get_position())

        token = self.build_one_char_token_or_two_char_token(
            ("!", TokenType.NEGATION_OPERATOR),
            ("!=", TokenType.NOT_EQUAL_OPERATOR)
        )
        if token:
            return token

        token = self.build_one_char_token_or_two_char_token(
            ("=", TokenType.ASSIGN_OPERATOR),
            ("==", TokenType.EQUAL_OPERATOR)
        )
        if token:
            return token

        token = self.build_one_char_token_or_two_char_token(
            ("<", TokenType.LESS_THAN_OPERATOR),
            ("<=", TokenType.LESS_THAN_OR_EQUAL_OPERATOR)
        )
        if token:
            return token

        token = self.build_one_char_token_or_two_char_token(
            (">", TokenType.GREATER_THAN_OPERATOR),
            (">=", TokenType.GREATER_THAN_OPERATOR_OR_EQUAL)
        )
        if token:
            return token

        return None

    def _build_string(self) -> Optional[Token]:
        string = ''

        char = self._get_char()
        if not char == '"':
            return None

        i = 0
        self._next_char()
        char = self._get_char()

        while char != '"':
            if i == MAX_STRING:
                raise LexerError(f"Too many char in string (above {MAX_STRING})", self._get_position())
            i += 1

            string += char
            self._next_char()
            char = self._get_char()

        token = Token(TokenType.STRING_VALUE, string, self._get_position())
        self._next_char()
        return token

    def _build_one_of_number_value(self) -> Optional[Token]:
        char = self._get_char()
        last_position = self._get_position()

        if not char.isdigit():
            return None

        base = 0
        i = 0
        while char.isdigit():
            if i == MAX_NUMBER_OF_DIGITS:
                raise LexerError(f"Too many digits in number (above {MAX_NUMBER_OF_DIGITS})", self._get_position())
            i += 1

            base = base * 10 + int(char)
            last_position = self._get_position()
            self._source.next_char()
            char = self._source.get_char()

        if char == '.':
            return self._build_float_or_currency(base)

        return Token(TokenType.INT_VALUE, base, last_position)

    def _build_float_or_currency(self, previous_base: int) -> Optional[Token]:
        base = float(previous_base)

        self._next_char()
        char = self._get_char()
        last_position = self._get_position()

        i = -1
        while char.isdigit():
            if i*(-1) == MAX_NUMBER_OF_DIGITS:
                raise LexerError(f"Too many digits in number (above {MAX_NUMBER_OF_DIGITS})", self._get_position())

            base = base + float(char) * 10**i
            last_position = self._get_position()
            self._source.next_char()
            char = self._source.get_char()
            i += -1

        if char.isupper() and char != 'EOF':
            return self._build_currency(base)

        return Token(TokenType.FLOAT_VALUE, base, last_position)

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
        i = 0
        while True:
            if i == MAX_STRING:
                raise LexerError(f"Too many char in comment (above {MAX_STRING})", self._get_position())
            i += 1

            if self._get_char() == "*":
                self._next_char()
                if self._get_char() == "/":
                    break

            self._next_char()

    def build_one_char_token_or_two_char_token(
            self,
            one_char_token: Tuple[str, TokenType],
            two_chars_token: Tuple[str, TokenType]
    ) -> Optional[Token]:
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


def tokens_generator(lexer):
    previous_token = Token(TokenType.INT_VALUE, 1, SourcePosition(0, 0))

    while previous_token.type != TokenType.EOF:
        new_token = lexer.get_next_token()
        previous_token = new_token
        yield new_token
