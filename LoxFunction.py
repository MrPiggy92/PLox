from Environment import *
from LoxCallable import *
from Return import *

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as e:
            return e.value
        return None
    def arity(self):
        return len(self.declaration.params)
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
