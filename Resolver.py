class Resolver:
    def __init__(self, interpreter, lox_class):
        self.interpeter = interpreter
        self.scopes = []
        self.lox = lox_class
        self.currentFunction = "NONE"
    def visitBlockStmt(self, stmt):
        self.beginScope()
        self.resolve(stmt.statements)
        self.endScope()
        return None
    def visitVarStmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initialiser != None:
            self.resolve(stmt.initialiser)
        self.define(stmt.name)
        return None
    def visitFunctionStmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolveFunction(stmt, "FUNCTION")
        return None
    def visitExpressionStmt(self, stmt):
        self.resolve(stmt.expression)
        return None
    def visitIfStmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenBranch)
        if stmt.elseBranch != None: self.resolve(stmt.elseBranch)
        return None
    def visitPrintStmt(self, stmt):
        self.resolve(stmt.expression)
        return None
    def visitReturnStmt(self, stmt):
        if self.currentFunction == "NONE":
            self.lox.parseError(stmt.keyword, "Can't return from top-level code.")
        if stmt.value != None: self.resolve(stmt.value)
        return None
    def visitWhileStmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)
    def visitVariableExpr(self, expr):
        #print(self.scopes)
        #print(self.scopes[-1])
        try:
            if len(self.scopes) > 0 and not self.scopes[-1][expr.name.lexeme]:
                self.lox.parseError(expr.name, "Can't read local variable in its own initialiser.")
        except:
            pass
        self.resolveLocal(expr, expr.name)
        return None
    def visitBinaryExpr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    def visitCallExpr(self, expr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(argument)
        return None
    def visitGroupingExpr(self, expr):
        self.resolve(expr.expression)
        return None
    def visitLiteralExpr(self, expr):
        return None
    def visitLogicalExpr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)
        return None
    def visitUnaryExpr(self, expr):
        self.resolve(expr.right)
        return None
    def resolve(self, statements):
        if type(statements) == list:
            for statement in statements:
                self.resolve(statement)
        else:
            statements.accept(self)
    def declare(self, name):
        if len(self.scopes) == 0: return
        scope = self.scopes[-1]
        if name.lexeme in scope.keys():
            self.lox.error(name, "Already a variable with this name in this scope.")
        scope[name.lexeme] = False
    def define(self, name):
        if len(self.scopes) == 0: return
        self.scopes[-1][name.lexeme] = True
    def resolveLocal(self, expr, name):
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexeme in self.scopes[i].keys():
                self.interpeter.resolve(expr, len(self.scopes)-1-i)
                return
    def resolveFunction(self, function, type):
        enclosingFunction = self.currentFunction
        self.currentFunction = type
        self.beginScope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.endScope()
        self.currentFunction = enclosingFunction
    def visitAssignExpr(self, expr):
        self.resolve(expr.value)
        self.resolveLocal(expr, expr.name)
        return None
    def beginScope(self):
        self.scopes.append({})
    def endScope(self):
        self.scopes.pop()

functionType = [
    "NONE",
    "FUNCTION"
]
