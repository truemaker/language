from constants import *
from errors import *
# TOKENS
TT_INT          = 'INT'
TT_FLOAT        = 'FLOAT'
TT_STRING       = 'STRING'
TT_PLUS         = 'PLUS'
TT_MINUS        = 'MINUS'
TT_MUL          = 'MUL'
TT_DIV          = 'DIV'
TT_POW          = 'POW'
TT_MODULO       = 'MODULO'
TT_LPAREN       = 'LPAREN'
TT_RPAREN       = 'RPAREN'
TT_LSQUARE      = 'LSQUARE'
TT_RSQUARE      = 'RSQUARE'
TT_KEYWORD      = 'KEYWORD'
TT_IDENTIFIER   = 'IDENTIFIER'
TT_EQUALS       = 'EQUALS'
TT_EE           = 'EE'
TT_NE           = 'NE'
TT_LT           = 'LT'
TT_GT           = 'GT'
TT_LTE          = 'LTE'
TT_GTE          = 'GTE'
TT_COMMA        = 'COMMA'
TT_ARROW        = 'ARROW'
TT_NEWLINE      = 'NEWLINE'
TT_PREPROCESS   = 'PREPROCESS'
TT_EOF          = 'EOF'

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'
    def matches(self, type_, value = None):
        return self.type == type_ and self.value == value

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

class Lexer:
        def __init__(self, fn, text):
                self.fn = fn
                self.text = text
                self.pos = Position(-1, 0, -1, fn, text)
                self.current_char = None
                self.advance()
        
        def advance(self):
                self.pos.advance(self.current_char)
                self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

        def make_tokens(self):
                tokens = []

                while self.current_char != None:
                        if self.current_char in ' \t':
                                self.advance()
                        elif self.current_char == '#':
                            self.skip_comment()
                        elif self.current_char in ';\n':
                            tokens.append(Token(TT_NEWLINE, pos_start=self.pos.copy()))
                            self.advance()
                        elif self.current_char in DIGITS:
                                tokens.append(self.make_number())
                        elif self.current_char in LETTERS:
                            tokens.append(self.make_identifier())
                        elif self.current_char == '"':
                            tokens.append(self.make_string())
                        elif self.current_char == '+':
                                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == '-':
                                tokens.append(self.make_minus())
                                self.advance()
                        elif self.current_char == '*':
                                tokens.append(Token(TT_MUL, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == '/':
                                tokens.append(Token(TT_DIV, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == '(':
                                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == ')':
                                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == '[':
                                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == ']':
                                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                                self.advance()
                        elif self.current_char == '^':
                            tokens.append(Token(TT_POW, pos_start=self.pos))
                            self.advance()
                        elif self.current_char == '%':
                            tokens.append(Token(TT_MODULO, pos_start=self.pos))
                            self.advance()
                        elif self.current_char == '=':
                            tokens.append(self.make_equals()) # Token(TT_EQUALS, pos_start=self.pos))
                        elif self.current_char == '>':
                            tokens.append(self.make_greater_than())
                        elif self.current_char == '<':
                            tokens.append(self.make_less_than())
                        elif self.current_char == '!':
                            tok, error = self.make_not_equals()
                            if error: return [], error
                            tokens.append(tok)
                        elif self.current_char == ',':
                            tokens.append(Token(TT_COMMA, pos_start=self.pos))
                            self.advance()
                        else:
                                pos_start = self.pos.copy()
                                char = self.current_char
                                self.advance()
                                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

                tokens.append(Token(TT_EOF, pos_start=self.pos))
                return tokens, None

        def make_identifier(self):
            identifier = ''
            pos_start = self.pos.copy()

            while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
                identifier += self.current_char
                self.advance()
            if identifier in KEYWORDS:
                tok_type = TT_KEYWORD
            elif identifier in PREPROCESSING_DIRECTIVES:
                tok_type = TT_PREPROCESS
            else:
                tok_type = TT_IDENTIFIER
            return Token(tok_type, identifier, pos_start,self.pos)
        def make_minus(self):
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '>':
                return Token(TT_ARROW, pos_start=pos_start, pos_end=self.pos)
            return Token(TT_MINUS, pos_start=pos_start)
        def make_not_equals(self):
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TT_NE, pos_start, self.pos.copy()), None
            else:
                return None, UnexpectedCharError(pos_start, self.pos.copy(),"Expected '='")
        def make_number(self):
                num_str = ''
                dot_count = 0
                pos_start = self.pos.copy()

                while self.current_char != None and self.current_char in DIGITS + '.':
                        if self.current_char == '.':
                                if dot_count == 1: break
                                dot_count += 1
                                num_str += '.'
                        else:
                                num_str += self.current_char
                        self.advance()

                if dot_count == 0:
                        return Token(TT_INT, int(num_str), pos_start, self.pos)
                else:
                        return Token(TT_FLOAT, float(num_str), pos_start, self.pos)
        def make_equals(self):
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TT_EE, pos_start, self.pos.copy())
            else:
                return Token(TT_EQUALS, pos_start, self.pos.copy())
        def make_greater_than(self):
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TT_GTE, pos_start, self.pos.copy())
            else:
                return Token(TT_GT, pos_start, self.pos.copy())
        def make_less_than(self):
            pos_start = self.pos.copy()
            self.advance()
            if self.current_char == '=':
                self.advance()
                return Token(TT_LTE, pos_start, self.pos.copy())
            else:
                return Token(TT_LT, pos_start, self.pos.copy())
        def make_string(self):
            string = ''
            pos_start = self.pos.copy()
            escape_character = False
            self.advance()
            escape_character = {
                "n":"\n",
                "t":"\t"
            }
            while self.current_char != None and (self.current_char != '"' or escape_character):
                if escape_character:
                    string += escape_character.get(self.current_char, self.current_char)
                else:
                    if self.current_char == '\\':
                        escape_character = True
                    else:
                        string += self.current_char
                self.advance()
                escape_character = False
            self.advance()
            return Token(TT_STRING, string, pos_start, self.pos.copy())
        def skip_comment(self):
            while self.current_char != "\n":
                self.advance()
            self.advance()