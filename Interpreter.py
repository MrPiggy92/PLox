from LoxRuntimeError import *
from Environment import *

class Interpreter:
    def __init__(self, lox):
        self.lox_class = lox
        self.environment = Environment()
    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            self.lox_class.runtimeError(e)
    def visitLiteralExpr(self, expr):
        return expr.value
    def visitGroupingExpr(self, expr):
        return self.evaluate(expr.expression)
    def visitUnaryExpr(self, expr):
        right = self.evaluate(expr.right)
        if expr.operator.type == "MINUS":
            self.checkNumberOperand(expr.operator, right)
            return -float(right)
        elif expr.operator.type == "BANG":
            return not self.isTruthy(right.value)
    def visitBinaryExpr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        if expr.operator.type == "GREATER":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) > float(right)
        elif expr.operator.type == "GREATER_EQUAL":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) >= float(right)
        elif expr.operator.type == "LESS":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) < float(right)
        elif expr.operator.type == "LESS_EQUAL":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) <= float(right)
        elif expr.operator.type == "EQUAL_EQUAL":
            self.checkNumberOperands(expr.operator, left, right)
            return self.isEqual(left, right)
        elif expr.operator.type == "BANG_EQUAL":
            self.checkNumberOperands(expr.operator, left, right)
            return not self.isEqual(left, right)
        elif expr.operator.type == "MINUS":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) - float(right)
        elif expr.operator.type == "SLASH":
            self.checkNumberOperands(expr.operator, left, right)
            if right == 0:
                raise LoxRuntimeError(expr.operator, "You can't divide by 0")
            return float(left) / float(right)
        elif expr.operator.type == "STAR":
            self.checkNumberOperands(expr.operator, left, right)
            return float(left) * float(right)
        elif expr.operator.type == "PLUS":
            if type(left) == float and type(right) == float:
                return float(left) + float(right)
            elif type(left) == str and type(right) == str:
                return str(left) + str(right)
            raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strigns.")
        return None
    def visitVariableExpr(self, expr):
        return self.environment.get(expr.name)
    def visitAssignExpr(self, expr):
        value = self.evaluate(expr.value)
        #print(value)
        self.environment.assign(expr.name, value)
        #print(self.environment.values)
        return value
    def visitLogicalExpr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.type == "OR":
            if self.isTruthy(left): return left
        else:
            if not self.isTruthy(left): return left
        return self.evaluate(expr.right)
    def visitExpressionStmt(self, stmt):
        self.evaluate(stmt.expression)
        return None
    def visitPrintStmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None
    def visitVarStmt(self, stmt):
        value = None
        if stmt.initialiser != None:
            value = self.evaluate(stmt.initialiser)
        self.environment.define(stmt.name.lexeme, value)
        return None
    def visitBlockStmt(self, stmt):
        self.executeBlock(stmt.statements, Environment(self.environment))
        return None
    def visitIfStmt(self, stmt):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)
        return None
    def visitWhileStmt(self, stmt):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None
    def executeBlock(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    def execute(self, stmt):
        stmt.accept(self)
    def evaluate(self, expr):
        return expr.accept(self)
    def isTruthy(self, value):
        if value == None: return False
        elif type(value) == bool: return bool(value)
        elif value == 0: return False
        return True
    def isEqual(self, a, b):
        if a == None and b == None: return True
        if a == None: return False
        return a == b
    def checkNumberOperand(self, operator, operand):
        if type(operand) == float: return
        raise LoxRuntimeError(operator, "Operand should be a number.")
    def checkNumberOperands(self, operator, left, right):
        if type(left) == type(right) == float: return
        raise LoxRuntimeError(operator, "Operands must be numbers.")
    def stringify(self, value):
        if value == None: return "nil"
        if type(value) == float:
            text = str(value)
            if text[-2:] == ".0":
                text = text[:-2]
            return text
        return str(value)
