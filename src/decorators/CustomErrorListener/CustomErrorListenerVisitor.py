from io import TextIOWrapper
from antlr4.error.ErrorListener import ErrorListener

class CustomErrorListenerVisitor(ErrorListener):
    def __init__(self, file: TextIOWrapper):
        super().__init__()
        self._file = file

    def syntaxError(self, recognizer = None, offendingSymbol = None, line = None, column = None, msg = None, e = None):
        """ Erro semantico """

        text = ""
        if e == "undeclared_type":
            text = f"tipo {msg} nao declarado"
        elif e == "undeclared_identifier":
            text = f"identificador {msg} nao declarado"
        elif e == "alread_declared_identifier":
            text = f"identificador {msg} ja declarado anteriormente"
        elif e == "attribution_not_compatible":
            text = f"atribuicao nao compativel para {msg}"
        elif e == "parameter_mismatch":
            text = f"incompatibilidade de parametros na chamada de {msg}"
        elif e == "return_not_allowed":
            text = "comando retorne nao permitido nesse escopo"

        self._file.write("Linha " + str(line) + ": " + text + "\n")
