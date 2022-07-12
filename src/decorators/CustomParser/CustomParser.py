from src.lexer import LAParser

class CustomParser(LAParser):
    def handle(self):
        """ Executa o analisador sintático """
        try:
            self.programa()
        finally:
            self._output.write("Fim da compilacao\n")
