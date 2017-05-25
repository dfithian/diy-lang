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
    return evaluate(if_true, env) if eq(True, evaluate(p, env), env) else evaluate(if_false, env)

def define(symbol, value, env):
    if not is_symbol(symbol) or symbol in KEYWORD_MAPPINGS:
        raise DiyLangError('{} is not a symbol'.format(symbol))
    env.set(symbol, evaluate(value, env))
    return 'Defined {}'.format(symbol)

def do_lambda(params, body, env):
    if not is_list(params):
        raise DiyLangError('Not a list: {}'.format(params))
    return Closure(env, params, body)

def do_closure(closure, args, env):
    new_args = [evaluate(arg, env) for arg in args]
    if len(closure.params) != len(new_args):
        raise DiyLangError('Closure wrong number of arguments, expected {} got {}' \
                           .format(len(closure.params), len(new_args)))
    new_env = Environment(closure.env.bindings).extend(dict(zip(closure.params, new_args)))
    return evaluate(closure.body, new_env)

def cond(xs, env):
    if len(xs) == 0:
        return False
    if evaluate(xs[0][0], env):
        return evaluate(xs[0][1], env)
    return cond(xs[1:], env)

def let(bindings, exp, env):
    new_env = Environment(env.bindings)
    for binding in bindings:
        binding[1] = evaluate(binding[1], new_env)
        new_env = new_env.extend(dict([(binding[0], binding[1])]))
    return evaluate(exp, new_env)

def defn(symbol, params, body, env):
    return define(symbol, do_lambda(params, body, env), env)

def cons(x, xs, env):
    s = is_string(xs)
    if s:
        ret = String(x.val + xs.val)
    else:
        ret = [evaluate(x, env)] + evaluate(xs, env)
    return ret

def head(xs, env):
    s = is_string(xs)
    if s:
        xs = xs.val
    if len(xs) == 0:
        raise DiyLangError('No head of empty list')
    return String(xs[0]) if s else xs[0]

def tail(xs, env):
    s = is_string(xs)
    if s:
        xs = xs.val
    if len(xs) == 0:
        raise DiyLangError('No tail of empty list')
    return String(xs[1:]) if s else xs[1:]

def empty(xs, env):
    if is_string(xs):
        xs = xs.val
    return len(xs) == 0

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

def call_with_n_args(f, xs, n, env):
    if len(xs) != n:
        raise DiyLangError('Wrong number of arguments')
    if n == 1:
        return f(xs[0], env)
    elif n == 2:
        return f(xs[0], xs[1], env)
    elif n == 3:
        return f(xs[0], xs[1], xs[2], env)

BUILTIN_FUNCTIONS = {
    'quote':  lambda xs, env: call_with_n_args(quote,     xs, 1, env),
    'atom':   lambda xs, env: call_with_n_args(atom,      xs, 1, env),
    'eq':     lambda xs, env: call_with_n_args(eq,        xs, 2, env),
    'if':     lambda xs, env: call_with_n_args(do_if,     xs, 3, env),
    'define': lambda xs, env: call_with_n_args(define,    xs, 2, env),
    'lambda': lambda xs, env: call_with_n_args(do_lambda, xs, 2, env),
    'cons':   lambda xs, env: call_with_n_args(cons,      xs, 2, env),
    'cond':   lambda xs, env: call_with_n_args(cond,      xs, 1, env),
    'let':    lambda xs, env: call_with_n_args(let,       xs, 2, env),
    'defn':   lambda xs, env: call_with_n_args(defn,      xs, 3, env)
}

LIST_FUNCTIONS = {
    'head': head,
    'tail': tail,
    'empty': empty
}

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
        if len(ast) == 0:
            raise DiyLangError('Empty list encountered')
        elif is_list(ast[0]):
            if len(ast) > 1:
                return evaluate([evaluate(ast[0], env)] + ast[1:], env)
            return evaluate(ast[0], env)
        elif ast[0] in BUILTIN_FUNCTIONS:
            return BUILTIN_FUNCTIONS[ast[0]](ast[1:], env)
        elif is_closure(ast[0]):
            return do_closure(ast[0], ast[1:], env)
        elif ast[0] in LIST_FUNCTIONS:
            if is_string(ast[1]):
                return LIST_FUNCTIONS[ast[0]](ast[1], env)
            return LIST_FUNCTIONS[ast[0]](evaluate(ast[1:], env), env)
        elif ast[0] in NUMBER_FUNCTIONS:
            return NUMBER_FUNCTIONS[ast[0]](evaluate(ast[1], env), evaluate(ast[2], env), env)
        elif ast[0] in env.bindings:
            binding = env.lookup(ast[0])
            if is_closure(binding):
                return do_closure(binding, ast[1:], env)
            return binding
        else:
            raise DiyLangError('{} is not a function'.format(ast[0]))
    elif is_symbol(ast):
        return env.lookup(ast)
    return ast
