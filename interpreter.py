from parse_tree import Parser


class Interpreter:
    """ Interpreter """

    def __init__(self, program):
        self.tree = Parser(program).parse()
        self.temp = []
        self.var_list = {}
        self.func_list = {}

    def eval(self, statement):
        if type(statement) == list:
            for i in statement:
                self.eval(i)
        elif statement.id == "NUMBER":
            return statement.value
        elif statement.id == "STRING":
            return statement.value
        elif statement.id == "BOOL":
            return statement.value
        elif statement.id == "+":
            return self.eval(statement.first) + self.eval(statement.second)
        elif statement.id == "-":
            return self.eval(statement.first) - self.eval(statement.second)
        elif statement.id == "*":
            return self.eval(statement.first) * self.eval(statement.second)
        elif statement.id == "/":
            return self.eval(statement.first) / self.eval(statement.second)
        elif statement.id == "<":
            return self.eval(statement.first) < self.eval(statement.second)
        elif statement.id == "&":
            return self.eval(statement.first) and self.eval(statement.second)
        elif statement.id == "|":
            return self.eval(statement.first) or self.eval(statement.second)
        elif statement.id == ">":
            return self.eval(statement.first) > self.eval(statement.second)
        elif statement.id == "==":
            return self.eval(statement.first) == self.eval(statement.second)
        elif statement.id == "::":
            vals = statement.second
            params = self.func_list[statement.first.value]["args"]
            vals_list = []
            params_list = []

            def traverse(root, vlist):
                if root:
                    traverse(root.first, vlist)
                    if root.value:
                        vlist.append(root)
                    traverse(root.second, vlist)

            traverse(vals, vals_list)
            traverse(params, params_list)
            for i in range(len(params_list)):
                self.var_list[params_list[i].value] = self.eval(vals_list[i])
            self.eval(self.func_list[statement.first.value]["body"])
        elif statement.id == "if":
            if (
                type(self.eval(statement.first)) == int
                and self.eval(statement.first) != 0
            ):
                self.eval(statement.second)
            elif self.eval(statement.first) == True:
                return self.eval(statement.second)
            else:
                return None
        elif statement.id == "while":
            while self.eval(statement.first) == True:
                self.eval(statement.second)
        elif statement.id == "fn":
            self.func_list[statement.first.value] = {
                "args": statement.second,
                "body": statement.third,
            }
        elif statement.id == "let":
            self.var_list[statement.first.first.value] = self.eval(
                statement.first.second
            )
        elif statement.id == "NAME":
            return self.var_list[statement.value]
        elif statement.id == "print":
            print(str(self.eval(statement.first)))
        elif statement.id == "=":
            self.var_list[statement.first.value] = self.eval(statement.second)
        else:
            print("Got it")

    def interpret(self, tree=None):
        if tree:
            for stmt in tree:
                return self.eval(stmt)
        else:
            for stmt in self.tree:
                self.temp.append(self.eval(stmt))
            return self.temp


if __name__ == "__main__":

    import sys

    def source_read():
        if len(sys.argv) > 1:
            with open(sys.argv[1]) as ff:
                data = ff.read()
                return data
        else:
            print("Usage: niko [source]")
            sys.exit()

    i = Interpreter(source_read())

    i.interpret()
