from LoxRuntimeError import *

class Environment:
    def __init__(self, *args):
        if len(args) > 0:
            self.enclosing = args[0]
        else:
            self.enclosing = None
        self.values = {}
    def define(self, name, value):
        self.values[name] = value
    def get(self, name):
        if name.lexeme in self.values.keys():
            return self.values[name.lexeme]
        elif self.enclosing != None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    def assign(self, name, value):
        #print(f"Assigning value {str(value)} to variable {name}")
        if name.lexeme in self.values.keys():
            #print("found")
            self.values[name.lexeme] = value
            #print(self.values[name.lexeme])
            return
        elif self.enclosing != None:
            self.enclosing.assign(name, value)
            return
        #print(self.values[name.lexeme])
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
