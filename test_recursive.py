#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tim.tadh@hackthology.com
#For licensing see the LICENSE file in the top level directory.


import itertools

from nose.tools import eq_ as eq, ok_ as ok, raises
from betterast import Node

import lexer
from recursive import parse
from lexer import token


def new_parser():
    return object.__new__(parse)

def test_mk_test_instance():
    parser = new_parser()
    assert isinstance(parser, parse)

def test_init():
    parser = new_parser()
    parser.init("2 + 3 / 4")
    assert isinstance(parser.tokens, list)
    expected = [
        token(lexer.NUMBER, 2),
        token(lexer.PLUS, '+'),
        token(lexer.NUMBER, 3),
        token(lexer.SLASH, '/'),
        token(lexer.NUMBER, 4),
    ]
    eq(len(parser.tokens), len(expected))
    for a, b in itertools.izip(parser.tokens, expected):
        eq(a, b)

def test_Factor_parse_number():
    parser = new_parser()
    parser.init("2")
    i, node = parser.Factor(0)
    eq(i, 1)
    eq(node.label, 2)

def test_consume_pos():
    parser = new_parser()
    parser.init("(2 + 3) / 4")
    i, tok = parser.consume(0, lexer.LPAREN)
    eq(i, 1)
    eq(tok.type, lexer.LPAREN)

@raises(SyntaxError)
def test_consume_neg():
    parser = new_parser()
    parser.init("(2 + 3) / 4")
    parser.consume(0, lexer.NUMBER)

def test_alt_pos():
    parser = new_parser()
    parser.init("(2 + 3) / 4")
    def one(i):
        return parser.consume(i, lexer.NUMBER)
    def two(i):
        return parser.consume(i, lexer.LPAREN)
    i, tok = parser.alt(0, [lexer.NUMBER, lexer.LPAREN], one, two)
    eq(i, 1)
    eq(tok.type, lexer.LPAREN)

@raises(SyntaxError)
def test_alt_neg():
    parser = new_parser()
    parser.init("(2 + 3) / 4")
    def one(i):
        return parser.consume(i, lexer.NUMBER)
    def two(i):
        return parser.consume(i, lexer.PLUS)
    parser.alt(0, [lexer.NUMBER, lexer.LPAREN], one, two)

def test_Factor1():
    parser = new_parser()
    parser.init("(2 + 3) / 4")
    i, node = parser.Factor1(1)
    eq(i, 2)
    eq(node.label, 2)
    eq(len(node.children), 0)

def test_Factor2():
    parser = new_parser()
    parser.init("(2)")
    i, node = parser.Factor2(0)
    eq(i, 3)
    eq(node.label, 2)
    eq(len(node.children), 0)

def test_Unary1():
    parser = new_parser()
    parser.init("-2")
    i, node = parser.Unary1(0)
    eq(i, 2)
    eq(node.label, "Neg")
    eq(len(node.children), 1)
    eq(node.children[0].label, 2)

def test_Unary2():
    parser = new_parser()
    parser.init("2")
    i, node = parser.Unary2(0)
    eq(i, 1)
    eq(node.label, 2)

def test_Unary_1():
    parser = new_parser()
    parser.init("-2")
    i, node = parser.Unary(0)
    eq(i, 2)
    eq(node.label, "Neg")
    eq(len(node.children), 1)
    eq(node.children[0].label, 2)

def test_Unary_2():
    parser = new_parser()
    parser.init("2")
    i, node = parser.Unary(0)
    eq(i, 1)
    eq(node.label, 2)

def test_collapse_None():
    parser = new_parser()
    eq(parser.collapse(Node(1), None), Node(1))

def test_collapse_subtree():
    parser = new_parser()
    eq(
      parser.collapse(Node(1), ("*", Node(2))),
      Node("*").addkid(Node(1)).addkid(Node(2))
    )

@raises(ValueError)
def test_collapse_bad_subtree():
    parser = new_parser()
    parser.collapse(Node(1), Node("*"))

def test_1_Term():
    parser = new_parser()
    parser.init("1 * 2")
    i, node = parser.Term(0)
    eq(i, 3)
    eq(node, Node("*").addkid(Node(1)).addkid(Node(2)))

def test_2_Term():
    parser = new_parser()
    parser.init("1 / 2")
    i, node = parser.Term(0)
    eq(i, 3)
    eq(node, Node("/").addkid(Node(1)).addkid(Node(2)))

def test_3_Term():
    parser = new_parser()
    parser.init("1 / 2 * 3")
    i, node = parser.Term(0)
    eq(i, 5)
    eq(node, Node("/")
              .addkid(Node(1))
              .addkid(
                Node("*")
                  .addkid(Node(2))
                  .addkid(Node(3))
              )
    )

def test_4_Term():
    parser = new_parser()
    parser.init("(1 / 2) * 3")
    i, node = parser.Term(0)
    eq(i, 7)
    eq(node, Node("*")
              .addkid(
                Node("/")
                  .addkid(Node(1))
                  .addkid(Node(2))
              )
              .addkid(Node(3))
    )

def test_1_Term_():
    parser = new_parser()
    parser.init("* 2")
    i, (op, right) = parser.Term_(0)
    eq(i, 2)
    eq(op, "*")
    eq(right.label, 2)

def test_Term_1():
    parser = new_parser()
    parser.init("* 2")
    i, (op, right) = parser.Term_1(0)
    eq(i, 2)
    eq(op, "*")
    eq(right.label, 2)

@raises(SyntaxError)
def test_Term_1_bad():
    parser = new_parser()
    parser.init("2 * 2")
    i, node = parser.Term_1(0)

def test_2_Term_():
    parser = new_parser()
    parser.init("/ 2")
    i, (op, right) = parser.Term_(0)
    eq(i, 2)
    eq(op, "/")
    eq(right.label, 2)

def test_Term_2():
    parser = new_parser()
    parser.init("/ 2")
    i, (op, right) = parser.Term_2(0)
    eq(i, 2)
    eq(op, "/")
    eq(right.label, 2)

@raises(SyntaxError)
def test_Term_2_bad():
    parser = new_parser()
    parser.init("2 / 2")
    i, node = parser.Term_2(0)

def test_3_Term_():
    parser = new_parser()
    parser.init("+ 2")
    i, n = parser.Term_(0)
    eq(n, None)

def test_Term_3():
    parser = new_parser()
    parser.init("+ / - *")
    i, n = parser.Term_3(0)
    eq(i, 0)
    eq(n, None)

def test_2_level_Term_():
    parser = new_parser()
    parser.init("* 2 * 3")
    i, (op, right) = parser.Term_(0)
    eq(op, "*")
    eq(right.label, "*")
    eq(len(right.children), 2)
    eq(right.children[0].label, 2)
    eq(right.children[1].label, 3)

def test_2_level_Term():
    parser = new_parser()
    parser.init("1 / 2 * 3")
    i, node = parser.Term(0)
    eq(node.label, "/")
    eq(len(node.children), 2)
    eq(node.children[0].label, 1)
    eq(node.children[1].label, "*")
    eq(len(node.children[1].children), 2)
    eq(node.children[1].children[0].label, 2)
    eq(node.children[1].children[1].label, 3)

def test_2_level_Expr_Term():
    parser = new_parser()
    parser.init("1 / 2 * 3")
    i, node = parser.Expr(0)
    eq(node.label, "/")
    eq(len(node.children), 2)
    eq(node.children[0].label, 1)
    eq(node.children[1].label, "*")
    eq(len(node.children[1].children), 2)
    eq(node.children[1].children[0].label, 2)
    eq(node.children[1].children[1].label, 3)

def test_1_Expr_():
    parser = new_parser()
    parser.init("+ 2")
    i, (op, right) = parser.Expr_(0)
    eq(i, 2)
    eq(op, "+")
    eq(right.label, 2)

def test_Expr_1():
    parser = new_parser()
    parser.init("+ 2")
    i, (op, right) = parser.Expr_1(0)
    eq(i, 2)
    eq(op, "+")
    eq(right.label, 2)

def test_2_Expr_():
    parser = new_parser()
    parser.init("- 2")
    i, (op, right) = parser.Expr_(0)
    eq(i, 2)
    eq(op, "-")
    eq(right.label, 2)

def test_Expr_2():
    parser = new_parser()
    parser.init("- 2")
    i, (op, right) = parser.Expr_2(0)
    eq(i, 2)
    eq(op, "-")
    eq(right.label, 2)

def test_3_Expr_():
    parser = new_parser()
    parser.init("2 2")
    i, n = parser.Expr_(0)
    eq(i, 0)
    eq(n, None)

def test_Expr_3():
    parser = new_parser()
    parser.init("2 2")
    i, n = parser.Expr_3(0)
    eq(i, 0)
    eq(n, None)

def test_Expr_Factor():
    parser = new_parser()
    parser.init("3")
    i, node = parser.Expr(0)
    eq(node.label, 3)

def test_Expr_Factor2():
    parser = new_parser()
    parser.init("(3)")
    i, node = parser.Expr(0)
    eq(i, 3)
    eq(node.label, 3)

def test_Expr_Unary_Factor():
    parser = new_parser()
    parser.init("-3")
    i, node = parser.Expr(0)
    eq(i, 2)
    eq(node, Node("Neg").addkid(Node(3)))

def test_Expr_Term_Unary():
    parser = new_parser()
    parser.init("1*-3")
    i, node = parser.Expr(0)
    eq(i, 4)
    eq(node,
       Node("*")
         .addkid(Node(1))
         .addkid(Node("Neg").addkid(Node(3)))
    )

def test_Expr_Expr_Unary():
    parser = new_parser()
    parser.init("1--3")
    i, node = parser.Expr(0)
    eq(i, 4)
    eq(node,
       Node("-")
         .addkid(Node(1))
         .addkid(Node("Neg").addkid(Node(3)))
    )

def test_Expr_Unary_Expr_Unary():
    parser = new_parser()
    parser.init("-1--3")
    i, node = parser.Expr(0)
    eq(i, 5)
    eq(node,
       Node("-")
         .addkid(Node("Neg").addkid(Node(1)))
         .addkid(Node("Neg").addkid(Node(3)))
    )

def test_precidence_mul():
    parser = new_parser()
    parser.init("1*3+4")
    i, node = parser.Expr(0)
    eq(node,
       Node("+")
        .addkid(
          Node("*").addkid(Node(1)).addkid(Node(3)))
        .addkid(Node(4))
    )

def test_precidence_mul2():
    parser = new_parser()
    parser.init("4+1*3")
    i, node = parser.Expr(0)
    eq(node,
       Node("+")
        .addkid(Node(4))
        .addkid(
          Node("*").addkid(Node(1)).addkid(Node(3)))
    )

def test_precidence_mul3():
    parser = new_parser()
    parser.init("1*(3+4)")
    i, node = parser.Expr(0)
    eq(node,
       Node("*")
        .addkid(Node(1))
        .addkid(
          Node("+").addkid(Node(3)).addkid(Node(4)))
    )

def test_precidence_mul4():
    parser = new_parser()
    parser.init("(3+4)*1")
    i, node = parser.Expr(0)
    eq(node,
       Node("*")
        .addkid(
          Node("+").addkid(Node(3)).addkid(Node(4)))
        .addkid(Node(1))
    )

@raises(SyntaxError)
def test_parse_neg():
    parser = new_parser()
    parser.init("(3)-/3")
    node = parser.parse()

def test_parse_complex():
    parser = new_parser()
    parser.init("2+3+4*(1+(5-2)/3)-4/3*(2+1)")
    node = parser.parse()
    expected = (
      Node("+")
        .addkid(Node(2))
        .addkid(
          Node("+")
            .addkid(Node(3))
            .addkid(
              Node("-")
                .addkid(
                  Node("*")
                    .addkid(Node(4))
                    .addkid(
                      Node("+")
                        .addkid(Node(1))
                        .addkid(
                          Node("/")
                            .addkid(
                              Node("-")
                                .addkid(Node(5))
                                .addkid(Node(2))
                            )
                            .addkid(Node(3))
                        )
                    )
                )
                .addkid(
                  Node("/")
                    .addkid(Node(4))
                    .addkid(
                      Node("*")
                        .addkid(Node(3))
                        .addkid(
                          Node("+")
                            .addkid(Node(2))
                            .addkid(Node(1))
                        )
                    )
                )
            )
        )
    )
    eq(node, expected)


