from lexer import Class
from functools import wraps
import pickle


class Node:
    pass


class Program(Node):
    def __init__(self, nodes):
        self.nodes = nodes


class Decl(Node):
    def __init__(self, type_, id_):
        self.type_ = type_
        self.id_ = id_


class ArrayDecl(Node):
    def __init__(self, type_, id_, size, from_, to_, elems):
        self.type_ = type_
        self.id_ = id_
        self.size = size
        self.from_ = from_
        self.to_ = to_
        self.elems = elems


class ArrayElem(Node):
    def __init__(self, id_, index):
        self.id_ = id_
        self.index = index


class VarDecl(Node):
    def __init__(self, decls):
        self.decls = decls


class Assign(Node):
    def __init__(self, id_, expr):
        self.id_ = id_
        self.expr = expr


class If(Node):
    def __init__(self, cond, true, false):
        self.cond = cond
        self.true = true
        self.false = false


class While(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block


class RepeatUntil(Node):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block


class For(Node):
    def __init__(self, init, to, reversed, block):
        self.init = init
        self.to = to
        self.reversed = reversed
        self.block = block


class FuncImpl(Node):
    def __init__(self, type_, id_, params, block):
        self.type_ = type_
        self.id_ = id_
        self.params = params
        self.block = block


class FuncCall(Node):
    def __init__(self, id_, args):
        self.id_ = id_
        self.args = args


class ProcImpl(Node):
    def __init__(self, id_, params, block):
        self.id_ = id_
        self.params = params
        self.block = block


class ProcCall(Node):
    def __init__(self, id_, args):
        self.id_ = id_
        self.args = args


class Block(Node):
    def __init__(self, var_decls, is_main, nodes):
        self.var_decls = var_decls
        self.is_main = is_main
        self.nodes = nodes


class Params(Node):
    def __init__(self, params):
        self.params = params


class Args(Node):
    def __init__(self, args):
        self.args = args


class Elems(Node):
    def __init__(self, elems):
        self.elems = elems


class Break(Node):
    pass


class Continue(Node):
    pass


class Exit(Node):
    def __init__(self, expr):
        self.expr = expr


class Type(Node):
    def __init__(self, value):
        self.value = value


class Int(Node):
    def __init__(self, value):
        self.value = value


class Real(Node):
    def __init__(self, value):
        self.value = value


class Boolean(Node):
    def __init__(self, value):
        self.value = value


class Char(Node):
    def __init__(self, value):
        self.value = value


class String(Node):
    def __init__(self, value):
        self.value = value


class Id(Node):
    def __init__(self, value):
        self.value = value


class BinOp(Node):
    def __init__(self, symbol, first, second, roundings=None):
        self.symbol = symbol
        self.first = first
        self.second = second
        self.roundings = roundings


class UnOp(Node):
    def __init__(self, symbol, first):
        self.symbol = symbol
        self.first = first


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.curr = tokens.pop(0)
        self.prev = None

    def restorable(call):
        @wraps(call)
        def wrapper(self, *args, **kwargs):
            state = pickle.dumps(self.__dict__)
            result = call(self, *args, **kwargs)
            self.__dict__ = pickle.loads(state)
            return result

        return wrapper

    def eat(self, class_):
        if self.curr.class_ == class_:
            self.prev = self.curr
            self.curr = self.tokens.pop(0)
        else:
            self.die_type(class_.name, self.curr.class_.name)

    def program(self):
        nodes = []
        while self.curr.class_ != Class.EOF:
            if self.curr.class_ == Class.VAR:
                nodes.append(self.var_decls(is_main=True))
            elif self.curr.class_ == Class.FUNCTION:
                nodes.append(self.func_impl())
            elif self.curr.class_ == Class.PROCEDURE:
                nodes.append(self.proc_impl())
            elif self.curr.class_ == Class.BEGIN:
                self.eat(Class.BEGIN)
                nodes.append(self.block(is_main=True))
                self.eat(Class.END)
                self.eat(Class.DOT)
            else:
                self.die_deriv(self.program.__name__)
        return Program(nodes)

    def id_(self):
        is_array_elem = self.prev.class_ != Class.TYPE
        id_ = Id(self.curr.lexeme)
        self.eat(Class.ID)
        if self.curr.class_ == Class.LPAREN and self.is_func_call():
            self.eat(Class.LPAREN)
            args = self.args()
            self.eat(Class.RPAREN)
            return FuncCall(id_, args)
        elif self.curr.class_ == Class.LPAREN and self.is_func_call():
            self.eat(Class.LPAREN)
            args = self.args()
            self.eat(Class.RPAREN)
            return ProcCall(id_, args)
        elif self.curr.class_ == Class.LBRACKET and is_array_elem:
            self.eat(Class.LBRACKET)
            index = self.expr()
            self.eat(Class.RBRACKET)
            id_ = ArrayElem(id_, index)
        if self.curr.class_ == Class.ASSIGN:
            self.eat(Class.ASSIGN)
            expr = None
            if self.is_compare():
                expr = self.compare()
            else:
                expr = self.expr()
            return Assign(id_, expr)
        else:
            return id_

    def decl(self):
        type_ = self.type_()
        id_ = self.id_()
        if self.curr.class_ == Class.LBRACKET:
            self.eat(Class.LBRACKET)
            size = None
            if self.curr.class_ != Class.RBRACKET:
                size = self.expr()
            self.eat(Class.RBRACKET)
            elems = None
            if self.curr.class_ == Class.ASSIGN:
                self.eat(Class.ASSIGN)
                self.eat(Class.LBRACE)
                elems = self.elems()
                self.eat(Class.RBRACE)
            self.eat(Class.SEMICOLON)
            return ArrayDecl(type_, id_, size, elems)
        elif self.curr.class_ == Class.LPAREN:
            self.eat(Class.LPAREN)
            params = self.params()
            self.eat(Class.RPAREN)
            self.eat(Class.LBRACE)
            block = self.block()
            self.eat(Class.RBRACE)
            return FuncImpl(type_, id_, params, block)
        else:
            self.eat(Class.SEMICOLON)
            return Decl(type_, id_)

    def var_decls(self, is_main):
        self.eat(Class.VAR)
        declarations = []
        while self.curr.class_ not in [Class.BEGIN, Class.PROCEDURE, Class.FUNCTION, Class.EOF]:
            ids = []
            while self.curr.class_ != Class.COLON:
                if len(ids) > 0:
                    self.eat(Class.COMMA)
                id_ = self.id_()
                ids.append(id_)

            self.eat(Class.COLON)
            new_decls = []

            if self.curr.class_ == Class.ARRAY:
                new_decls.extend(self.array_init(ids))
            elif self.curr.class_ == Class.TYPE:
                type_ = self.type_()
                if self.curr.class_ == Class.LBRACKET:
                    self.eat(Class.LBRACKET)
                    size = self.expr()
                    self.eat(Class.RBRACKET)
                    for id in ids:
                        new_decls.append(ArrayDecl(type_, id, size, None, None, None))
                else:
                    for id in ids:
                        new_decls.append(Decl(type_, id))

            declarations.extend(new_decls)
            self.eat(Class.SEMICOLON)

        var_decls = VarDecl(declarations)

        self.eat(Class.BEGIN)
        block = self.block(var_decls=var_decls, is_main=is_main)
        self.eat(Class.END)
        if is_main:
            self.eat(Class.DOT)
        else:
            self.eat(Class.SEMICOLON)

        return block

    def array_init(self, ids):
        array_decls = []

        self.eat(Class.ARRAY)
        self.eat(Class.LBRACKET)
        from_ = Int(self.curr.lexeme)
        self.eat(Class.INT)
        self.eat(Class.DOT)
        self.eat(Class.DOT)
        to_ = Int(self.curr.lexeme)
        self.eat(Class.INT)
        self.eat(Class.RBRACKET)
        self.eat(Class.OF)
        type_ = self.type_()
        elems = None
        if self.curr.class_ != Class.SEMICOLON:
            self.eat(Class.EQ)
            self.eat(Class.LPAREN)
            elems = self.elems()
            self.eat(Class.RPAREN)

        for id in ids:
            array_decls.append(ArrayDecl(type_, id, None, from_, to_, elems))

        return array_decls

    def func_impl(self):
        self.eat(Class.FUNCTION)
        id_ = self.id_()
        self.eat(Class.LPAREN)
        params = self.params()
        self.eat(Class.RPAREN)
        self.eat(Class.COLON)
        type_ = self.type_()
        self.eat(Class.SEMICOLON)

        block = None
        if self.curr.class_ == Class.VAR:
            block = self.var_decls(is_main=False)
        else:
            self.eat(Class.BEGIN)
            block = self.block()
            self.eat(Class.END)
            self.eat(Class.SEMICOLON)

        return FuncImpl(type_, id_, params, block)

    def proc_impl(self):
        self.eat(Class.PROCEDURE)
        id_ = self.id_()
        self.eat(Class.LPAREN)
        params = self.params()
        self.eat(Class.RPAREN)
        self.eat(Class.SEMICOLON)

        block = None
        if self.curr.class_ == Class.VAR:
            block = self.var_decls(is_main=False)
        else:
            self.eat(Class.BEGIN)
            block = self.block()
            self.eat(Class.END)
            self.eat(Class.SEMICOLON)

        return ProcImpl(id_, params, block)

    def if_(self):
        self.eat(Class.IF)
        cond = self.logic()
        self.eat(Class.THEN)
        self.eat(Class.BEGIN)
        true = self.block()
        false = None
        self.eat(Class.END)
        if self.curr.class_ == Class.ELSE:
            self.eat(Class.ELSE)
            self.eat(Class.BEGIN)
            false = self.block()
            self.eat(Class.END)

        self.eat(Class.SEMICOLON)
        return If(cond, true, false)

    def while_(self):
        self.eat(Class.WHILE)
        cond = self.logic()
        self.eat(Class.DO)
        self.eat(Class.BEGIN)
        block = self.block()
        self.eat(Class.END)
        self.eat(Class.SEMICOLON)
        return While(cond, block)

    def repeat_until(self):
        self.eat(Class.REPEAT)
        block = self.block()
        self.eat(Class.UNTIL)
        cond = self.logic()
        self.eat(Class.SEMICOLON)
        return RepeatUntil(cond, block)

    def for_(self):
        self.eat(Class.FOR)
        init = self.id_()

        reversed = False
        if self.curr.class_ == Class.TO:
            self.eat(Class.TO)
        else:
            self.eat(Class.DOWNTO)
            reversed = True

        to = self.expr()
        self.eat(Class.DO)
        self.eat(Class.BEGIN)
        block = self.block()
        self.eat(Class.END)
        self.eat(Class.SEMICOLON)
        return For(init, to, reversed, block)

    def block(self, var_decls=None, is_main=False):
        nodes = []
        while self.curr.class_ not in [Class.END, Class.UNTIL]:
            if self.curr.class_ == Class.IF:
                nodes.append(self.if_())
            elif self.curr.class_ == Class.WHILE:
                nodes.append(self.while_())
            elif self.curr.class_ == Class.REPEAT:
                nodes.append(self.repeat_until())
            elif self.curr.class_ == Class.FOR:
                nodes.append(self.for_())
            elif self.curr.class_ == Class.BREAK:
                nodes.append(self.break_())
            elif self.curr.class_ == Class.CONTINUE:
                nodes.append(self.continue_())
            elif self.curr.class_ == Class.EXIT:
                nodes.append(self.exit_())
            elif self.curr.class_ == Class.TYPE:
                nodes.append(self.decl())
            elif self.curr.class_ == Class.ID:
                nodes.append(self.id_())
                self.eat(Class.SEMICOLON)
            else:
                self.die_deriv(self.block.__name__)
        return Block(var_decls, is_main, nodes)

    def params(self):
        params = []
        ids = []
        while self.curr.class_ != Class.COLON:
            if len(ids) > 0:
                self.eat(Class.COMMA)
            id_ = self.id_()
            ids.append(id_)

        self.eat(Class.COLON)
        type_ = self.type_()
        for id in ids:
            params.append(Decl(type_, id))
        return Params(params)

    def args(self):
        args = []
        index = 0
        while self.curr.class_ != Class.RPAREN:
            if len(args) > 0:
                self.eat(Class.COMMA)
            args.append(self.expr())
        return Args(args)

    def elems(self):
        elems = []
        while self.curr.class_ != Class.RPAREN:
            if len(elems) > 0:
                self.eat(Class.COMMA)
            elems.append(self.expr())
        return Elems(elems)

    def exit_(self):
        self.eat(Class.EXIT)
        expr = None
        if self.curr.class_ == Class.LPAREN:
            self.eat(Class.LPAREN)
            expr = self.expr()
            self.eat(Class.RPAREN)
        self.eat(Class.SEMICOLON)
        return Exit(expr)

    def break_(self):
        self.eat(Class.BREAK)
        self.eat(Class.SEMICOLON)
        return Break()

    def continue_(self):
        self.eat(Class.CONTINUE)
        self.eat(Class.SEMICOLON)
        return Continue()

    def type_(self):
        type_ = Type(self.curr.lexeme)
        self.eat(Class.TYPE)
        return type_

    def factor(self):
        if self.curr.class_ == Class.INT:
            value = Int(self.curr.lexeme)
            self.eat(Class.INT)
            return value
        elif self.curr.class_ == Class.CHAR:
            value = Char(self.curr.lexeme)
            self.eat(Class.CHAR)
            return value
        elif self.curr.class_ == Class.STRING:
            value = String(self.curr.lexeme)
            self.eat(Class.STRING)
            return value
        elif self.curr.class_ == Class.BOOLEAN:
            value = Boolean(self.curr.lexeme)
            self.eat(Class.BOOLEAN)
            return value
        elif self.curr.class_ == Class.REAL:
            value = Real(self.curr.lexeme)
            self.eat(Class.REAL)
            return value
        elif self.curr.class_ == Class.ID:
            return self.id_()
        elif self.curr.class_ in [Class.MINUS, Class.NOT]:
            op = self.curr
            self.eat(self.curr.class_)
            first = None
            if self.curr.class_ == Class.LPAREN:
                self.eat(Class.LPAREN)
                first = self.logic()
                self.eat(Class.RPAREN)
            else:
                first = self.factor()
            return UnOp(op.lexeme, first)
        elif self.curr.class_ == Class.LPAREN:
            self.eat(Class.LPAREN)
            first = self.logic()
            self.eat(Class.RPAREN)
            return first
        elif self.curr.class_ == Class.SEMICOLON:
            return None
        else:
            self.die_deriv(self.factor.__name__)

    def term(self):
        first = self.factor()
        while self.curr.class_ in [Class.STAR, Class.FWDSLASH, Class.DIV, Class.MOD, Class.XOR]:
            if self.curr.class_ == Class.STAR:
                op = self.curr.lexeme
                self.eat(Class.STAR)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.FWDSLASH:
                op = self.curr.lexeme
                self.eat(Class.FWDSLASH)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.DIV:
                op = self.curr.lexeme
                self.eat(Class.DIV)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.MOD:
                op = self.curr.lexeme
                self.eat(Class.MOD)
                second = self.factor()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.XOR:
                op = self.curr.lexeme
                self.eat(Class.XOR)
                second = self.factor()
                first = BinOp(op, first, second)
        return first

    def expr(self):
        first = self.term()
        while self.curr.class_ in [Class.PLUS, Class.MINUS]:
            if self.curr.class_ == Class.PLUS:
                op = self.curr.lexeme
                self.eat(Class.PLUS)
                second = self.term()
                first = BinOp(op, first, second)
            elif self.curr.class_ == Class.MINUS:
                op = self.curr.lexeme
                self.eat(Class.MINUS)
                second = self.term()
                first = BinOp(op, first, second)

        if self.curr.class_ == Class.COLON:
            self.eat(Class.COLON)
            first.roundings = []
            first.roundings.append(Int(self.curr.lexeme))
            self.eat(Class.INT)
            self.eat(Class.COLON)
            first.roundings.append(Int(self.curr.lexeme))
            self.eat(Class.INT)

        return first

    def compare(self):
        first = self.expr()
        if self.curr.class_ == Class.EQ:
            op = self.curr.lexeme
            self.eat(Class.EQ)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.NEQ:
            op = self.curr.lexeme
            self.eat(Class.NEQ)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.LT:
            op = self.curr.lexeme
            self.eat(Class.LT)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.GT:
            op = self.curr.lexeme
            self.eat(Class.GT)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.LTE:
            op = self.curr.lexeme
            self.eat(Class.LTE)
            second = self.expr()
            return BinOp(op, first, second)
        elif self.curr.class_ == Class.GTE:
            op = self.curr.lexeme
            self.eat(Class.GTE)
            second = self.expr()
            return BinOp(op, first, second)
        else:
            return first

    def logic_term(self):
        first = self.compare()
        while self.curr.class_ == Class.AND:
            op = self.curr.lexeme
            self.eat(Class.AND)
            second = self.compare()
            first = BinOp(op, first, second)
        return first

    def logic(self):
        first = self.logic_term()
        while self.curr.class_ == Class.OR:
            op = self.curr.lexeme
            self.eat(Class.OR)
            second = self.logic_term()
            first = BinOp(op, first, second)
        return first

    @restorable
    def is_func_call(self):
        try:
            self.eat(Class.LPAREN)
            self.args()
            self.eat(Class.RPAREN)

            if self.curr.class_ == Class.SEMICOLON:
                return self.curr.class_ != Class.BEGIN
            else:
                return True
        except:
            return False

    @restorable
    def is_compare(self):
        try:
            self.id_()
            curr = self.curr.class_
            if curr in [Class.EQ, Class.NEQ, Class.GTE, Class.LTE, Class.GT, Class.LT]:
                return True
            return False
        except:
            return False

    def parse(self):
        return self.program()

    def die(self, text):
        raise SystemExit(text)

    def die_deriv(self, fun):
        self.die("Derivation error: {}".format(fun))

    def die_type(self, expected, found):
        self.die("Expected: {}, Found: {}".format(expected, found))

