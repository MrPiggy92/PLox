class Block:
    def __init__(self, statements):
        self.statements = statements
    def accept(self, visitor):
        return visitor.visitBlockStmt(self)
class Expression:
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visitExpressionStmt(self)
class If:
    def __init__(self, condition, thenBranch, elseBranch):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch
    def accept(self, visitor):
        return visitor.visitIfStmt(self)
class Print:
    def __init__(self, expression):
        self.expression = expression
    def accept(self, visitor):
        return visitor.visitPrintStmt(self)
class Var:
    def __init__(self, name, initialiser):
        self.name = name
        self.initialiser = initialiser
    def accept(self, visitor):
        return visitor.visitVarStmt(self)
class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def accept(self, visitor):
        return visitor.visitWhileStmt(self)
