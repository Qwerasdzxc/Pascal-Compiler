from parser import Id, Int, Real, Char, String, Boolean, ArrayElem, BinOp, Break, Continue, Exit
from symbolizer import Symbol
from visitor import Visitor


class Runner(Visitor):
    def __init__(self, ast):
        self.ast = ast
        self.global_ = {}
        self.local = {}
        self.scope = {}
        self.call_stack = []
        self.search_new_call = True
        self.return_ = False
        self.input_picked = False

    def get_symbol(self, node):
        recursion = self.is_recursion()
        ref_call = -2 if not self.search_new_call else -1
        ref_scope = -2 if recursion and not self.search_new_call else -1
        id_ = node.value
        if len(self.call_stack) > 0:
            fun = self.call_stack[ref_call]
            for scope in reversed(self.scope[fun]):
                if scope in self.local:
                    curr_scope = self.local[scope][ref_scope]
                    if id_ in curr_scope:
                        return curr_scope[id_]
        return self.global_[id_]

    def init_scope(self, node):
        fun = self.call_stack[-1]
        if fun not in self.scope:
            self.scope[fun] = []
        scope = id(node)
        if scope not in self.local:
            self.local[scope] = []
        self.local[scope].append({})
        for s in node.symbols:
            self.local[scope][-1][s.id_] = s.copy()

    def clear_scope(self, node):
        scope = id(node)
        self.local[scope].pop()

    def is_recursion(self):
        if len(self.call_stack) > 0:
            curr_call = self.call_stack[-1]
            prev_calls = self.call_stack[:-1]
            for call in reversed(prev_calls):
                if call == curr_call:
                    return True
        return False

    def visit_Program(self, parent, node):
        for s in node.symbols:
            self.global_[s.id_] = s.copy()
        for n in node.nodes:
            self.visit(node, n)

    def visit_Decl(self, parent, node):
        id_ = self.get_symbol(node.id_)
        id_.value = None

    def visit_VarDecl(self, parent, node):
        for decl in node.decls:
            self.visit(node, decl)

    def visit_ArrayDecl(self, parent, node):
        id_ = self.get_symbol(node.id_)
        id_.symbols = node.symbols
        size, elems = node.size, node.elems
        if elems is not None:
            self.visit(node, elems)
        else:
            if size is None:
                size = node.to_.value - node.from_.value + 2

            for i in range(size):
                id_.symbols.put(i, id_.type_, None)
                id_.symbols.get(i).value = None

    def visit_ArrayElem(self, parent, node):
        id_ = self.get_symbol(node.id_)
        index = self.visit(node, node.index)
        return id_.symbols.get(index.value)

    def visit_Assign(self, parent, node):
        id_ = self.visit(node, node.id_)
        value = self.visit(node, node.expr)
        if isinstance(value, Symbol):
            value = value.value
        id_.value = value

    def visit_If(self, parent, node):
        cond = self.visit(node, node.cond)
        if isinstance(cond, Symbol):
            cond = cond.value

        if cond:
            self.init_scope(node.true)
            result = self.visit(node, node.true)
            self.clear_scope(node.true)
            return result
        else:
            if node.false is not None:
                self.init_scope(node.false)
                result = self.visit(node, node.false)
                self.clear_scope(node.false)
                return result

    def visit_While(self, parent, node):
        cond = self.visit(node, node.cond)
        while cond:
            self.init_scope(node.block)
            self.visit(node, node.block)
            self.clear_scope(node.block)
            cond = self.visit(node, node.cond)

    def visit_RepeatUntil(self, parent, node):
        while True:
            self.init_scope(node.block)
            self.visit(node, node.block)
            self.clear_scope(node.block)

            cond = self.visit(node, node.cond)
            if cond or self.return_:
                self.return_ = False
                break

    def visit_For(self, parent, node):
        result = None
        self.visit(node, node.init)

        if isinstance(node.to, Id):
            to = self.get_symbol(node.to).value
        else:
            to = self.visit(node, node.to)

        if not node.reversed:
            cond = self.get_symbol(node.init.id_).value <= to
        else:
            cond = self.get_symbol(node.init.id_).value >= to

        while cond and not self.return_ and not self.input_picked:
            self.init_scope(node.block)
            result = self.visit(node, node.block)
            self.clear_scope(node.block)

            if result is not None:
                break

            if isinstance(node.to, Id):
                to = self.get_symbol(node.to).value
            else:
                to = self.visit(node, node.to)
            if not node.reversed:
                cond = self.get_symbol(node.init.id_).value < to
                self.get_symbol(node.init.id_).value += 1
            else:
                cond = self.get_symbol(node.init.id_).value > to
                self.get_symbol(node.init.id_).value -= 1

        self.input_picked = False
        return result

    def visit_FuncImpl(self, parent, node):
        id_ = self.get_symbol(node.id_)
        id_.params = node.params
        id_.block = node.block

    def visit_ProcImpl(self, parent, node):
        id_ = self.get_symbol(node.id_)
        id_.params = node.params
        id_.block = node.block

    def visit_FuncCall(self, parent, node):
        func = node.id_.value
        args = node.args.args
        if func == 'write' or func == 'writeln':
            output = ""
            for a in args[0:]:
                if isinstance(a, Int):
                    output += a.value
                elif isinstance(a, Real):
                    output += a.value
                elif isinstance(a, Boolean):
                    output += a.value
                elif isinstance(a, Char):
                    output += a.value
                elif isinstance(a, String):
                    output += a.value
                elif isinstance(a, Id) or isinstance(a, ArrayElem):
                    id_ = self.visit(node.args, a)
                    if hasattr(id_, 'symbols') and id_.type_ == 'char':
                        elems = id_.symbols
                        ints = [s.value for s in elems]
                        non_nulls = [i for i in ints if i is not None]
                        chars = [chr(i) for i in non_nulls]
                        value = ''.join(chars)
                    else:
                        value = id_.value
                        if id_.type_ == 'char':
                            value = chr(value)
                    output += str(value)
                else:
                    value = self.visit(node.args, a)
                    if isinstance(a, BinOp) and a.roundings is not None:
                        format = "{:." + str(a.roundings[1].value) + "f}"
                        output += format.format(value)
                    else:
                        output += str(value)
            print(output, end=('' if func == 'write' else '\n'))
        elif func == 'read':
            inputs = input().split()
            symbol = self.get_symbol(args[0].id_)
            for i, a in enumerate(inputs):
                element = symbol.symbols.symbols[i + 1]
                type_ = element.type_
                if type_ == 'integer':
                    element.value = int(inputs[i])
                elif type_ == 'real':
                    element.value = float(inputs[i])
                elif type_ == 'char':
                    element.value = ord(inputs[i][0])
            self.input_picked = True
        elif func == 'readln':
            inputs = input().split()
            for i, a in enumerate(args):
                id_ = self.visit(node.args, args[i])
                symbol = self.get_symbol(a)
                type_ = symbol.type_
                if type_ == 'integer':
                    id_.value = int(inputs[i])
                elif type_ == 'real':
                    id_.value = float(inputs[i])
                elif type_ == 'char':
                    id_.value = ord(inputs[i][0])
                elif type_ == 'string':
                    word = inputs[i]
                    length = len(id_.symbols)
                    for c in word:
                        id_.symbols.put(length, id_.type_, None)
                        id_.symbols.get(length).value = ord(c)
                        length += 1
        elif func == 'chr':
            a = args[0]
            if isinstance(a, Int):
                return chr(a.value)
            n = self.visit(node.args, a)
            if isinstance(n, Symbol):
                return chr(n.value)
            return chr(n)
        elif func == 'ord':
            a = args[0]
            if isinstance(a, Char):
                return ord(a.value)

            id_ = self.visit(node.args, a)
            return id_.value
        elif func == 'strlen':
            a = args[0]
            if isinstance(a, String):
                return len(a.value)
            elif isinstance(a, Id):
                id_ = self.visit(node.args, a)
                return len(id_.symbols)
        elif func == 'strcat':
            a, b = args[0], args[1]
            dest = self.get_symbol(a)
            values = []
            if isinstance(b, Id):
                src = self.get_symbol(b)
                elems = [s.value for s in src.symbols]
                non_nulls = [c for c in elems if c is not None]
                values = [c for c in non_nulls]
            elif isinstance(b, String):
                values = [ord(c) for c in b.value]
            i = len(dest.symbols)
            for v in values:
                dest.symbols.put(i, dest.type_, None)
                dest.symbols.get(i).value = v
                i += 1
        else:
            impl = self.global_[func]
            self.call_stack.append(func)
            self.init_scope(impl.block)
            self.visit(node, node.args)
            result = self.visit(node, impl.block)
            self.clear_scope(impl.block)
            self.call_stack.pop()
            self.return_ = False
            return result

    def visit_Block(self, parent, node):
        if node.is_main:
            self.call_stack.append('main')
            self.init_scope(node)

        result = None
        scope = id(node)
        fun = self.call_stack[-1]
        self.scope[fun].append(scope)

        if node.var_decls is not None:
            self.visit(node, node.var_decls)

        if len(self.local[scope]) > 5:
            exit(0)

        for n in node.nodes:
            if self.return_:
                break
            if isinstance(n, Break):
                self.return_ = True
                break
            elif isinstance(n, Continue):
                continue
            elif isinstance(n, Exit):
                self.return_ = True
                if n.expr is not None:
                    result = self.visit(n, n.expr)
                break
            else:
                result = self.visit(node, n)

        self.scope[fun].pop()

        if node.is_main:
            self.clear_scope(node)
            self.call_stack.pop()

        return result

    def visit_Params(self, parent, node):
        pass

    def visit_Args(self, parent, node):
        fun_parent = self.call_stack[-2]
        impl = self.global_[fun_parent]
        self.search_new_call = False

        if fun_parent is 'main':
            args = [self.visit(impl, a) for a in node.args]
        else:
            args = [self.visit(impl.block, a) for a in node.args]

        args = [a.value if isinstance(a, Symbol) else a for a in args]
        fun_child = self.call_stack[-1]
        impl = self.global_[fun_child]
        scope = id(impl.block)
        self.scope[fun_child].append(scope)
        self.search_new_call = True
        for p, a in zip(impl.params.params, args):
            id_ = self.visit(impl.block, p.id_)
            id_.value = a
        self.scope[fun_child].pop()

    def visit_Elems(self, parent, node):
        id_ = self.get_symbol(parent.id_)
        for i, e in enumerate(node.elems):
            value = self.visit(node, e)
            id_.symbols.put(i, id_.type_, None)
            id_.symbols.get(i).value = value

    def visit_Break(self, parent, node):
        pass

    def visit_Continue(self, parent, node):
        pass

    def visit_Exit(self, parent, node):
        pass

    def visit_Type(self, parent, node):
        pass

    def visit_Int(self, parent, node):
        return node.value

    def visit_Char(self, parent, node):
        return ord(node.value)

    def visit_String(self, parent, node):
        return node.value

    def visit_Real(self, parent, node):
        return node.value

    def visit_Boolean(self, parent, node):
        return node.value == 'true'

    def visit_Id(self, parent, node):
        return self.get_symbol(node)

    def visit_BinOp(self, parent, node):
        first = self.visit(node, node.first)
        if isinstance(first, Symbol):
            first = first.value
        second = self.visit(node, node.second)
        if isinstance(second, Symbol):
            second = second.value
        if node.symbol == '+':
            return first + second
        elif node.symbol == '-':
            return first - second
        elif node.symbol == '*':
            return first * second
        elif node.symbol == '/':
            return first / second
        elif node.symbol == 'div':
            return int(first) // int(second)
        elif node.symbol == 'mod':
            return first % second
        elif node.symbol == '=':
            return first == second
        elif node.symbol == '<>':
            return first != second
        elif node.symbol == '<':
            return first < second
        elif node.symbol == '>':
            return first > second
        elif node.symbol == '<=':
            return first <= second
        elif node.symbol == '>=':
            return first >= second
        elif node.symbol == 'and':
            bool_first = first != 0
            bool_second = second != 0
            return bool_first and bool_second
        elif node.symbol == 'or':
            bool_first = first != 0
            bool_second = second != 0
            return bool_first or bool_second
        else:
            return None

    def visit_UnOp(self, parent, node):
        first = self.visit(node, node.first)
        if isinstance(first, Symbol):
            first = first.value
        if node.symbol == '-':
            return -first
        elif node.symbol == 'not':
            bool_first = first != 0
            return not bool_first
        else:
            return None

    def run(self):
        self.visit(None, self.ast)