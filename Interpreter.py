from LoxRuntimeError import *
from Environment import *
from LoxCallable import *
from LoxFunction import *
from Return import *
import time

class Clock(LoxCallable):
    def arity(self): return 0
    def call(self, interpeter, arguments):
        return time.time()
    def __repr__(self):
        return "<native fn clock>"
class Input(LoxCallable):
    def arity(self): return 1
    def call(self, interpreter, arguments):
        return input(arguments[0])
    def __repr__(self):
        return "<native fn input>"
class Print(LoxCallable):
    def arity(self): return 1
    def call(self, interpreter, arguments):
        print(arguments[0])
        return arguments[0]
    def __repr__(self):
        return "<native fn print>"
class Interpreter:
    def __init__(self, lox):
        self.lox_class = lox
        self.globals = Environment()
        self.environment = self.globals
        self.globals.define("clock", Clock())
        self.globals.define("input", Input())
        self.globals.define("print", Print())
        self.locals = {}
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
        return self.lookUpVariable(expr.name, expr)
    def lookUpVariable(self, name, expr):
        try:
            distance = self.locals[expr]
            return self.environment.getAt(distance, name.lexeme)
        except:
            return self.globals.get(name)
    def visitAssignExpr(self, expr):
        value = self.evaluate(expr.value)
        try:
            distance = self.locals[expr]
            self.environment.assignAt(distance, expr.name, value)
        except:
            self.globals.assign(expr.name, value)
        return value
    def visitLogicalExpr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.type == "OR":
            if self.isTruthy(left): return left
        else:
            if not self.isTruthy(left): return left
        return self.evaluate(expr.right)
    def visitCallExpr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        function = LoxCallable(callee) # Callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)
    def visitExpressionStmt(self, stmt):
        self.evaluate(stmt.expression)
        return None
    def visitFunctionStmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None
    def visitReturnStmt(self, stmt):
        value = None
        if stmt.value != None:
            value = self.evaluate(stmt.value)
        raise Return(value)
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
    def resolve(self, expr, depth):
        self.locals[expr] = depth
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
