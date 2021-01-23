from visitor import Visitor


class Symbol:
    def __init__(self, id_, type_, scope):
        self.id_ = id_
        self.type_ = type_
        self.scope = scope

    def __str__(self):
        return "<{} {} {}>".format(self.id_, self.type_, self.scope)

    def copy(self):
        return Symbol(self.id_, self.type_, self.scope)


class Symbols:
    def __init__(self):
        self.symbols = {}

    def put(self, id_, type_, scope):
        self.symbols[id_] = Symbol(id_, type_, scope)

    def get(self, id_):
        return self.symbols[id_]

    def contains(self, id_):
        return id_ in self.symbols

    def remove(self, id_):
        del self.symbols[id_]

    def __len__(self):
        return len(self.symbols)

    def __str__(self):
        out = ""
        for _, value in self.symbols.items():
            if len(out) > 0:
                out += "\n"
            out += str(value)
        return out

    def __iter__(self):
        return iter(self.symbols.values())

    def __next__(self):
        return next(self.symbols.values())


class Symbolizer(Visitor):
    def __init__(self, ast):
        self.ast = ast

    def visit_Program(self, parent, node):
        node.symbols = Symbols()
        for n in node.nodes:
            self.visit(node, n)

    def visit_Decl(self, parent, node):
        parent.symbols.put(node.id_.value, node.type_.value, id(parent))

    def visit_ArrayDecl(self, parent, node):
        node.symbols = Symbols()
        parent.symbols.put(node.id_.value, node.type_.value, id(parent))

    def visit_ArrayElem(self, parent, node):
        pass

    def visit_Assign(self, parent, node):
        pass

    def visit_If(self, parent, node):
        self.visit(node, node.true)
        if node.false is not None:
            self.visit(node, node.false)

    def visit_While(self, parent, node):
        self.visit(node, node.block)

    def visit_For(self, parent, node):
        self.visit(node, node.block)

    def visit_RepeatUntil(self, parent, node):
        self.visit(node, node.block)

    def visit_FuncImpl(self, parent, node):
        parent.symbols.put(node.id_.value, node.type_.value, id(parent))
        self.visit(node, node.block)
        self.visit(node, node.params)

    def visit_ProcImpl(self, parent, node):
        parent.symbols.put(node.id_.value, None, id(parent))
        self.visit(node, node.block)
        self.visit(node, node.params)

    def visit_FuncCall(self, parent, node):
        pass

    def visit_ProcCall(self, parent, node):
        pass

    def visit_Block(self, parent, node):
        if node.is_main:
            parent.symbols.put('main', '', id(parent))
        node.symbols = Symbols()
        if node.var_decls is not None:
            self.visit(node, node.var_decls)
        for n in node.nodes:
            self.visit(node, n)

    def visit_VarDecl(self, parent, node):
        for n in node.decls:
            self.visit(parent, n)

    def visit_Params(self, parent, node):
        node.symbols = Symbols()
        for p in node.params:
            self.visit(node, p)
            self.visit(parent.block, p)

    def visit_Args(self, parent, node):
        pass

    def visit_Elems(self, parent, node):
        pass

    def visit_Break(self, parent, node):
        pass

    def visit_Continue(self, parent, node):
        pass

    def visit_Exit(self, parent, node):
        pass

    def visit_Type(self, parent, node):
        pass

    def visit_Int(self, parent, node):
        pass

    def visit_Char(self, parent, node):
        pass

    def visit_String(self, parent, node):
        pass

    def visit_Real(self, parent, node):
        pass

    def visit_Boolean(self, parent, node):
        pass

    def visit_Id(self, parent, node):
        pass

    def visit_BinOp(self, parent, node):
        pass

    def visit_UnOp(self, parent, node):
        pass

    def symbolize(self):
        self.visit(None, self.ast)
