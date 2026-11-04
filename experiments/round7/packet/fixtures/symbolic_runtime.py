"""Minimal executable toy symbolic language for H2. Not a general-purpose compiler.

Grammar:
    program = '@' INTEGER '(' IDENT ':' 'I' ')' '{' expr '}'
    expr    = 'R' '(' term ',' IDENT ')' '{' expr '}'
            | '?' '(' cond ',' expr ',' expr ')'
            | '!' INTEGER '(' TEMPLATE ',' args ')'
    cond    = term '=' term
    term    = IDENT ('+' INTEGER)? | INTEGER

Fixed templates T0/T1. This is an intentionally tiny executable slice, not a
universal semantics claim, an optimized opcode encoding, or a dedicated tokenizer.
"""
import re

TOKEN = re.compile(r'\s*(@|\?|!|\{|\}|\(|\)|:|,|\+|=|R|I|T[01]|[A-Za-z_][A-Za-z_0-9]*|\d+)')

class SyntaxErrorIR(ValueError):
    pass


def lex(src):
    out=[]
    pos=0
    while pos < len(src):
        m = TOKEN.match(src, pos)
        if not m:
            if src[pos:].isspace():
                break
            raise SyntaxErrorIR(f'invalid character at offset {pos}')
        out.append(m.group(1))
        pos=m.end()
    return out


class Parser:
    def __init__(self, tokens):
        self.t=tokens
        self.p=0

    def take(self, target=None):
        if self.p >= len(self.t):
            raise SyntaxErrorIR('unexpected end of input')
        x=self.t[self.p]
        self.p+=1
        if target is not None and x != target:
            raise SyntaxErrorIR(f'expected {target!r}, got {x!r}')
        return x

    def term(self):
        x=self.take()
        if x.isdigit():
            return ('int', int(x))
        if not re.fullmatch(r'[A-Za-z_]\w*',x) or x in ('R','I'):
            raise SyntaxErrorIR('invalid operand: '+x)
        if self.p<len(self.t) and self.t[self.p]=='+':
            self.take('+')
            return ('plus', x, int(self.take()))
        return ('var',x)

    def expr(self):
        kind=self.take()
        if kind=='R':
            self.take('(')
            count=self.term()
            self.take(',')
            index=self.take()
            if not re.fullmatch(r'[A-Za-z_]\w*',index):
                raise SyntaxErrorIR('invalid loop index')
            self.take(')')
            self.take('{')
            body=self.expr()
            self.take('}')
            return ('repeat',count,index,body)
        if kind=='?':
            self.take('(')
            lhs=self.term()
            self.take('=')
            rhs=self.term()
            self.take(',')
            a=self.expr()
            self.take(',')
            b=self.expr()
            self.take(')')
            return ('if',lhs,rhs,a,b)
        if kind=='!':
            op=self.take()
            if op!='7':
                raise SyntaxErrorIR('unknown effect opcode')
            self.take('(')
            template=self.take()
            if template not in ('T0','T1'):
                raise SyntaxErrorIR('invalid template')
            args=[]
            while self.p<len(self.t) and self.t[self.p]==',':
                self.take(',')
                args.append(self.term())
            self.take(')')
            if len(args) != (1 if template=='T0' else 2):
                raise SyntaxErrorIR('template arity mismatch')
            return ('log',template,args)
        raise SyntaxErrorIR('unknown expression '+kind)


def compile_program(source):
    p=Parser(lex(source))
    p.take('@')
    name=p.take()
    if not name.isdigit():
        raise SyntaxErrorIR('function opcode must be numeric')
    p.take('(')
    param=p.take()
    p.take(':')
    p.take('I')
    p.take(')')
    p.take('{')
    body=p.expr()
    p.take('}')
    if p.p!=len(p.t):
        raise SyntaxErrorIR('trailing tokens')
    return (param,body)


def eval_term(t,env):
    if t[0]=='int': return t[1]
    if t[0]=='var': return env[t[1]]
    return env[t[1]]+t[2]


def execute(source, n):
    if not isinstance(n,int) or isinstance(n,bool):
        raise TypeError('n must be int')
    param,body=compile_program(source)
    log=[]
    def run(ast,env):
        tag=ast[0]
        if tag=='repeat':
            count=eval_term(ast[1],env)
            for idx in range(max(0,count)):
                run(ast[3],{**env,ast[2]:idx})
        elif tag=='if':
            branch=ast[3] if eval_term(ast[1],env)==eval_term(ast[2],env) else ast[4]
            run(branch,env)
        else:
            args=[eval_term(x,env) for x in ast[2]]
            if ast[1]=='T0':
                log.append(f'Starting controller service for {args[0]} runs')
            else:
                log.append(f'Restarting controller service for run {args[0]} of {args[1]}')
    run(body,{param:n})
    return log
