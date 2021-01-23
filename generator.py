from parser import Id, FuncCall, BinOp, ArrayElem, Int, Char, Real, String, FuncImpl, Assign, While, For, If
from visitor import Visitor
import re


class Generator(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.py = ""
        self.level = 0
        self.ids = {}

    def get_symbol(self, node):
        return self.ids[node.value if isinstance(node, Id) else node.id_.value]

    def append(self, text):
        self.py += str(text)

    def newline(self):
        self.append('\n\r')

    def indent(self):
        for i in range(self.level):
            self.append('\t')

    def visit_Program(self, parent, node):
        for s in node.symbols:
            self.ids[s.id_] = s.copy()
        for n in node.nodes:
            self.visit(node, n)

    def visit_Decl(self, parent, node):
        self.visit(node, node.type_)
        self.append(' ')
        self.visit(node, node.id_)
        if node.type_.value == 'string':
            self.append('[100] = {0}')
        self.append(';')

    def visit_ArrayDecl(self, parent, node):
        if node.type_.value == 'string':
            self.append('char')
        else:
            self.visit(node, node.type_)
        self.append(' ')
        self.visit(node, node.id_)
        if node.elems is not None:
            self.append('[')
            self.visit(node, node.elems)
            self.append(']')
        elif node.size is not None:
            self.append('[')
            self.visit(node, node.size)
            self.append(']')
        elif node.from_ is not None and node.to_ is not None:
            self.append('[')
            self.append(str(node.to_.value - node.from_.value + 1))
            self.append(']')
        else:
            self.append('[100]')
        self.append(';')

    def visit_ArrayElem(self, parent, node):
        self.visit(node, node.id_)
        self.append('[')
        self.visit(node, node.index)
        symbol = self.get_symbol(node)
        if symbol.type_ == 'string':
            self.append(' - 1')
        self.append(']')

    def visit_Assign(self, parent, node):
        self.visit(node, node.id_)
        self.append(' = ')
        self.visit(node, node.expr)

    def visit_If(self, parent, node):
        self.append('if (')
        self.visit(node, node.cond)
        self.append(') {')
        self.newline()
        self.visit(node, node.true)
        if node.false is not None:
            self.indent()
            self.append('}')
            self.newline()
            self.indent()
            self.append('else {')
            self.newline()
            self.visit(node, node.false)
        self.indent()
        self.append('}')
        self.newline()

    def visit_While(self, parent, node):
        self.append('while (')
        self.visit(node, node.cond)
        self.append(') {')
        self.newline()
        self.visit(node, node.block)
        self.indent()
        self.append('}')
        self.newline()

    def visit_For(self, parent, node):
        self.append('for (')
        self.visit(node, node.init)
        self.append('; ')
        self.append(node.init.id_.value + (' >= ' if node.reversed else ' <= '))
        self.visit(node, node.to)
        self.append('; ')
        self.append(node.init.id_.value + ' ')
        if not node.reversed:
            self.append('++')
        else:
            self.append('--')
        self.append(') {')
        self.newline()
        self.visit(node, node.block)
        self.indent()
        self.append('}')

    def visit_RepeatUntil(self, parent, node):
        self.append('do {')
        self.newline()
        self.visit(node, node.block)
        self.indent()
        self.append('} while( !(')
        self.visit(node, node.cond)
        self.append(') )');

    def visit_FuncImpl(self, parent, node):
        self.visit(node, node.type_)
        self.append(' ')
        self.append(node.id_.value)
        self.append('(')
        self.visit(node, node.params)
        self.append(') {')
        self.newline()
        self.visit(node, node.block)
        self.append('}')
        self.newline()

    def visit_ProcImpl(self, parent, node):
        self.append('void ')
        self.append(node.id_.value)
        self.append('(')
        self.visit(node, node.params)
        self.append(') {')
        self.newline()
        self.visit(node, node.block)
        self.append('}')
        self.newline()

    def visit_FuncCall(self, parent, node):
        func = node.id_.value
        args = node.args.args
        if func == 'writeln' and len(args) == 0:
            self.append('printf("\\n")')
        elif func == 'writeln' or func == 'write':
            self.append('printf("')
            for i, a in enumerate(args[0:]):
                type_ = None
                roundings = None

                if isinstance(a, Id) or (isinstance(a, FuncCall) and a.id_.value != 'chr') or isinstance(a, ArrayElem):
                    symbol = self.get_symbol(a)
                    type_ = symbol.type_
                elif isinstance(a, BinOp):
                    symbol = self.get_symbol(a.first)
                    type_ = symbol.type_
                    if type_ == 'real':
                        roundings = a.roundings

                self.append('%')

                if isinstance(a, Int) or type_ == 'integer':
                    self.append('d')
                elif isinstance(a, Char) or type_ == 'char':
                    self.append('c')
                elif isinstance(a, Real) or type_ == 'real':
                    if roundings is not None:
                        self.append('.')
                        self.append(roundings[1].value)
                    self.append('f')
                elif isinstance(a, String) or type_ == 'string':
                    self.append('s')
                elif isinstance(a, FuncCall):
                    if a.id_.value == 'chr':
                        self.append('c')

            if func == 'writeln':
                self.append('\\n')
            self.append('", ')
            for i, a in enumerate(args[0:]):
                if i > 0:
                    self.append(', ')

                if isinstance(a, FuncCall):
                    if a.id_.value == 'chr':
                        self.visit(node, a.args.args[0])
                    else:
                        self.visit(node, node.args)
                else:
                    self.visit(node.args, a)
            self.append(')')
        elif func == 'readln' or func == 'read':
            self.append('scanf("')
            for i, a in enumerate(args[0:]):
                type_ = None

                if isinstance(a, Id) or isinstance(a, ArrayElem):
                    symbol = self.get_symbol(a)
                    type_ = symbol.type_

                if isinstance(a, Int) or type_ == 'integer':
                    self.append('%d')
                elif isinstance(a, Char) or type_ == 'char':
                    self.append('%c')
                elif isinstance(a, Real) or type_ == 'real':
                    self.append('%f')
                elif isinstance(a, String) or type_ == 'string':
                    self.append('%s')
                elif isinstance(a, BinOp):
                    self.append('%d')
                elif isinstance(a, FuncCall):
                    if a.id_.value == 'chr':
                        self.append('%c')
            self.append('", ')
            for i, a in enumerate(args[0:]):
                if i > 0:
                    self.append(', ')

                self.append('&')
                self.visit(node.args, a)
            self.append(')')
        elif func == 'length':
            self.append('strlen(')
            self.visit(node, node.args)
            self.append(')')
        elif func == 'concat':
            self.append('strcat(')
            self.visit(node.args, args[0])
            self.append(', ')
            self.visit(node.args, args[1])
            self.append(')')
        elif func == 'chr':
            self.append('(')
            self.visit(node, node.args)
            self.append(')')
        elif func == 'ord':
            self.visit(node, node.args)
        elif func == 'inc':
            self.visit(node, node.args)
            self.append(' += 1')
        elif func == 'dec':
            self.visit(node, node.args)
            self.append(' -= 1')
        elif func == 'insert':
            self.append(args[1].value)
            self.append('[')
            self.append(args[2].value)
            self.append(' - 1] = ')
            self.visit(node, args[0])
        else:
            self.append(func)
            self.append('(')
            self.visit(node, node.args)
            self.append(')')

    def visit_ProcCall(self, parent, node):
        func = node.id_.value
        args = node.args.args
        self.append(func)
        self.append('(')
        self.visit(node, node.args)
        self.append(')')

    def visit_VarDecl(self, parent, node):
        for decl in node.decls:
            self.indent()
            self.visit(node, decl)
            self.newline()

        self.newline()

    def visit_Block(self, parent, node):
        if node.is_main:
            self.append('int main() {')
            self.newline()

        self.level += 1

        if node.var_decls is not None:
            self.visit(node, node.var_decls)
            self.newline()

        for s in node.symbols:
            self.ids[s.id_] = s.copy()

        for n in node.nodes:
            self.indent()

            if isinstance(parent, FuncImpl) and isinstance(n, Assign) and parent.id_.value == n.id_.value:
                self.append('return ')
                self.visit(node, n.expr)
            else:
                self.visit(node, n)

            if not isinstance(n, If) and not isinstance(n, While) and not isinstance(n, For):
                self.append(';')

            self.newline()
        self.level -= 1

        if node.is_main:
            self.append('}')

    def visit_Params(self, parent, node):
        for i, p in enumerate(node.params):
            if i > 0:
                self.append(', ')
            self.visit(p, p.type_)
            self.append(' ')
            self.visit(p, p.id_)

    def visit_Args(self, parent, node):
        for i, a in enumerate(node.args):
            if i > 0:
                self.append(', ')
            self.visit(node, a)

    def visit_Elems(self, parent, node):
        for i, e in enumerate(node.elems):
            if i > 0:
                self.append(', ')
            self.visit(node, e)

    def visit_Break(self, parent, node):
        self.append('break')

    def visit_Continue(self, parent, node):
        self.append('continue')

    def visit_Exit(self, parent, node):
        self.append('return')
        if node.expr is not None:
            self.append(' ')
            self.visit(node, node.expr)

    def visit_Type(self, parent, node):
        if node.value == 'integer' or node.value == 'boolean':
            self.append('int')
        elif node.value == 'string':
            self.append('char')
        elif node.value == 'char':
            self.append('char')
        elif node.value == 'real':
            self.append('float')

    def visit_Int(self, parent, node):
        self.append(node.value)

    def visit_Char(self, parent, node):
        self.append(ord(node.value))

    def visit_String(self, parent, node):
        self.append("\"")
        self.append(node.value)
        self.append("\"")

    def visit_Boolean(self, parent, node):
        self.append("1" if node.value == 'true' else "0")

    def visit_Id(self, parent, node):
        self.append(node.value)

    def visit_BinOp(self, parent, node):
        self.append('(')
        self.visit(node, node.first)
        if node.symbol == 'and':
            self.append(' && ')
        elif node.symbol == 'or':
            self.append(' || ')
        elif node.symbol == '/':
            self.append(' / ')
        elif node.symbol == '=':
            self.append(' == ')
        elif node.symbol == 'mod':
            self.append(' % ')
        elif node.symbol == 'div':
            self.append(' / ')
        elif node.symbol == '<>':
            self.append(' != ')
        else:
            self.append(' ')
            self.append(node.symbol)
            self.append(' ')
        self.visit(node, node.second)
        self.append(')')

    def visit_UnOp(self, parent, node):
        if node.symbol == 'not':
            self.append('!')
        elif node.symbol != '&':
            self.append(node.symbol)
        self.visit(node, node.first)

    def generate(self, path):
        self.visit(None, self.ast)
        self.py = re.sub('\n\s*\n', '\n', self.py)
        with open(path, 'w') as source:
            source.write(self.py)
        return path
