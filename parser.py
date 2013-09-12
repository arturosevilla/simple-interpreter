from lexer import UnknownToken, TokenType

class UnknownVariable(Exception):

    def __init__(self, variable):
        self.variable = variable

    def __str__(self):
        return self.variable


class Expression(object):
    def eval(self, context):
        raise NotImplementedError()


class BinaryExpression(Expression):
    
    def __init__(self, left, right):
        self.left = left
        self.right = right


class SumOperation(BinaryExpression):

    def __init__(self, left, right):
        super(SumOperation, self).__init__(
            left,
            right
        )

    def eval(self, context):
        return self.left.eval(context) + self.right.eval(context)


class DifferenceOperation(BinaryExpression):

    def __init__(self, left, right):
        super(DifferenceOperation, self).__init__(
            left,
            right
        )

    def eval(self, ctx):
        return self.left.eval(ctx) - self.right.eval(ctx)


class ProductOperation(BinaryExpression):

    def __init__(self, left, right):
        super(ProductOperation, self).__init__(
            left,
            right
        )

    def eval(self, ctx):
        return self.left.eval(ctx) * self.right.eval(ctx)


class DivisionOperation(BinaryExpression):

    def __init__(self, dividend, divisor):
        super(DivisionOperation, self).__init__(
            dividend,
            divisor
        )

    def eval(self, ctx):
        return self.left.eval(ctx) / self.right.eval(ctx)


class ConstExpression(Expression):

    def __init__(self, number):
        self.number = number

    def eval(self, ctx):
        return self.number


class SymbolExpression(Expression):

    def __init__(self, variable):
        self.variable = variable

    def eval(self, context):
        if self.variable not in context:
            raise UnknownVariable(self.variable)
        return context[self.variable]


# term -> factor factor_rest
# factor -> num | (expr)
# factor_rest-> * num | / num
# factor_rest -> epsilon
# *expr -> term term_rest
# term_rest -> + term | - term
# term_rest -> epsilon
# num -> [0-9]+


class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self._fallback = None
        self.reset()

    def fallback(self, token):
        self._fallback = token

    def match(self, types, allow_empty=False):
        if not isinstance(types, list):
            types = [types]
        if self._fallback is not None:
            token = self._fallback
            self._fallback = None
        else:
            token = self.lexer.get_next_token()
        if token is None and allow_empty:
            return None
        elif token is None or token.type_ not in types:
            if token is None:
                token_type = '(empty)'
            else:
                token_type = token.type_
            self.fallback(token)
            raise UnknownToken(token_type)
        return token
    
    def parse(self):
        return self.expr()

    def expr(self):
        token = self.term()
        return self.term_rest(token)

    def term(self):
        token = self.factor()
        return self.factor_rest(token)

    def factor(self):
        token = self.match([
            TokenType.NUM,
            TokenType.OPEN_PARENS,
            TokenType.SYMBOL
        ])
        if token.type_ == TokenType.OPEN_PARENS:
            expr = self.expr()
            self.match(TokenType.CLOSING_PARENS)
            return expr
        if token.type_ == TokenType.SYMBOL:
            return SymbolExpression(token.lexeme)
        return ConstExpression(token.lexeme)

    def factor_rest(self, factor):
        try:
            token = self.match(TokenType.OP, True)
        except UnknownToken:
            token = None

        if token is None:
            return factor
        if token.lexeme == '*':
            return ProductOperation(
                factor,
                self.term()
            )
        elif token.lexeme == '/':
            return DifferenceOperation(
                factor,
                self.term()
            )

        else:
            self.fallback(token)
            return factor

    def term_rest(self, term):
        token = self.match(TokenType.OP, True)
        if token is None:
            return term
        if token.lexeme == '+':
            return SumOperation(
                term,
                self.term()
            )
        elif token.lexeme == '-':
            return DifferenceOperation(
                term,
                self.term()
            )
        else:
            raise ValueError('This should not happen!')

    def reset(self):
        self.lexer.reset()
    
    def eval(self, ctx):
        return self.parse().eval(ctx)

class Interpreter(object):

    def __init__(self, parser):
        self.parser = parser
        self.context = {
            'pi': 3.141592,
            'e': 2.7128,
            'g': 9.8
        }

    def reset(self):
        self.parser.reset()

    def eval(self):
        return self.parser.eval(self.context)

