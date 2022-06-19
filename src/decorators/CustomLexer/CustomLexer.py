from src.lexer import LALexer
from re import match
from antlr4.error.Errors import LexerNoViableAltException

class CustomLexer(LALexer):
    def notifyListeners(self, e: LexerNoViableAltException):
        start = self._tokenStartCharIndex
        stop = self._input.index
        text = self._input.getText(start, stop)
        # Mensagem para símbolo não identificado
        msg = self.getErrorDisplay(text) + " - simbolo nao identificado"
        # Mensagem comentários não fechados
        if match(r'{[^}]+', self.getErrorDisplay(text)):
            msg = "comentario nao fechado"
        # Mensagem para cadeias não fechadas
        elif match(r'"[^"]+', self.getErrorDisplay(text)):
            msg = "cadeia literal nao fechada"
        listener = self.getErrorListenerDispatch()
        listener.syntaxError(self, None, self._tokenStartLine, self._tokenStartColumn, msg, e)