# Create an AST from a boolean expression. AST is a tuple
# consisting of an operator and a list of operands.
#
# Note: NOT is not supported.

# Example:
#   given a AND b
#   returns ('AND', ['a','b'])
#
# Copyright 2006, by Paul McGuir
# Modified: 02/2011 for csci1580
# Modified: 02/2018 for data2040

import pyparsing
from typing import Union


# TODO: Consider implementing this as a Python Abstract Base Class
class BoolOperand(object):
    reprsymbol = None

    def __init__(self, t):
        self.args = t[0][0::2]

    def __str__(self):
        sep = " %s " % self.reprsymbol
        return "(" + sep.join(map(str, self.args)) + ")"

    def eval_expr(self):
        raise NotImplementedError


class BoolAnd(BoolOperand):
    reprsymbol = 'AND'

    def eval_expr(self):
        lst = []
        for a in self.args:
            if not isinstance(a, BoolOperand):
                elem = a
            else:
                elem = a.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst


class BoolOr(BoolOperand):
    reprsymbol = 'OR'

    def eval_expr(self):
        lst = []
        for a in self.args:
            if not isinstance(a, BoolOperand):
                elem = a
            else:
                elem = a.eval_expr()
            lst.append(elem)
        return self.reprsymbol, lst


boolOperand = pyparsing.Word(pyparsing.alphanums + "!#$%&'*+,-./:;<=>?@[]^_`{|}~\\")
opList = [("AND", 2, pyparsing.opAssoc.LEFT, BoolAnd),
          ("OR", 2, pyparsing.opAssoc.LEFT, BoolOr)]
boolExpr = pyparsing.operatorPrecedence(boolOperand, opList)


def bool_expr_ast(expr : str) -> Union[str, tuple]:
    expr = expr.strip()
    parsed_expr = boolExpr.parseString(expr)[0]
    if not isinstance(parsed_expr, BoolOperand):
        return expr
    else:
        return parsed_expr.eval_expr()

if __name__ == '__main__':
    print(bool_expr_ast('b AND c OR d'))