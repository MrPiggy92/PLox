import sys

class GenerateAst:
    def main(self):
        if len(sys.argv) != 2:
            print("Usage: python3 GenerateAst_tool.py <output directory>")
            exit(64)
        outputDir = sys.argv[1]
        #outputDir = ""
        self.defineAst(outputDir, "Expr", [
        "Assign   : name, value",
        "Binary   : left, operator, right",
        "Call     : callee, paren, arguments",
        "Get      : object, name",
        "Grouping : expression",
        "Literal  : value",
        "Logical  : left, operator, right",
        "Set      : object, name, value",
        "Super    : keyword, method",
        "This     : keyword",
        "Unary    : operator, right",
        "Variable : name"
        ])
        self.defineAst(outputDir, "Stmt", [
        "Block      : statements",
        "Class      : name, superclass, methods",
        "Expression : expression",
        "Function   : name, params, body",
        "If         : condition, thenBranch, elseBranch",
        "Print      : expression",
        "Return     : keyword, value",
        "Var        : name, initialiser",
        "While      : condition, body"
        ])
    def defineAst(self, outputDir, baseName, types):
        path = outputDir + '/' + baseName + ".py"
        #textToWrite = self.defineVisitor(baseName, types)
        #textToWrite = textToWrite[:-8]
        textToWrite = ''
        for type in types:
            className = type.split(':')[0].strip()
            fields = type.split(':')[1].strip()
            textToWrite += self.defineType(baseName, className, fields)
            textToWrite += f"""    def accept(self, visitor):
        return visitor.visit{className}{baseName}(self)
"""
        #print(textToWrite)
        with open(path, 'w') as file:
            file.write(textToWrite)
    def defineType(self, baseName, className, fieldList):
        text = f"""class {className}:
    def __init__(self, {fieldList}):
"""
        fields = fieldList.split(', ')
        for field in fields:
            text += f"        self.{field} = {field}\n"
        #print(text)
        return text
    def defineExpr(self, baseName, types):
        text = """    class Expr:
        """
        for type in types:
            typeName = type.split(':')[0].strip()
            text += f"""def visit{typeName}(self, {typeName}):
            pass
        """
        return text
a = GenerateAst()
a.main()
