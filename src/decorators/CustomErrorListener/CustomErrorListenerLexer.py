from io import TextIOWrapper
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import Token, Lexer, Parser
from re import match

from src.decorators import CustomLexer

class CustomErrorListenerLexer(ErrorListener):
    def __init__(self, file: TextIOWrapper):
        super().__init__()
        self._file = file
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """ Erro léxico """
        start = recognizer._tokenStartCharIndex
        stop = recognizer._input.index
        text = recognizer._input.getText(start, stop)
        text = recognizer.getErrorDisplay(text)
        # Mensagem para símbolo não identificado
        msg = text + " - simbolo nao identificado"
        # Mensagem comentários não fechados
        if match(r'{[^}]+', text):
            msg = "comentario nao fechado"
        # Mensagem para cadeias não fechadas
        elif match(r'"[^"]+', text):
            msg = "cadeia literal nao fechada"

        self._file.write("Linha " + str(line) + ": " + msg + "\n")

        raise Exception()