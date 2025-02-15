from Expr import *
from Stmt import *

class Parser:
    def __init__(self, tokens, lox):
        self.tokens = tokens
        self.current = 0
        self.lox_class = lox
    def parse(self):
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        return statements
    def declaration(self):
        try:
            if self.match("VAR"): return self.varDeclaration()
            elif self.match("FUN"): return self.function("function")
            elif self.match("CLASS"): return self.classDeclaration()
            return self.statement()
        except ParseError:
            self.synchronise()
            return None
    def varDeclaration(self):
        name = self.consume("IDENTIFIER", "Expect variable name.")
        initialiser = None
        if self.match("EQUAL"):
            initialiser = self.expression()
        self.consume("SEMICOLON", "Expect ';' after variable declaration.")
        return Var(name, initialiser)
    def classDeclaration(self):
        name = self.consume("IDENTIFIER", "Expect class name.")
        superclass = None
        if self.match("LESS"):
            self.consume("IDENTIFIER", "Expect superclass name.")
            superclass = Variable(self.previous())
        self.consume("LEFT_BRACE", "Expect '{' before class body")
        methods = []
        while not(self.check("RIGHT_BRACE")) and not(self.isAtEnd()):
            methods.append(self.function("method"))
        self.consume("RIGHT_BRACE", "Expect '}' after class body")
        return Class(name, superclass, methods)
    def statement(self):
        if self.match("PRINT"): return self.printStatement()
        elif self.match("IF"): return self.ifStatement()
        elif self.match("WHILE"): return self.whileStatement()
        elif self.match("FOR"): return self.forStatement()
        elif self.match("LEFT_BRACE"): return Block(self.block())
        elif self.match("RETURN"): return self.returnStatement()
        return self.expressionStatement()
    def printStatement(self):
        value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Print(value)
    def ifStatement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after if condition.")
        thenBranch = self.statement()
        elseBranch = None
        if self.match("ELSE"):
            elseBranch = self.statement()
        return If(condition, thenBranch, elseBranch)
    def whileStatement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume("RIGHT_PAREN", "Expect ')' after while condition.")
        body = self.statement()
        return While(condition, body)
    def forStatement(self):
        self.consume("LEFT_PAREN", "Expect '(' after 'for'.")
        if self.match("SEMICOLON"):
            initialiser = None
        elif self.match("VAR"):
            initialiser = self.varDeclaration()
        else:
            initialiser = self.expressionStatement()
        if not self.check("SEMICOLON"):
            condition = self.expression()
        else:
            condition = None
        self.consume("SEMICOLON", "Expect ';' after loop condition.")
        if not self.check("RIGHT_PAREN"):
            increment = self.expression()
        else:
            increment = None
        self.consume("RIGHT_PAREN", "Expect ')' after for clauses.")
        body = self.statement()
        if increment != None:
            body = Block([body, Expression(increment)])
        if condition == None: condition = Literal(True)
        body = While(condition, body)
        if initialiser != None:
            body = Block([initialiser, body])
        return body
    def returnStatement(self):
        keyword = self.previous()
        value = None
        if not self.check("SEMICOLON"):
            value = self.expression()
        self.consume("SEMICOLON", "Expect ';' after return value.")
        return Return(keyword, value)
    def expressionStatement(self):
        expr = self.expression()
        self.consume("SEMICOLON", "Expect ';' after value.")
        return Expression(expr)
    def function(self, kind):
        name = self.consume("IDENTIFIER", f"Expect {kind} name.")
        self.consume("LEFT_PAREN", f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check("RIGHT_PAREN"):
            parameters.append(self.consume("IDENTIFIER", "Expect paramter name."))
            while self.match("COMMA"):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 paramaters.")
                parameters.append(self.consume("IDENTIFIER", "Expect paramter name."))
        self.consume("RIGHT_PAREN", "Expect ')' after parameters.")
        self.consume("LEFT_BRACE", "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name, parameters, body)
    def block(self):
        statements = []
        while (not self.check("RIGHT_BRACE")) and (not self.isAtEnd()):
            statements.append(self.declaration())
        self.consume("RIGHT_BRACE", "Expect '}' after block.")
        return statements
    def assignment(self):
        expr = self.logicalOr()
        #print(expr)
        #print(self.peek())
        if self.match("EQUAL"):
            equals = self.previous()
            value = self.assignment()
            if type(expr) == Variable:
                name = expr.name
                return Assign(name, value)
            elif type(expr) == Get:
                get = expr
                return Set(get.object, get.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr
    def logicalOr(self):
        expr = self.logicalAnd()
        while self.match("OR"):
            operator = self.previous()
            right = self.logicalAnd()
            expr = Logical(expr, operator, right)
        return expr
    def logicalAnd(self):
        expr = self.equality()
        while self.match("AND"):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        return expr
    def expression(self):
        return self.assignment()
    def equality(self):
        expr = self.comparison()
        while self.match("BANG_EQUAL", "EQUAL_EQUAL"):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr
    def comparison(self):
        expr = self.mod()
        while self.match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self.previous()
            right = self.mod()
            expr = Binary(expr, operator, right)
        return expr
    def mod(self):
        expr = self.term()
        while self.match("MODULO"):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr
    def term(self):
        expr = self.factor()
        while self.match("MINUS", "PLUS"):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    def factor(self):
        expr = self.unary()
        while self.match("STAR", "SLASH"):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    def unary(self):
        if self.match("BANG", "MINUS"):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()
    def call(self):
        expr = self.primary()
        while True:
            if self.match("LEFT_PAREN"):
                expr = self.finishCall(expr)
            elif self.match("DOT"):
                name = self.consume("IDENTIFIER", "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr
    def primary(self):
        if self.match("TRUE"): return Literal(True)
        elif self.match("FALSE"): return Literal(False)
        elif self.match("NIL"): return Literal(None)
        elif self.match("NUMBER", "STRING"):
            return Literal(self.previous().literal)
        elif self.match("SUPER"):
            keyword = self.previous()
            self.consume("DOT", "Expect '.' after 'super'.")
            method = self.consume("IDENTIFIER", "Expect superclass method name.")
            return Super(keyword, method)
        elif self.match("THIS"):
            return This(self.previous())
        elif self.match("IDENTIFIER"):
            return Variable(self.previous())
        elif self.match("LEFT_PAREN"):
            expr = self.expression()
            self.consume("RIGHT_PAREN", "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")
    def finishCall(self, callee):
        arguments = []
        if not self.check("RIGHT_PAREN"):
            arguments.append(self.expression())
            while self.match("COMMA"):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
        paren = self.consume("RIGHT_PAREN", "Expect ')' after arguments")
        return Call(callee, paren, arguments)
    def match(self, *args):
        for type in args:
            if self.check(type):
                self.advance()
                return True
        return False
    def check(self, type):
        if self.isAtEnd(): return False
        return self.peek().type == type
    def isAtEnd(self):
        return self.peek().type == "EOF"
    def peek(self):
        return self.tokens[self.current]
    def advance(self):
        if not self.isAtEnd(): self.current += 1
        return self.previous()
    def previous(self):
        return self.tokens[self.current-1]
    def consume(self, token, message):
        if self.check(token): return self.advance()
        self.error(self.peek(), message)
        raise self.error(self.peek(), message)
    def error(self, token, message):
        self.lox_class.parseError(token, message)
        return ParseError()
    def synchronise(self):
        self.advance()
        while not self.isAtEnd():
            if self.previous().type == "SEMICOLON": return
            nextType = self.peek().type
            if nextType in ["CLASS", "FUN", "VAR", "FOR", "IF", "WHILE", "PRINT", "RETURN"]:
                return
            self.advance()
class ParseError(RuntimeError):
    pass
