#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

from betterast import Node

import lexer
from lexer import Lex

# Expr   -> Term Expr_
# Expr_  -> PLUS Term Expr_
#         | DASH Term Expr_
#         | e
# Term   -> Unary Term_
# Term_  -> STAR Unary Term_
#         | SLASH Unary Term_
#         | e
# Unary  -> DASH Factor
#         | Factor
# Factor -> NUMBER
#         | LPAREN Expr RPAREN

class parse(object):

    def __new__(cls, string):
        self = object.__new__(cls)
        self.init(string)
        return self.parse()

    def init(self, string):
        self.last_e = None
        self.tokens = [tok for tok in Lex(string)]

    def parse(self):
        i, obj = self.Expr(0)
        if i < len(self.tokens):
            raise SyntaxError, "Unconsumed Input %s:\nLast error: %s" % (
                str(self.tokens[i:]), self.last_e)
        return obj

    def collapse(self, subtree, extra):
        if extra is None:
            return subtree
        op, left = extra
        return Node(op).addkid(subtree).addkid(left)

    def Expr(self, i):
        # Expr   -> Term Expr_
        i, term = self.Term(i)
        i, expr_ = self.Expr_(i)
        return i, self.collapse(term, expr_)

    def Expr_(self, i):
        # Expr_  -> PLUS Term Expr_
        #         | DASH Term Expr_
        #         | e
        return self.alt(i, None, self.Expr_1, self.Expr_2, self.Expr_3)

    def Expr_1(self, i): 
        # Expr_  -> PLUS Term Expr_
        i, _ = self.consume(i, lexer.PLUS)
        i, term = self.Term(i)
        i, expr_ = self.Expr_(i)
        return i, ('+', self.collapse(term, expr_))

    def Expr_2(self, i):
        # Expr_  -> DASH Term Expr_
        i, _ = self.consume(i, lexer.DASH)
        i, term = self.Term(i)
        i, expr_ = self.Expr_(i)
        return i, ('-', self.collapse(term, expr_))

    def Expr_3(self, i):
        # Expr_  -> e
        return i, None

    def Term(self, i):
        # Term   -> Unary Term_
        i, unary = self.Unary(i)
        i, term_ = self.Term_(i)
        return i, self.collapse(unary, term_)

    def Term_(self, i):
        # Term_  -> STAR Unary Term_
        #         | SLASH Unary Term_
        #         | e
        return self.alt(i, None, self.Term_1, self.Term_2, self.Term_3)

    def Term_1(self, i): 
        # Term_  -> STAR Unary Term_
        i, _ = self.consume(i, lexer.STAR)
        i, unary = self.Unary(i)
        i, term_ = self.Term_(i)
        return i, ('*', self.collapse(unary, term_))

    def Term_2(self, i):
        # Term_  -> SLASH Unary Term_
        i, _ = self.consume(i, lexer.SLASH)
        i, unary = self.Unary(i)
        i, term_ = self.Term_(i)
        return i, ('/', self.collapse(unary, term_))

    def Term_3(self, i):
        # Term_  -> e
        return i, None

    def Unary(self, i):
        # Unary  -> DASH Factor
        #         | Factor
        return self.alt(
            i,
            [lexer.DASH, lexer.NUMBER, lexer.LPAREN],
            self.Unary1, self.Unary2
        )

    def Unary1(self, i):
        # Unary  -> DASH Factor
        i, _ = self.consume(i, lexer.DASH)
        i, node = self.Factor(i)
        return i, Node("Neg").addkid(node)

    def Unary2(self, i):
        # Unary  -> Factor
        return self.Factor(i)

    def Factor(self, i):
        # Factor -> NUMBER
        #         | LPAREN Expr RPAREN
        return self.alt(
            i,
            [lexer.NUMBER, lexer.LPAREN],
            self.Factor1, self.Factor2,
        )

    def Factor1(self, i):
        # Factor -> NUMBER
        i, tok = self.consume(i, lexer.NUMBER)
        return i, Node(tok.value)

    def Factor2(self, i):
        # Factor -> LPAREN Expr RPAREN
        i, _ = self.consume(i, lexer.LPAREN)
        i, node = self.Expr(i)
        i, _ = self.consume(i, lexer.RPAREN)
        return i, node

    def alt(self, i, expected, *alternatives):
        for alternative in alternatives:
            try:
                return alternative(i)
            except SyntaxError, e:
                self.last_e = e
                pass
        if self.tokens[i].type in expected:
            raise self.last_e
        raise SyntaxError, "Expected one of %s but got %s" % (
            str(expected), self.tokens[i].type)

    def consume(self, i, toktype):
        if i >= len(self.tokens):
            raise SyntaxError, \
              "Ran off the end of the input but expected %s" % toktype
        tok = self.tokens[i]
        if tok.type == toktype:
            return i+1, tok
        raise SyntaxError, "Expected %s but got %s" % (toktype, tok.type)


