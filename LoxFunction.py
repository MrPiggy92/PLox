from Environment import *
from LoxCallable import *

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration
    def call(self, interpreter, arguments):
        environment = Environment(interpreter.globals)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        interpreter.executeBlock(self.declaration.body, environment)
        return None
    def arity(self):
        return len(self.declaration.params)
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
