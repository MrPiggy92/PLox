from Environment import *
from LoxCallable import *
from Return import *

class LoxFunction(LoxCallable):
    def __init__(self, declaration, closure, isInitialiser):
        self.isInitialiser = isInitialiser
        self.declaration = declaration
        self.closure = closure
    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except Return as e:
            if self.isInitialiser: return self.closure.getAt(0, "this")
            return e.value
        if self.isInitialiser: return self.closure.getAt(0, "this")
        return None
    def arity(self):
        return len(self.declaration.params)
    def __repr__(self):
        return f"<fn {self.declaration.name.lexeme}>"
    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.isInitialiser)
