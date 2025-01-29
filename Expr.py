class Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def accept(self, visitor):
        return visitor.visitAssignExpr(self)
class Binary:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visitBinaryExpr(self)
class Call:
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    def accept(self, visitor):
        return visitor.visitCallExpr(self)
class Grouping:
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visitGroupingExpr(self)
class Literal:
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        return visitor.visitLiteralExpr(self)
class Logical:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visitLogicalExpr(self)
class Unary:
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    def accept(self, visitor):
        return visitor.visitUnaryExpr(self)
class Variable:
    def __init__(self, name):
        self.name = name
    def accept(self, visitor):
        return visitor.visitVariableExpr(self)
