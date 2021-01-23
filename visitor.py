class Visitor:
    def visit(self, parent, node):
        method = 'visit_' + type(node).__name__
        visitor = getattr(self, method, self.die)
        return visitor(parent, node)

    def die(self, parent, node):
        method = 'visit_' + type(node).__name__
        raise SystemExit("Missing method: {}".format(method))
