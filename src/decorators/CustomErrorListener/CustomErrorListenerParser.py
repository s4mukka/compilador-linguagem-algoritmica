from io import TextIOWrapper
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token, Lexer, Parser
from re import match

from src.decorators import CustomLexer

class CustomErrorListenerParser(ErrorListener):
    def __init__(self, file: TextIOWrapper):
        super().__init__()
        self._file = file
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """ Erro sintático """
        token: Token = offendingSymbol
        text = token.text
        if token.EOF == token.type:
            text = 'EOF'
        msg = f"erro sintatico proximo a {text}"

        self._file.write("Linha " + str(line) + ": " + msg + "\n")

        raise Exception()