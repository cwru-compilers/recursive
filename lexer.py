#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.

import sys, functools

TOKENSR = (
    'NUMBER', 'PLUS', 'DASH', 'STAR', 'SLASH', 'LPAREN', 'RPAREN',
)
TOKENS = dict((k, k) for i, k in enumerate(TOKENSR))
sys.modules[__name__].__dict__.update(TOKENS)

# This simple token class should be largely compatible with the one in PLY
# although I haven't tested that. I simply assume it is true...
class token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return str(self.value)
    def __eq__(self, b):
        if b is None: return False
        if not isinstance(b, token): return False
        return self.type == b.type and self.value == b.value

def Lex(inpt):
    digits = list()
    for x in inpt:
        if x.isdigit():
            digits.append(x)
        elif digits:
            yield token(NUMBER, int(''.join(digits)))
            digits = list()

        if x == ' ': continue
        elif x == '\n': continue
        elif x == '\t': continue
        elif x == '+': yield token(PLUS, x)
        elif x == '-': yield token(DASH, x)
        elif x == '*': yield token(STAR, x)
        elif x == '/': yield token(SLASH, x)
        elif x == '(': yield token(LPAREN, x)
        elif x == ')': yield token(RPAREN, x)
        elif not x.isdigit():
            raise Exception, 'Unknown character! "%s"' % (x)
    if digits:
        yield token(NUMBER, int(''.join(digits)))

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
##
## THIS HACKERY IS NOT ADVISED
##
## I wrote the following to emulate PLY lexer
## you should just use PLY's lexer instead.
##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def __input(inpt):
    Lex.c = Lex(inpt)

def __token():
    if not hasattr(Lex, 'c'): return
    try:
        return Lex.c.next()
    except StopIteration:
        return

Lex.input = __input
Lex.token = __token

