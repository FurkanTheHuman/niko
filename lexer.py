from threading import Thread
from string import ascii_letters, digits
from queue import Queue


class Lexer(Thread):
    def __init__(self, source, que, name="No Name"):
        super().__init__()
        self._source = source
        self._que = que
        self._start = 0
        self._pos = 0
        self.name = name
        self._line = 1
        self.keywords = ("if", "else", "while", "for", "fn", "print", "let")
        self._opertors = [
            "+",
            "-",
            "*",
            "/",
            "=",
            ":",
            "==",
            "<",
            ">",
            "|",
            "&",
            ",",
            "::",
        ]
        self.operators = self._opertors
        self.indentlevels = [0]

    def run(self):
        state = self._lex_initial
        while True:
            try:
                state = state()
            except Consumed:
                self._cleanup()
                break
            except LexException as e:
                print(e)
                self._add("END")
                break

    def _add(self, token_type, value=None):
        self._que.put((token_type, self._line, self._source[self._start : self._pos]))
        self._start = self._pos

    def _lex_initial(self):
        while True:
            current = self._current_char()
            if current in ascii_letters:
                return self._lex_name
            elif current in digits:
                return self._lex_number
            elif current == '"':
                self._pos += 1
                return self._lex_string
            elif current in self._opertors:
                self._pos += 1
                if self._current_char() == "*" and current == "*":
                    self._pos += 1
                    self._add("**")
                elif self._current_char() == "/" and current == "/":
                    self._pos += 1
                    self._add("//")
                elif self._current_char() == "=" and current == "=":
                    self._pos += 1
                    self._add("==")
                elif self._current_char() == ":" and current == ":":
                    self._pos += 1
                    self._add("::")

                else:
                    self._add(current)
            elif current in " \t":
                self._pos += 1
                self._start = self._pos
            elif current == "\n":
                self._line += 1
                self._pos += 1
                self._start = self._pos
                self._add("NEWLINE")
                return self._lex_indent
            elif current == "(":
                self._pos += 1
                self._add("LEFT_PAREN")
                self._start = self._pos
            elif current == ")":
                self._pos += 1
                self._add("RIGHT_PAREN")
                self._start = self._pos
            elif current == "#":
                self._pos += 1
                while True:
                    current = self._current_char()
                    self._pos += 1
                    if current == "\n":
                        self._start = self._pos
                        return self._lex_initial

            else:
                raise LexException("Unknown character at line " + str(self._line))

    def _current_char(self):
        try:
            return self._source[self._pos]
        except IndexError:
            raise Consumed("Input END")

    def _lex_string(self):
        escape = False
        while True:
            try:
                current = self._current_char()
            except Consumed:
                raise LexException("Bizim bi string vardi, o nooldu?")
            self._pos += 1
            if escape:
                escape = False
                continue

            if current == "\\":
                escape = True

            elif current == '"':
                self._add("STRING")
                return self._lex_initial()

            elif current == "\n":
                self._line += 1
                self._pos += 1
                self._start = self._pos

    def _lex_number(self):
        while True:
            try:
                current = self._current_char()
            except Consumed:
                self._add("NUMBER")
                raise
            if current in digits:
                self._pos += 1
            elif current == ".":
                self._pos += 1
                return self._lex_float()
            else:
                if (
                    current != " "
                    and current not in self._opertors
                    and current != "("
                    and current != ")"
                    and current != "\n"
                ):
                    raise LexException(
                        f"Integer error at line {self._line } (( {current} ))"
                    )
                else:
                    self._add("NUMBER")
                    # self._pos += 1
                    return self._lex_initial

    def _lex_float(self):
        while True:
            try:
                current = self._current_char()
            except Consumed:
                self._add("FLOAT")
                raise
            if current in digits:
                self._pos += 1
            else:
                if (
                    current != " "
                    and current not in self._opertors
                    and current != "("
                    and current != ")"
                    and current != "\n"
                ):
                    raise LexException(f"Float error at line {self._line }")
                else:
                    self._add("FLOAT")
                    self._pos += 1
                    return self._lex_initial

    def _lex_name(self):
        def add_keyword_or_name():
            token = self._source[self._start : self._pos]
            if token in self.keywords:
                return self._add("KEYWORD")
            elif token in ["True", "False"]:
                return self._add("BOOL")
            else:
                return self._add("NAME")

        while True:
            try:
                current = self._current_char()
            except Consumed:
                add_keyword_or_name()
                raise
            if current in ascii_letters:
                self._pos += 1
            else:
                add_keyword_or_name()
                return self._lex_initial

    def _lex_indent(self):
        current_indent = 0
        while True:
            current = self._current_char()
            if current == " ":
                self._pos += 1
                current_indent += 1
            elif current == "\t":
                self._pos += 1
                current_indent += 4
            elif current == "\n":
                self._pos += 1
                current_indent = 0
            else:
                if current_indent < self.indentlevels[-1]:
                    if current_indent in self.indentlevels:
                        while True:
                            if current_indent < self.indentlevels[-1]:
                                self._add("DEDENT")
                                self.indentlevels.pop()
                            else:
                                return self._lex_initial
                    else:
                        raise LexException(
                            "Congratz! Your indentation is all messed up!"
                        )
                elif current_indent > self.indentlevels[-1]:
                    self._add("INDENT")
                    self.indentlevels.append(current_indent)
                    return self._lex_initial
                else:
                    # yeni tokeni indentten sonra başlat
                    self._start = self._pos
                    return self._lex_initial

    def _cleanup(self):
        current_indentation = self.indentlevels.pop()
        while current_indentation != 0:
            self._add("DEDENT")
            current_indentation = self.indentlevels.pop()
        self._add("END")


class Consumed(Exception):
    pass


class LexException(Exception):
    pass


if __name__ == "__main__":
    import sys

    def source_read():
        if len(sys.argv) > 1:
            with open(sys.argv[1]) as ff:
                data = ff.read()
                return data
        else:
            sys.exit()

    q = Queue()
    ll = Lexer(source_read(), q)
    ll.start()
    while True:
        ttype, line, tvalue = q.get()
        print(ttype, line, tvalue)
        if ttype == "END":
            break
