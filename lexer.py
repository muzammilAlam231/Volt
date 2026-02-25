"""
Volt Language v2.0 - Lexer (Tokenizer)
Converts raw source code into a stream of tokens.
Supports string interpolation, new keywords for OOP/modules/etc.
"""


class TokenType:
    # Literals
    NUMBER        = 'NUMBER'
    STRING        = 'STRING'
    INTERP_STRING = 'INTERP_STRING'
    TRUE          = 'TRUE'
    FALSE         = 'FALSE'
    NULL          = 'NULL'

    # Identifiers & Keywords
    IDENTIFIER = 'IDENTIFIER'
    SET        = 'SET'
    SHOW       = 'SHOW'
    ASK        = 'ASK'
    IF         = 'IF'
    ELIF       = 'ELIF'
    ELSE       = 'ELSE'
    WHILE      = 'WHILE'
    LOOP       = 'LOOP'
    FOR        = 'FOR'
    IN         = 'IN'
    TO         = 'TO'
    FUNC       = 'FUNC'
    RETURN     = 'RETURN'
    BREAK      = 'BREAK'
    CONTINUE   = 'CONTINUE'
    AND        = 'AND'
    OR         = 'OR'
    NOT        = 'NOT'
    PUSH       = 'PUSH'
    POP        = 'POP'

    # OOP keywords
    CLASS      = 'CLASS'
    NEW        = 'NEW'
    THIS       = 'THIS'
    SUPER      = 'SUPER'
    EXTENDS    = 'EXTENDS'

    # Match / Switch
    MATCH      = 'MATCH'
    CASE       = 'CASE'
    DEFAULT    = 'DEFAULT'

    # Error handling
    TRY        = 'TRY'
    CATCH      = 'CATCH'
    FINALLY    = 'FINALLY'
    THROW      = 'THROW'

    # Import
    USE        = 'USE'

    # Operators
    PLUS       = 'PLUS'
    MINUS      = 'MINUS'
    STAR       = 'STAR'
    SLASH      = 'SLASH'
    PERCENT    = 'PERCENT'
    ASSIGN     = 'ASSIGN'
    EQ         = 'EQ'
    NEQ        = 'NEQ'
    LT         = 'LT'
    GT         = 'GT'
    LTE        = 'LTE'
    GTE        = 'GTE'
    ARROW      = 'ARROW'
    FAT_ARROW  = 'FAT_ARROW'
    DOT        = 'DOT'

    # Delimiters
    LPAREN     = 'LPAREN'
    RPAREN     = 'RPAREN'
    LBRACE     = 'LBRACE'
    RBRACE     = 'RBRACE'
    LBRACKET   = 'LBRACKET'
    RBRACKET   = 'RBRACKET'
    COMMA      = 'COMMA'
    COLON      = 'COLON'

    # Special
    NEWLINE    = 'NEWLINE'
    EOF        = 'EOF'


class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:{self.column})"


KEYWORDS = {
    'set':      TokenType.SET,
    'show':     TokenType.SHOW,
    'ask':      TokenType.ASK,
    'if':       TokenType.IF,
    'else':     TokenType.ELSE,
    'while':    TokenType.WHILE,
    'for':      TokenType.FOR,
    'in':       TokenType.IN,
    'to':       TokenType.TO,
    'func':     TokenType.FUNC,
    'return':   TokenType.RETURN,
    'break':    TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'and':      TokenType.AND,
    'or':       TokenType.OR,
    'not':      TokenType.NOT,
    'true':     TokenType.TRUE,
    'false':    TokenType.FALSE,
    'null':     TokenType.NULL,
    'push':     TokenType.PUSH,
    'pop':      TokenType.POP,
    'class':    TokenType.CLASS,
    'new':      TokenType.NEW,
    'this':     TokenType.THIS,
    'super':    TokenType.SUPER,
    'extends':  TokenType.EXTENDS,
    'match':    TokenType.MATCH,
    'case':     TokenType.CASE,
    'default':  TokenType.DEFAULT,
    'try':      TokenType.TRY,
    'catch':    TokenType.CATCH,
    'finally':  TokenType.FINALLY,
    'throw':    TokenType.THROW,
    'use':      TokenType.USE,
}


class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer Error at line {line}, col {column}: {message}")


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, message):
        raise LexerError(message, self.line, self.column)

    def peek(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return '\0'

    def peek_ahead(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return '\0'

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def add_token(self, type, value):
        self.tokens.append(Token(type, value, self.line, self.column))

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.peek() in (' ', '\t', '\r'):
            self.advance()

    def skip_comment(self):
        if self.peek() == '-' and self.peek_ahead() == '-':
            while self.pos < len(self.source) and self.peek() != '\n':
                self.advance()

    def read_string(self, quote_char, interpolate=False):
        """Read a string literal. f-strings (f"...") support {expr} interpolation."""
        self.advance()  # consume opening quote
        parts = []
        current_text = []
        has_interpolation = False

        while self.pos < len(self.source) and self.peek() != quote_char:
            ch = self.peek()

            # Escape sequences
            if ch == '\\':
                self.advance()
                if self.pos >= len(self.source):
                    self.error("Unterminated string literal")
                esc = self.advance()
                escape_map = {'n': '\n', 't': '\t', '\\': '\\', '"': '"',
                              "'": "'", '{': '{', '}': '}', '0': '\0'}
                current_text.append(escape_map.get(esc, '\\' + esc))

            # Interpolation (only in f-strings)
            elif ch == '{' and interpolate:
                has_interpolation = True
                # Save current text segment
                text_so_far = ''.join(current_text)
                if text_so_far:
                    parts.append(('text', text_so_far))
                current_text = []

                self.advance()  # consume {
                # Read expression text until matching }
                expr_text = self._read_interpolation_expr()
                parts.append(('expr', expr_text))

            elif ch == '\n':
                self.error("Unterminated string literal")
            else:
                current_text.append(self.advance())

        if self.pos >= len(self.source):
            self.error("Unterminated string literal")

        self.advance()  # consume closing quote

        # If no interpolation, just return a regular string
        text_so_far = ''.join(current_text)
        if not has_interpolation:
            return ('string', text_so_far)

        # Add remaining text
        if text_so_far:
            parts.append(('text', text_so_far))

        return ('interp', parts)

    def _read_interpolation_expr(self):
        """Read expression text inside { } in an interpolated string."""
        depth = 1
        result = []
        while self.pos < len(self.source) and depth > 0:
            ch = self.peek()
            if ch == '{':
                depth += 1
                result.append(self.advance())
            elif ch == '}':
                depth -= 1
                if depth > 0:
                    result.append(self.advance())
                else:
                    self.advance()  # consume closing }
            elif ch == '"' or ch == "'":
                # Read nested string literal
                q = self.advance()
                result.append(q)
                while self.pos < len(self.source) and self.peek() != q:
                    if self.peek() == '\\':
                        result.append(self.advance())
                    result.append(self.advance())
                if self.pos < len(self.source):
                    result.append(self.advance())
            else:
                result.append(self.advance())
        return ''.join(result)

    def read_number(self):
        result = []
        has_dot = False
        while self.pos < len(self.source) and (self.peek().isdigit() or self.peek() == '.'):
            if self.peek() == '.':
                # Check if next char after dot is a digit (avoid 5.method())
                if not self.peek_ahead().isdigit():
                    break
                if has_dot:
                    break
                has_dot = True
            result.append(self.advance())
        num_str = ''.join(result)
        return float(num_str) if has_dot else int(num_str)

    def read_identifier(self):
        result = []
        while self.pos < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
            result.append(self.advance())
        return ''.join(result)

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            if self.pos >= len(self.source):
                break

            ch = self.peek()

            # Comments
            if ch == '-' and self.peek_ahead() == '-':
                self.skip_comment()
                continue

            # Newlines
            if ch == '\n':
                self.add_token(TokenType.NEWLINE, '\\n')
                self.advance()
                continue

            # Strings
            if ch in ('"', "'"):
                result = self.read_string(ch)
                if result[0] == 'string':
                    self.add_token(TokenType.STRING, result[1])
                else:
                    self.add_token(TokenType.INTERP_STRING, result[1])
                continue

            # Numbers
            if ch.isdigit():
                value = self.read_number()
                self.add_token(TokenType.NUMBER, value)
                continue

            # Identifiers & Keywords
            if ch.isalpha() or ch == '_':
                # Check for f-string: f"..." or f'...'
                if ch == 'f' and self.peek_ahead() in ('"', "'"):
                    self.advance()  # consume 'f'
                    quote = self.peek()
                    result = self.read_string(quote, interpolate=True)
                    if result[0] == 'string':
                        self.add_token(TokenType.STRING, result[1])
                    else:
                        self.add_token(TokenType.INTERP_STRING, result[1])
                    continue

                value = self.read_identifier()
                token_type = KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)
                if token_type == TokenType.TRUE:
                    self.add_token(TokenType.TRUE, True)
                elif token_type == TokenType.FALSE:
                    self.add_token(TokenType.FALSE, False)
                elif token_type == TokenType.NULL:
                    self.add_token(TokenType.NULL, None)
                else:
                    self.add_token(token_type, value)
                continue

            # Multi-character operators
            two = ch + self.peek_ahead()
            if two == '==':
                self.add_token(TokenType.EQ, '=='); self.advance(); self.advance(); continue
            if two == '!=':
                self.add_token(TokenType.NEQ, '!='); self.advance(); self.advance(); continue
            if ch == '!' and self.peek_ahead() != '=':
                self.add_token(TokenType.NOT, '!'); self.advance(); continue
            if two == '<=':
                self.add_token(TokenType.LTE, '<='); self.advance(); self.advance(); continue
            if two == '>=':
                self.add_token(TokenType.GTE, '>='); self.advance(); self.advance(); continue
            if two == '->':
                self.add_token(TokenType.ARROW, '->'); self.advance(); self.advance(); continue
            if two == '=>':
                self.add_token(TokenType.FAT_ARROW, '=>'); self.advance(); self.advance(); continue

            # Single-character operators & delimiters
            single_map = {
                '+': TokenType.PLUS,    '-': TokenType.MINUS,
                '*': TokenType.STAR,    '/': TokenType.SLASH,
                '%': TokenType.PERCENT, '=': TokenType.ASSIGN,
                '<': TokenType.LT,      '>': TokenType.GT,
                '(': TokenType.LPAREN,  ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,  '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,']': TokenType.RBRACKET,
                ',': TokenType.COMMA,   ':': TokenType.COLON,
                '.': TokenType.DOT,
            }

            if ch in single_map:
                self.add_token(single_map[ch], ch)
                self.advance()
                continue

            self.error(f"Unexpected character: {ch!r}")

        self.add_token(TokenType.EOF, None)
        return self.tokens
