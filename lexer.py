class UnknownToken(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class Token(object):

    def __init__(self, type_, lexeme=None):
        self.type_ = type_
        self.lexeme = lexeme


class TokenType(object):
    IF = 0
    SYMBOL = 1
    NUM = 2
    OP = 3
    OPEN_PARENS = 4
    CLOSE_PARENS = 5
    OPEN_BRACES = 6
    CLOSE_BRACES = 7


class Lexer(object):

    def __init__(self, program):
        self.program = program.strip()
        self.current = 0
        self.state = 1

    def next(self):
        if self.current >= len(self.program):
            return None
        ch = self.program[self.current]
        self.current += 1
        return ch

    def unread(self):
        if self.current > 0:
            self.current -= 1

    def isspace(self, ch):
        return ch in (' ', '\t', '\n')

    def isalpha_(self, ch):
        ch = ch.lower()
        if ord('a') <= ord(ch) <= ord('z'):
            return True
        return ch == '_'

    def isnum(self, ch):
        return ord('0') <= ord(ch) <= ord('9')

    def isalphanumeric_(self, ch):
        return self.isnum(ch) or self.isalpha_(ch)

    def handle_state1(self):
        ch = self.program[self.current - 1]
        if self.isnum(ch):
            self.state = 6
        elif ch in ('+', '-', '/', '*'):
            self.state = 9
        elif ch == '(':
            self.state = 10
        elif ch == ')':
            self.state = 11
        elif ch == '{':
            self.state = 12
        elif ch == '}':
            self.state = 13
        elif ch in ('<', '>', '='):
            self.state = 14
        elif ch == '!':
            self.state = 16
        elif not self.isalpha_(ch):
            self.state = 5
        elif ch == 'i':
            self.state = 2
        else:
            self.state = 4

    def handle_state2(self):
        ch = self.program[self.current - 1]
        if ch == 'f':
            self.state = 3
        elif self.isalpha_(ch) or self.isnum(ch):
            self.state = 4
        else:
            self.state = 5

    def handle_state6(self):
        ch = self.program[self.current - 1]
        if ch == '.':
            self.state = 7
        elif self.isnum(ch):
            self.state = 6
        else:
            self.state = 5

    def handle_state7(self):
        ch = self.program[self.current - 1]
        if self.isnum(ch):
            self.state = 8
        else:
            self.state = 5

    def handle_state8(self):
        ch = self.program[self.current - 1]
        if self.isnum(ch):
            self.state = 8
        else:
            self.state = 5

    def handle_state3(self):
        ch = self.program[self.current - 1]
        if self.isalphanumeric_(ch):
            self.state = 4
        else:
            self.state = 5

    def handle_state4(self):
        ch = self.program[self.current - 1]
        if self.isalphanumeric_(ch):
            self.state = 4
        else:
            self.state = 5

    def handle_state14(self):
        ch = self.program[self.current - 1]
        if ch == '=':
            self.state = 15
            return True
        return False

    def handle_state16(self):
        ch = self.program[self.current - 1]
        if ch == '=':
            self.state = 17
        else:
            self.state = 5

    def get_next_token(self):
        current = self.next()
        if current is None:
            return None
        while self.isspace(current):
            current = self.next()

        start = self.current - 1
        should_continue = True
        while should_continue:
            if self.state == 1:
                self.handle_state1()
            elif self.state == 2:
                self.handle_state2()
            elif self.state == 3:
                self.handle_state3()
            elif self.state == 4:
                self.handle_state4()
            elif self.state == 5:
                self.state = 1
                raise UnknownToken(
                    self.program[start:self.current]
                )
            elif self.state == 6:
                self.handle_state6()
            elif self.state == 7:
                self.handle_state7()
            elif self.state == 8:
                self.handle_state8()
            elif self.state == 14:
                if not self.handle_state14():
                    self.unread()
                    break
            elif self.state == 16:
                self.handle_state16()
           
            if self.state in (9, 10, 11, 12, 13, 15, 17):
                should_continue = False
            elif self.state != 5:
                ch = self.next()
                if ch is None or self.isspace(ch):
                    should_continue = False

        exit_state = self.state
        self.state = 1
        if exit_state == 3:
            return Token(TokenType.IF, 'if')
        elif exit_state == 6:
            return Token(
                TokenType.NUM,
                int(self.program[start:self.current].strip())
            )
        elif exit_state == 8:
            return Token(
                TokenType.NUM,
                float(self.program[start:self.current].strip())
            )
        elif exit_state in (9, 14, 15, 17):
            return Token(
                TokenType.OP,
                self.program[start:self.current].strip()
            )
        elif exit_state == 10:
            return Token(TokenType.OPEN_PARENS, '(')
        elif exit_state == 11:
            return Token(TokenType.CLOSE_PARENS, ')')
        elif exit_state == 12:
            return Token(TokenType.OPEN_BRACES, '{')
        elif exit_state == 13:
            return Token(TokenType.CLOSE_BRACES, '}')
        elif exit_state in (2, 4):
            return Token(
                TokenType.SYMBOL,
                self.program[start:self.current].strip()
            )
        else:
            raise UnknownToken(
                self.program[start:self.current]
            )

