#!/usr/bin/env python

from parser import Parser, AssignmentError
from lexer import Lexer
import sys
import math

class Interpreter(object):

    def __init__(self):
        self.context = {
            'pi': math.pi,
            'e': math.e,
            'g': 9.8
        }

    def eval(self, ast):
        return ast.eval(self.context)

    def eval_from_file(self, source):
        for line in source.readlines():
            ast = self.read_ast(line)
            if ast is None:
                continue
            self.eval(ast)

    def repl(self):
        exit = False
        while not exit:
            try:
                code = raw_input('>> ').strip()
                if len(code) == 0:
                    continue
                ast = self.read_ast(code)
                if ast is None:
                    continue
                print self.eval(ast)
            except EOFError:
                exit = True

    def read_ast(self, source):
        try:
            ast = Parser(Lexer(source)).compile_ast()
        except AssignmentError, e:
            print e
        else:
            return ast


if __name__ == '__main__':
    interpreter = Interpreter()
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1]) as source:
                interpreter.eval_from_file(source)
        except IOError:
            print 'Cannot read ', sys.argv[1]
    else:
        interpreter.repl()
        print ''

