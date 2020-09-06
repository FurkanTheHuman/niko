import re
import sys
from lexer import Lexer
from queue import Queue


class ParseError(Exception):
    pass


class BaseSymbol:

    id = value = parent = None
    first = second = third = None  # Tree leafs
    stmt_begin = False

    def nud(self):
        enum_source = ""
        for i, code in enumerate(self.parent.program.split("\n")):
            enum_source += str(i + 1) + ": " + code + "\n"
        raise ParseError(
            f"Parse error \nSource Code: \n\n{enum_source} \n TokenID: {self.id} \n line: {self.parent.line}"
        )

    def led(self, left):
        raise ParseError("Unknown operator (%r)" % self.id)

    def __repr__(self):
        """
        FOR DEBUG:
        You can print the AST with this.
        example: `python3 parse_tree.py test-code/math.py`
        """
        if self.id in ["NAME", "NUMBER", "FLOAT", "STRING", "BOOL"]:
            return "(%s %s)" % (self.id, self.value)
        out = [self.id, self.first, self.second, self.third]
        return "\n      (" + " ".join(map(str, filter(None, out))) + ")"

class Parser:
    def __init__(self, program):
        self.sym = {}
        self._generate_symbols()
        self.program = program
        self._var_list = {}
        self.token_gen = self.tokenize(self.program)
        self.token = next(self.token_gen)
        self.line = 1
        self.func_tree = {} # holds defined functions

    def symbol_factory(self, id, bp=0):
        """ 
        Add known symbols to symbol table(sym). 
        Parser does not recognize symbols if it is not in the table
        """
        try:
            s = self.sym[id] # if already in table don't do anything. Memoized
        except KeyError as e:

            class s(BaseSymbol): 
                # create appropriate symbol class at run time
                pass

            s.__name__ = "sym(" + id + ")"
            s.id = id
            s.lbp = bp
            s.parent = self
            self.sym[id] = s
        else:
            s.lbp = max(bp, s.lbp)
        return s # NOTE: This function does not returns an object. It returns the class

    def expression(self, rbp=0):
        """ 
        Heart of the parsing algorithm -> TDOP 
        
        Explaining this function here is not feasible.
        Check README.md for links to the tutorials

        At the most basic level this function handles the precedence
        of tokens and parses them from highest to lowest   
        """
        t = self.token
        self.token = next(self.token_gen)
        left = t.nud()
        while rbp < self.token.lbp:
            t = self.token
            self.token = next(self.token_gen)
            left = t.led(left)
        return left

    def func_tree_generate(self, name, args, body):
        self.func_tree[name] = {"args": args, "body": body}

    def _advance(self, idlist=None):
        """
        Get the next token 
        """
        if self.token.id == "END":
            return
        if idlist and self.token.id in idlist:
            self.token = next(self.token_gen)
        elif not idlist:
            self.token = next(self.token_gen)
        else:
            raise ParseError(
                """Expected one of %s found %r instead. (line: %i)"""
                % (" ".join(idlist), self.token.id, self.line)
            )

    def Block(self): 
        """
        for parsing inside of a statement.
        every statement begins with indentation.
        like python
        """
        self._advance(["INDENT"])
        stmts = self.Statements()
        self._advance(["DEDENT"])
        return stmts

    def Statements(self):
        """ Parse all statements """
        statements = []
        while True:
            if self.token.id in ["END", "DEDENT"]:
                break
            s = self.Statement()
            if s:
                statements.append(s)
        return statements

    def Statement(self):
        """ Parse a single statement """
        t = self.token
        if t.stmt_begin:
            self._advance()
            return t.std()
        ex = self.expression(0)
        self._advance(["NEWLINE", "END", "DEDENT"])
        return ex

    def _generate_symbols(self):
        """
        Used for generation of required symbols.
        Like operators, contants, anything.
        adds them to symbol table
        """

        def infix(id, bp):
            def led(self, left):
                self.first = left
                self.second = self.parent.expression(bp)
                return self

            self.symbol_factory(id, bp).led = led

        def prefix(id, bp):
            def nud(self):
                self.first = self.parent.expression(bp)
                return self

            self.symbol_factory(id, bp).nud = nud

        def infixr(id, bp):
            def led(self, left):
                self.first = left
                self.second = self.parent.expression(bp - 1)
                return self

            self.symbol_factory(id, bp).led = led

        def paren(id):
            def nud(self):
                expr = self.parent.expression()
                self.parent._advance("RIGHT_PAREN")
                return expr

            self.symbol_factory(id).nud = nud

        paren("LEFT_PAREN")
        self.symbol_factory("RIGHT_PAREN")
        self.symbol_factory("END")
        self.symbol_factory(":")
        self.symbol_factory("NEWLINE")
        self.symbol_factory("INDENT")
        self.symbol_factory("DEDENT")

        # numbers denote order of operations
        infix("+", 10)
        infix("-", 10)
        infix("*", 20)
        infix("/", 20)
        infix("==", 5)
        infix(">", 5)
        infix("<", 5)
        infix("&", 4)
        infix("|", 3)
        infix(",", 1)
        infix("::", 1)
        
        infixr("=", 1) # assignment is a little different from others.

        # example +4 , -2  
        prefix("+", 100)
        prefix("-", 100)

        def literal(id):
            self.symbol_factory(id).nud = lambda self: self

        for l in ["NUMBER", "FLOAT", "NAME", "STRING", "BOOL"]:
            literal(l)

        def statement(id, std):
            self.symbol_factory(id).stmt_begin = True
            self.symbol_factory(id).std = std

        def if_statement(self):
            self.first = self.parent.expression()
            self.parent._advance([":"])
            self.parent._advance(["NEWLINE"])
            self.second = self.parent.Block()
            if self.parent.token.id == "else":
                self.parent._advance(["else"])
                self.parent._advance([":"])
                self.parent._advance(["NEWLINE"])
                self.third = self.parent.Block()
            return self

        def let_statement(self):
            self.first = self.parent.expression()
            self.parent._advance(["NEWLINE"])
            return self

        def print_statement(self):
            self.parent._advance(["LEFT_PAREN"])
            self.first = self.parent.expression()
            self.parent._advance(["RIGHT_PAREN"])
            self.parent._advance(["NEWLINE"])
            return self

        def while_statement(self):
            self.parent._advance(["LEFT_PAREN"])
            self.first = self.parent.expression()
            self.parent._advance(["RIGHT_PAREN"])
            self.parent._advance([":"])
            self.parent._advance(["NEWLINE"])
            self.second = self.parent.Block()
            return self

        def func_statement(self):
            arg_list = []

            self.first = self.parent.expression()
            self.parent._advance(["LEFT_PAREN"])
            self.second = self.parent.expression()
            self.parent._advance(["RIGHT_PAREN"])
            self.parent._advance([":"])
            self.parent._advance(["NEWLINE"])
            self.third = self.parent.Block()
            return self

        statement("if", if_statement)
        statement("let", let_statement)
        statement("print", print_statement)
        statement("while", while_statement)
        statement("fn", func_statement)

    def tokenize(self, program):
        tokenq = Queue()
        lex = Lexer(program, tokenq)
        lex.start()
        while True:
            ttype, line, tvalue = tokenq.get()
            self.line = line
            if ttype == "NUMBER":
                symbol = self.sym["NUMBER"]
                s = symbol()
                s.value = int(tvalue)
                yield s
            elif ttype == "STRING":
                symbol = self.sym["STRING"]
                s = symbol()
                s.value = tvalue[1 : len(tvalue) - 1]
                yield s
            elif ttype in lex.operators:
                symbol = self.sym[tvalue]
                s = symbol()
                yield s
            elif ttype == "KEYWORD":
                symbol = self.sym[tvalue]
                s = symbol()
                yield s
            elif ttype == "BOOL":
                symbol = self.sym["BOOL"]
                s = symbol()
                s.value = True if tvalue == "True" else False
                yield s
            elif ttype == "NAME":
                symbol = self.sym[ttype]
                s = symbol()
                s.value = tvalue
                yield s
            elif ttype == "END":
                symbol = self.sym["END"]
                s = symbol()
                yield s
            elif ttype in ["LEFT_PAREN", "RIGHT_PAREN", "NEWLINE", "INDENT", "DEDENT"]:
                symbol = self.sym[ttype]
                s = symbol()
                yield s
            else:
                raise SyntaxError("unknown operator {}, {}".format(ttype, tvalue))

    def parse(self):
        return self.Statements()

# FOR TESTING PURPOSES. PRINTS SYNTAX TREE
if __name__ == "__main__":

    def source_read():
        if len(sys.argv) > 1:
            with open(sys.argv[1]) as ff:
                data = ff.read()
                return data
        else:
            sys.exit()

    parser = Parser(source_read())
    print(parser.parse())
