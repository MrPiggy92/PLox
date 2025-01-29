from LoxRuntimeError import *
class Return(LoxRuntimeError):
    def __init__(self, value):
        self.value = value
