def tokenize(exp):
    tokens = exp.replace('(', ' ( ').replace(')', ' ) ').split()
    # print tokens
    return tokens


def atom(token):
    "Numbers become numbers; every other token is a str"
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return str(token)


def read_from_token(tokens):
    "Read an expression from a sequence of tokens"
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_token(tokens))
        tokens.pop(0)
        # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def parse(exp):
    # parse the program
    # abstract the syntax tree
    token = read_from_token(tokenize(exp))
    # print token
    # evaluate the expression
    return token


def standard_env():
    "An environment with some Scheme standard procedures."
    import math
    import operator as op
    env = Env()
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
    env.update({
        '+':	op.add,
        '-':	op.sub,
        '*':	op.mul,
        '/':	op.div,
        '>':	op.gt,
        '<':	op.lt,
        '>=':	op.ge,
        '<=':	op.le,
        '=':	op.eq,
        'abs':	abs,
        'append':	op.add,
        'apply':	apply,
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?':	op.is_,
        'equal?':	op.eq,
        'length':	len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map':		map,
        'max':		max,
        'min':		min,
        'not':     	op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, (int, float)),
        'procedure?': callable,
        'round':  	round,
        'symbol?': lambda x: isinstance(x, str),
    })
    return env


class Env(dict):

    def __init__(self, parms=(), args=(), outer=None):
    #    print "env parms", parms
    #    print "env args", args

        self.update(zip(parms, args))

        self.outer = outer

    def find(self, var):
        return self if (var in self) else self.outer.find(var)


class Procedure(object):

    def __init__(self, parms, body, env):
    #    print "proce", parms, body
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
    #    print "args", args
    #    print "body", self.body
    #    print "parms", self.parms
        return eval(self.body, Env(self.parms, args, self.env))


def eval(x, env=standard_env()):
    # print x
    # for item1, item2 in env.items():
    #	print item1, item2
    if isinstance(x, str):  # variable reference
                # print "dict", env
        return env.find(x)[x]
    elif not isinstance(x, list):  # constant literal
        return x
    elif x[0] == 'quote':  # quotation
        (_, exp) = x
        return exp
    elif x[0] == 'if':  # conditional
        (_, test, conseq, alt) = x
    #    print "xxx", test, "   ", conseq, "    ", alt
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':  # definition
        (_, var, exp) = x
    #    print var
        env[var] = eval(exp, env)
    elif x[0] == 'set!':
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':  # procedure
        (_, parms, body) = x
    #    print "lambda", parms, body
        return Procedure(parms, body, env)
    else:  # procedure call
    #   print "procedure", x[0]
        proc = eval(x[0], env)
    #    print "proc", proc
        args = [eval(arg, env) for arg in x[1:]]
    #    print proc, "   ", args
        return proc(*args)


def schemestr(exp):
    # "Convert a Python object back into a Scheme-readable string."
    if isinstance(exp, list):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


def repl(prompt='lisp> '):
    # user interface
    while True:
        exp = raw_input(prompt)
        if exp == 'exit':
            exit()
        else:
            val = eval(parse(exp))
            if val is not None:
                print(schemestr(val))

if __name__ == '__main__':
    repl()
