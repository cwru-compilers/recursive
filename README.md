# Example Recursive Descent Parser

By Tim Henderson

### Setup

    $ git clone https://github.com/cwru-compilers/recursive.git
    $ cd recursive
    $ virtualenv --no-site-packages env
    $ . env/bin/activate
    $ pip install -r requirements.txt

### Run the tests

    $ nosetests

### Notes

1. The Lexer is handwritten and in lexer.py
2. There are tests which can be run with `nosetests`

# Grammar

## Original

    Expr   -> Expr PLUS Term
            | Expr DASH Term
    Term   -> Term STAR Unary
            | Term SLASH Unary
    Unary  -> DASH Factor
            | Factor
    Factor -> NUMBER
            | LPAREN Expr RPAREN

## LL(1)

    Expr   -> Term Expr_
    Expr_  -> PLUS Term Expr_
            | DASH Term Expr_
            | e
    Term   -> Unary Term_
    Term_  -> STAR Unary Term_
            | SLASH Unary Term_
            | e
    Unary  -> DASH Factor
            | Factor
    Factor -> NUMBER
            | LPAREN Expr RPAREN


