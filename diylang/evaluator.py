# -*- coding: utf-8 -*-

from .types import Environment, DiyLangError, Closure, String
from .ast import is_boolean, is_atom, is_symbol, is_list, is_closure, \
    is_integer, is_string
from .parser import KEYWORD_MAPPINGS, unparse

"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""

def quote(q, env):
    return q

def atom(a, env):
    return not is_list(evaluate(a, env))

def eq(l, r, env):
    return atom(l, env) and atom(r, env) and evaluate(l, env) == evaluate(r, env)

def do_if(p, if_true, if_false, env):
    return evaluate(if_true, env) if eq(True, p, env) else evaluate(if_false, env)

def define(symbol, value, env):
    if not is_symbol(symbol) or symbol in KEYWORD_MAPPINGS:
        raise DiyLangError('{} is not a symbol'.format(symbol))
    env.set(symbol, evaluate(value, env))
    return 'Defined {}'.format(symbol)

def add(l, r, env):
    if is_integer(l) and is_integer(r):
        return int(int(l) + int(r))
    raise DiyLangError('Expected two numbers (got {}, {})'.format(l, r))

def subtract(l, r, env):
    if is_integer(l) and is_integer(r):
        return int(int(l) - int(r))
    raise DiyLangError('Expected two numbers (got {}, {})'.format(l, r))

def divide(l, r, env):
    if is_integer(l) and is_integer(r):
        if int(r) == 0:
            raise DiyLangError('Divide by zero')
        return int(int(l) / int(r))
    raise DiyLangError('Expected two numbers (got {}, {})'.format(l, r))

def multiply(l, r, env):
    if is_integer(l) and is_integer(r):
        return int(int(l) * int(r))

def mod(l, r, env):
    if is_integer(l) and is_integer(r):
        if int(r) == 0:
            raise DiyLangError('Mod by zero')
        return int(int(l) % int(r))
    raise DiyLangError('Expected two numbers (got {}, {})'.format(l, r))

def greater(l, r, env):
    if is_integer(l) and is_integer(r):
        return int(l) > int(r)
    raise DiyLangError('Expected two numbers (got {}, {})'.format(l, r))

NUMBER_FUNCTIONS = {
    '+': add,
    '-': subtract,
    '/': divide,
    '*': multiply,
    'mod': mod,
    '>': greater
}

def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""
    if is_list(ast):
        if ast[0] == 'quote':
            return quote(ast[1], env)
        elif ast[0] == 'atom':
            return atom(ast[1], env)
        elif ast[0] == 'eq':
            return eq(ast[1], ast[2], env)
        elif ast[0] == 'if':
            return do_if(evaluate(ast[1], env), ast[2], ast[3], env)
        elif ast[0] == 'define':
            if len(ast) != 3:
                raise DiyLangError('Wrong number of arguments')
            define(ast[1], ast[2], env)
        elif ast[0] in NUMBER_FUNCTIONS:
            return NUMBER_FUNCTIONS[ast[0]](evaluate(ast[1], env), evaluate(ast[2], env), env)
    elif is_symbol(ast):
        return env.lookup(ast)
    return ast
