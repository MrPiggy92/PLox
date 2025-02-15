import sys
if __name__ == "__main__":
    from Scanner import *
    from parser import *
    from Interpreter import *
    from Resolver import *

class Lox:
    def __init__(self):
        self.hadError = False
        self.hadRuntimeError = False
        self.interpreter = Interpreter(self)
    def main(self):
        if len(sys.argv) > 2:
            print("Usage: python3 plox.py [script]")
            exit(64)
        elif len(sys.argv) == 2:
            self.runFile(sys.argv[1])
        else:
            self.runPrompt()
    def runFile(self, path):
        with open(path) as file:
            code = file.read()
        self.run(code)
        if self.hadError: exit(65)
        if self.hadRuntimeError: exit(70)
    def runPrompt(self):
        while True:
            line = input(" > ").strip()
            if line == None: break
            self.run(line)
            self.hadError = False
    def run(self, source):
        try:
            scanner = Scanner(source, self)
            tokens = scanner.scanTokens()
            parser = Parser(tokens, self)
            statements = parser.parse()
            if self.hadError: return
            resolver = Resolver(self.interpreter, self)
            resolver.resolve(statements)
            if self.hadError: return
            self.interpreter.interpret(statements)
        except KeyboardInterrupt:
            print("Cancel")
            self.hadError = True
            return
        #print(expr)
        #for token in tokens:
        #    print(token)
    def error(self, line, message):
        self.report(line, '', message)
    def parseError(self, token, message):
        if token.type == "EOF": 
            self.report(token.line, "at end", message)
        else:
            self.report(token.line, f"at '{token.lexeme}'", message)
    def report(self, line, where, message):
        print(f"[line {line}] Error{(' ' + where) if where != '' else where}: {message}")
        self.hadError = True
    def runtimeError(self, e):
        print(f"[line {e.token.line}] {str(e.args[1])}")
        self.hadRuntimeError = True
lox = Lox()
lox.main()
