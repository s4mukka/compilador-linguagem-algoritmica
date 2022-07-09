from io import TextIOWrapper
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token
from re import match

class CustomErrorListener(ErrorListener):
    def __init__(self, file: TextIOWrapper):
        super().__init__()
        self._file = file
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        token: Token = offendingSymbol

        # Caso não seja erro léxico
        if token is not None:
            text = token.text
            if token.EOF == token.type:
                text = 'EOF'
            msg = f"erro sintatico proximo a {text}"

        self._file.write("Linha " + str(line) + ": " + msg + "\n")
        self._file.write("Fim da compilacao\n")

        raise Exception()